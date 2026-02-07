import asyncio
import discord
from pathlib import Path
from typing import AsyncIterator

from .config import load_config
from .exceptions import ConfigurationError
from .message import SmartMessage
from .logger import get_logger

logger = get_logger(__name__)


class BridgeClient(discord.Client):
    """Custom Discord client that bridges to the Bridge class."""

    def __init__(self, bridge: "Bridge", *args, **kwargs):
        self._bridge = bridge
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        """Called when the bot is ready."""
        await self._bridge._handle_on_ready()

    async def on_message(self, message: discord.Message):
        """Called when a message is received."""
        await self._bridge._handle_on_message(message)


class Bridge:
    """Main bridge class for connecting to Discord and handling messages.

    This class provides a simplified interface for receiving and sending
    Discord messages without dealing with low-level Discord API details.

    Example:
        >>> bridge = Bridge(config_path="config.yaml")
        >>> await bridge.run()
        >>> await bridge.wait_for_ready()
        >>> async for message in bridge.listen():
        ...     await message.reply(f"You said: {message.content}")
    """

    def __init__(self, config_path: str) -> None:
        """Initialize the Bridge with configuration.

        Args:
            config_path: Path to the YAML configuration file

        Raises:
            ConfigurationError: If config file is not found or invalid
        """
        self.config_path = config_path

        # Load configuration
        try:
            config_result = load_config(Path(self.config_path))
            self.token = config_result[0]
            self.prefix = config_result[1]
            self.allowed_channels = config_result[2]
            self.max_reconnect_attempts = config_result[3]
            self.reconnect_base_delay = config_result[4]
            logger.info(f"Configuration loaded from {config_path}")
            logger.info(f"Command prefix set to: '{self.prefix}'")
            if self.allowed_channels:
                logger.info(f"Whitelisted channels: {self.allowed_channels}")
        except FileNotFoundError:
            raise ConfigurationError(f"Config file not found at: {config_path}")

        # Internal state
        self.is_ready: bool = False
        self.bot_user_id: int | None = None
        self._ready_event = asyncio.Event()
        self._incoming_queue: asyncio.Queue[SmartMessage] = asyncio.Queue()
        self._shutdown_event = asyncio.Event()
        self._client: BridgeClient | None = None

        # Setup Discord client
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        self._client = BridgeClient(self, intents=intents)

    async def run(self) -> None:
        """Start the bot and connect to Discord with automatic reconnection.

        This method starts the Discord client and begins listening for
        messages. It will block until the connection is closed.

        If the connection drops, it will automatically attempt to reconnect
        with exponential backoff up to max_reconnect_attempts times.

        Raises:
            ConnectionError: If initial login fails (invalid token)
            ReconnectExhaustedError: If all reconnection attempts are exhausted
        """
        logger.info("Starting Discord bot...")

        try:
            await self._connect_with_retry()
        except discord.LoginFailure:
            logger.error("Failed to log in. Please check your discord_token.")
            raise ConnectionError("Failed to log in. Is the discord_token correct?")

    async def _connect_with_retry(self) -> None:
        """Connect to Discord with automatic retry and exponential backoff.

        Attempts to connect to Discord, and if the connection drops,
        automatically retries with exponential backoff.
        """
        from .exceptions import ReconnectExhaustedError

        attempt = 0

        while True:
            try:
                if attempt > 0:
                    delay = min(
                        self.reconnect_base_delay * (2 ** (attempt - 1)),
                        60.0,  # Cap at 60 seconds
                    )
                    logger.info(
                        f"Reconnection attempt {attempt}/{self.max_reconnect_attempts} in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)

                logger.info("Connecting to Discord...")
                await self._client.start(self.token)

                # If we get here, the client closed normally
                logger.info("Discord client closed normally")
                break

            except discord.LoginFailure:
                # Don't retry on login failure - it's a config issue
                raise
            except Exception as e:
                attempt += 1

                if attempt >= self.max_reconnect_attempts:
                    logger.error(f"Failed to reconnect after {attempt} attempts")
                    raise ReconnectExhaustedError(
                        f"Failed to reconnect after {attempt} attempts: {e}",
                        attempts=attempt,
                        last_error=e,
                    ) from e

                logger.warning(f"Connection lost: {e}. Will retry...")

    async def stop(self) -> None:
        """Gracefully stop the bot and disconnect from Discord.

        This method will:
        1. Set the shutdown flag to stop accepting new messages
        2. Wait for pending messages in the queue to be processed
        3. Close the Discord client connection

        Example:
            >>> # In your application
            >>> try:
            ...     async for message in bridge.listen():
            ...         await process_message(message)
            ... except asyncio.CancelledError:
            ...     await bridge.stop()
        """
        logger.info("Initiating graceful shutdown...")
        self._shutdown_event.set()

        # Wait for queue to drain (with timeout)
        logger.debug("Waiting for message queue to drain...")
        try:
            await asyncio.wait_for(self._drain_queue(), timeout=30.0)
        except asyncio.TimeoutError:
            logger.warning("Queue drain timed out, forcing shutdown")

        # Close Discord connection
        if self._client:
            logger.info("Closing Discord connection...")
            await self._client.close()
            logger.info("Discord connection closed")

        logger.info("Bridge shutdown complete")

    async def _drain_queue(self) -> None:
        """Wait for the incoming message queue to be empty."""
        while not self._incoming_queue.empty():
            await asyncio.sleep(0.1)

    async def wait_for_ready(self) -> None:
        """Wait until the bot is connected and ready to receive messages.

        This method blocks until the bot has successfully connected to
        Discord and is ready to process messages.
        """
        logger.debug("Waiting for bot to be ready...")
        await self._ready_event.wait()
        logger.info("Bot is ready!")

    async def listen(self) -> AsyncIterator[SmartMessage]:
        """Async iterator that yields messages received from Discord.

        This is the main interface for receiving messages. Use it in an
        async for loop to process incoming commands.

        Yields:
            SmartMessage: A wrapped message object with convenient reply method

        Example:
            >>> async for message in bridge.listen():
            ...     print(f"Received: {message.content}")
            ...     await message.reply("Got it!")
        """
        while not self._shutdown_event.is_set():
            try:
                # Wait for message with timeout to check shutdown periodically
                message = await asyncio.wait_for(self._incoming_queue.get(), timeout=1.0)
                yield message
            except asyncio.TimeoutError:
                # Check shutdown flag and continue
                continue

    async def _handle_on_ready(self) -> None:
        """Handle the event when the bot successfully connects."""
        self.bot_user_id = self._client.user.id
        self.is_ready = True
        self._ready_event.set()
        logger.info(f"Bridge is ready. Logged in as {self._client.user}")

    async def _handle_on_message(self, message: discord.Message) -> None:
        """Handle incoming Discord messages and filter them.

        This method filters messages based on:
        1. Bot readiness state
        2. Message author (ignores bot's own messages)
        3. Command prefix
        4. Channel whitelist (if configured)

        Args:
            message: The raw Discord message object
        """
        if not self.is_ready:
            return

        # 1. Ignore messages from the bot itself
        if message.author.id == self.bot_user_id:
            return

        # 2. Ignore messages that don't start with the prefix
        if not message.content.startswith(self.prefix):
            return

        # 3. Check channel whitelist if configured
        if self.allowed_channels and message.channel.id not in self.allowed_channels:
            logger.debug(f"Ignoring message from non-whitelisted channel: {message.channel.id}")
            return

        # If filters pass, create a SmartMessage and put it in the queue
        smart_msg = SmartMessage(message, self.prefix)
        logger.debug(f"Received command from {message.author.id}: {smart_msg.content}")
        await self._incoming_queue.put(smart_msg)
