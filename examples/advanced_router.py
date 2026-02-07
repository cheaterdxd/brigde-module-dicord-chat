"""Example: Using the Command Router for structured command handling."""
import asyncio
import os
import shutil
import logging
from datetime import datetime

from discord_bridge import Bridge, ConfigurationError, setup_logging, CommandRouter


async def main():
    # Setup logging
    logger = setup_logging(level=logging.INFO)
    
    # Create config if needed
    if not os.path.exists("config.yaml"):
        shutil.copy("config.yaml.example", "config.yaml")
        logger.warning("Please configure config.yaml with your Discord token")
        return

    # Initialize bridge
    try:
        bridge = Bridge(config_path="config.yaml")
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return

    # Create command router
    router = CommandRouter()

    # Register commands using decorators
    @router.command("hello", description="Say hello to the bot")
    async def hello_handler(message, args):
        """Handle !hello command."""
        await message.reply(f"Hello, {message.author_name}! ")

    @router.command("time", description="Get the current time")
    async def time_handler(message, args):
        """Handle !time command."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(f"Current time: {current_time}")

    @router.command("echo", description="Echo back your message", usage="<message>")
    async def echo_handler(message, args):
        """Handle !echo command."""
        if args:
            await message.reply(f"You said: {args}")
        else:
            await message.reply("Please provide a message to echo. Usage: !echo <message>")

    @router.command("dm", description="Check if this is a DM")
    async def dm_handler(message, args):
        """Handle !dm command."""
        if message.is_dm:
            await message.reply("This is a direct message!")
        else:
            await message.reply(f"This is a channel message (Channel ID: {message.channel_id})")

    @router.command("info", description="Get information about yourself")
    async def info_handler(message, args):
        """Handle !info command."""
        info = f"**Your Info:**\n"
        info += f"Name: {message.author_name}\n"
        info += f"ID: {message.author_id}\n"
        info += f"Channel: {message.channel_id}\n"
        info += f"Is DM: {message.is_dm}"
        await message.reply(info)

    @router.default
    async def unknown_handler(message, args):
        """Handle unknown commands."""
        await message.reply(
            f"Unknown command: `{message.content.split()[0]}`\n"
            f"Type `!help` to see available commands."
        )

    # Start the bot
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    logger.info("Bot ready! Commands registered: " + ", ".join(router.get_commands().keys()))

    # Main loop - use the router to handle messages
    try:
        async for message in bridge.listen():
            handled = await router.handle(message)
            if not handled:
                logger.warning(f"Unhandled message: {message.content}")
    except asyncio.CancelledError:
        logger.info("Shutting down...")
        await bridge.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
