"""Command router for Discord Bridge with decorator-based registration."""

from typing import Callable, Awaitable, Optional
from dataclasses import dataclass

from .message import SmartMessage
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class CommandInfo:
    """Information about a registered command.

    Attributes:
        name: The command name (e.g., "hello")
        handler: The async function that handles the command
        description: Optional description for help text
        usage: Optional usage example
    """

    name: str
    handler: Callable[[SmartMessage, str], Awaitable[None]]
    description: str = ""
    usage: str = ""


class CommandRouter:
    """Router for handling Discord commands with decorator-based registration.

    This class provides a simple way to register command handlers using
    decorators and automatically route incoming messages to the correct handler.

    Example:
        >>> router = CommandRouter()
        >>>
        >>> @router.command("hello")
        >>> async def hello_handler(message, args):
        ...     await message.reply(f"Hello, {message.author_name}!")
        >>>
        >>> @router.command("echo", description="Echo back your message")
        >>> async def echo_handler(message, args):
        ...     await message.reply(args if args else "Nothing to echo")
        >>>
        >>> # In your main loop:
        >>> async for message in bridge.listen():
        ...     await router.handle(message)
    """

    def __init__(self) -> None:
        """Initialize the command router."""
        self._commands: dict[str, CommandInfo] = {}
        self._default_handler: Optional[
            Callable[[SmartMessage, str], Awaitable[None]]
        ] = None
        logger.debug("CommandRouter initialized")

    def command(self, name: str, description: str = "", usage: str = "") -> Callable:
        """Decorator to register a command handler.

        Args:
            name: The command name (without prefix, e.g., "hello" for "!hello")
            description: Description shown in help text
            usage: Usage example shown in help text

        Returns:
            Decorator function

        Example:
            >>> @router.command("hello", description="Say hello")
            >>> async def hello_cmd(message, args):
            ...     await message.reply("Hello!")
        """

        def decorator(
            handler: Callable[[SmartMessage, str], Awaitable[None]],
        ) -> Callable[[SmartMessage, str], Awaitable[None]]:
            self._commands[name.lower()] = CommandInfo(
                name=name.lower(), handler=handler, description=description, usage=usage
            )
            logger.debug(f"Registered command: {name}")
            return handler

        return decorator

    def default(self, handler: Callable[[SmartMessage, str], Awaitable[None]]) -> None:
        """Set a default handler for unrecognized commands.

        Args:
            handler: Async function to handle unknown commands

        Example:
            >>> @router.default
            >>> async def unknown_handler(message, args):
            ...     await message.reply("Unknown command. Type !help for available commands.")
        """
        self._default_handler = handler
        logger.debug("Default handler registered")

    async def handle(self, message: SmartMessage) -> bool:
        """Handle an incoming message by routing to the appropriate command.

        Args:
            message: The SmartMessage to handle

        Returns:
            True if a handler was found and executed, False otherwise

        Example:
            >>> async for message in bridge.listen():
            ...     handled = await router.handle(message)
            ...     if not handled:
            ...         logger.info(f"Unhandled message: {message.content}")
        """
        # Parse command and arguments
        parts = message.content.split(maxsplit=1)
        command = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        logger.debug(f"Handling command: {command} with args: {args[:50]}...")

        # Check for built-in help command
        if command == "help":
            await self._handle_help(message)
            return True

        # Find and execute command handler
        if command in self._commands:
            cmd_info = self._commands[command]
            try:
                await cmd_info.handler(message, args)
                logger.debug(f"Command '{command}' handled successfully")
                return True
            except Exception as e:
                logger.error(f"Error handling command '{command}': {e}")
                await message.reply(f"Error executing command: {e}")
                return True

        # Use default handler if no command matched
        if self._default_handler:
            try:
                await self._default_handler(message, args)
                logger.debug("Default handler executed")
                return True
            except Exception as e:
                logger.error(f"Error in default handler: {e}")
                return False

        logger.debug(f"No handler found for command: {command}")
        return False

    async def _handle_help(self, message: SmartMessage) -> None:
        """Generate and send help text for all registered commands.

        Args:
            message: The message requesting help
        """
        help_lines = ["**Available Commands:**\n"]

        for cmd_name, cmd_info in sorted(self._commands.items()):
            line = f"`!{cmd_name}`"
            if cmd_info.description:
                line += f" - {cmd_info.description}"
            if cmd_info.usage:
                line += f"\n  Usage: `!{cmd_name} {cmd_info.usage}`"
            help_lines.append(line)

        help_text = "\n".join(help_lines)
        await message.reply(help_text)
        logger.debug("Help command executed")

    def get_commands(self) -> dict[str, CommandInfo]:
        """Get a dictionary of all registered commands.

        Returns:
            Dictionary mapping command names to CommandInfo objects
        """
        return self._commands.copy()

    def has_command(self, name: str) -> bool:
        """Check if a command is registered.

        Args:
            name: The command name to check

        Returns:
            True if the command is registered, False otherwise
        """
        return name.lower() in self._commands
