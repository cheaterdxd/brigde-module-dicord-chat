import asyncio
import discord
from pathlib import Path

from .config import load_config
from .exceptions import ConfigurationError
from .message import SmartMessage

class Bridge:
    def __init__(self, config_path: str):
        self.config_path = config_path
        
        # Load configuration
        try:
            self.token, self.prefix = load_config(Path(self.config_path))
        except FileNotFoundError:
            raise ConfigurationError(f"Config file not found at: {config_path}")

        # Internal state
        self.is_ready = False
        self.bot_user_id = None
        self._ready_event = asyncio.Event()
        self._incoming_queue = asyncio.Queue()
        
        # Setup Discord client and event handlers
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        self._client = discord.Client(intents=intents)
        self._client.event(self._handle_on_ready)
        self._client.event(self._handle_on_message)

    async def run(self):
        """Starts the bot and connects to Discord."""
        try:
            await self._client.start(self.token)
        except discord.LoginFailure:
            raise ConnectionError("Failed to log in. Is the discord_token correct?")

    async def wait_for_ready(self):
        """Waits until the bot is connected and ready to receive messages."""
        await self._ready_event.wait()

    async def listen(self):
        """Async iterator that yields messages received from Discord."""
        while True:
            message = await self._incoming_queue.get()
            yield message

    async def _handle_on_ready(self):
        """Handles the event when the bot successfully connects."""
        self.bot_user_id = self._client.user.id
        self.is_ready = True
        self._ready_event.set()
        print(f"Bridge is ready. Logged in as {self._client.user}")

    async def _handle_on_message(self, message: discord.Message):
        """Handles all incoming messages and filters them."""
        if not self.is_ready:
            return

        # 1. Ignore messages from the bot itself
        if message.author.id == self.bot_user_id:
            return

        # 2. Ignore messages that don't start with the prefix
        if not message.content.startswith(self.prefix):
            return

        # If filters pass, create a SmartMessage and put it in the queue
        smart_msg = SmartMessage(message, self.prefix)
        await self._incoming_queue.put(smart_msg)