"""Example: Handling direct messages (DMs) differently from channel messages."""
import asyncio
import os
import shutil
import logging

from discord_bridge import Bridge, ConfigurationError, setup_logging, CommandRouter


async def main():
    logger = setup_logging(level=logging.INFO)
    
    if not os.path.exists("config.yaml"):
        shutil.copy("config.yaml.example", "config.yaml")
        logger.warning("Please configure config.yaml")
        return

    try:
        bridge = Bridge(config_path="config.yaml")
    except ConfigurationError as e:
        logger.error(f"Config error: {e}")
        return

    router = CommandRouter()

    @router.command("hello", description="Say hello")
    async def hello_handler(message, args):
        """Handle hello differently in DMs vs channels."""
        if message.is_dm:
            # More personal greeting in DMs
            await message.reply(
                f"Hey {message.author_name}! Thanks for messaging me privately. "
                f"Feel free to ask me anything here!"
            )
        else:
            # Standard greeting in channels
            await message.reply(f"Hello {message.author_name}! ")

    @router.command("support", description="Get support information")
    async def support_handler(message, args):
        """Provide support info, encouraging DMs for private matters."""
        if message.is_dm:
            await message.reply(
                "Thanks for reaching out privately!\n\n"
                "For support, please describe your issue and I'll help you right away.\n"
                "Your message is confidential in this DM."
            )
        else:
            await message.reply(
                f"Hi {message.author_name}! For private support matters, "
                f"please DM me directly. I'm happy to help!"
            )

    @router.command("secret", description="Get a secret message")
    async def secret_handler(message, args):
        """Only works in DMs."""
        if message.is_dm:
            await message.reply(
                "Here's your secret: The bot was built with discord_bridge! "
            )
        else:
            await message.reply(
                "This command only works in direct messages! "
                "Please DM me to get your secret."
            )

    @router.command("channel", description="Get channel information")
    async def channel_handler(message, args):
        """Show channel/DM info."""
        if message.is_dm:
            await message.reply(
                "You're currently in a **Direct Message** with me.\n"
                f"Your User ID: {message.author_id}\n"
                "This is a private conversation!"
            )
        else:
            await message.reply(
                f"You're in a **Server Channel** (ID: {message.channel_id})\n"
                f"Your User ID: {message.author_id}\n"
                "Other users in this channel can see our conversation."
            )

    @router.command("broadcast", description="[Channel only] Broadcast a message")
    async def broadcast_handler(message, args):
        """Only works in channels."""
        if message.is_dm:
            await message.reply(
                "Broadcasting only works in server channels, not in DMs!"
            )
            return
        
        if not args:
            await message.reply("Usage: !broadcast <message>")
            return
        
        await message.reply(f" Broadcasting: {args}")

    # Log all incoming messages to show DM vs Channel distinction
    async def message_logger(message):
        """Log whether message is DM or channel."""
        msg_type = "DM" if message.is_dm else "Channel"
        logger.info(f"[{msg_type}] {message.author_name}: {message.content}")
        return True

    # Start bot
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    logger.info("DM handler bot ready!")

    try:
        async for message in bridge.listen():
            # Log message type
            await message_logger(message)
            # Handle command
            await router.handle(message)
    except asyncio.CancelledError:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
