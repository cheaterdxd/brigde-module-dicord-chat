"""Example: Sending rich embed messages with formatting."""
import asyncio
import os
import shutil
import logging
from datetime import datetime

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

    @router.command("status", description="Show bot status")
    async def status_handler(message, args):
        """Send a status embed."""
        await message.reply_with_embed(
            title="Bot Status",
            description="Everything is running smoothly!",
            color=0x00FF00,  # Green
            fields=[
                {"name": "Uptime", "value": "Online", "inline": True},
                {"name": "Version", "value": "2.0.0", "inline": True},
                {"name": "Commands", "value": str(len(router.get_commands())), "inline": True}
            ],
            footer="Powered by discord_bridge",
            thumbnail_url="https://cdn.discordapp.com/embed/avatars/0.png"
        )

    @router.command("server", description="Show server information")
    async def server_handler(message, args):
        """Send server info embed."""
        await message.reply_with_embed(
            title="Server Information",
            description="This is an example embed with rich formatting",
            color=0x3498DB,  # Blue
            fields=[
                {"name": "Feature 1", "value": "Automatic message splitting", "inline": False},
                {"name": "Feature 2", "value": "Rate limit protection", "inline": False},
                {"name": "Feature 3", "value": "Command routing", "inline": False},
                {"name": "Feature 4", "value": "Rich embeds", "inline": False}
            ],
            footer="discord_bridge - Making Discord bots simple"
        )

    @router.command("error", description="Show error example")
    async def error_handler(message, args):
        """Send an error-style embed."""
        await message.reply_with_embed(
            title="Error Example",
            description="This is what an error embed looks like",
            color=0xFF0000,  # Red
            fields=[
                {"name": "Error Code", "value": "404", "inline": True},
                {"name": "Status", "value": "Not Found", "inline": True}
            ]
        )

    @router.command("colors", description="Show different embed colors")
    async def colors_handler(message, args):
        """Send multiple embeds with different colors."""
        colors = [
            (0xFF0000, "Red", "#FF0000"),
            (0x00FF00, "Green", "#00FF00"),
            (0x0000FF, "Blue", "#0000FF"),
            (0xFFFF00, "Yellow", "#FFFF00"),
            (0xFF00FF, "Magenta", "#FF00FF"),
            (0x00FFFF, "Cyan", "#00FFFF")
        ]
        
        for color, name, hex_code in colors:
            await message.reply_with_embed(
                title=f"{name} Color",
                description=f"Hex code: {hex_code}",
                color=color
            )
            await asyncio.sleep(0.5)  # Small delay between embeds

    # Start bot
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    logger.info("Embed example bot ready!")

    try:
        async for message in bridge.listen():
            await router.handle(message)
    except asyncio.CancelledError:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
