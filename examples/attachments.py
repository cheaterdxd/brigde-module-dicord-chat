"""Example: Sending file attachments."""
import asyncio
import os
import shutil
import logging
import tempfile

from discord_bridge import Bridge, ConfigurationError, setup_logging, CommandRouter


async def create_sample_file(content: str, filename: str) -> str:
    """Create a temporary file with sample content."""
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


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

    @router.command("textfile", description="Send a sample text file")
    async def textfile_handler(message, args):
        """Send a text file attachment."""
        content = f"Hello {message.author_name}!\n\nThis is a sample text file.\nGenerated at: {asyncio.get_event_loop().time()}"
        filepath = await create_sample_file(content, f"hello_{message.author_id}.txt")
        
        try:
            await message.reply_with_file(
                content="Here's your personalized text file!",
                file_path=filepath
            )
            logger.info(f"Sent text file to {message.author_name}")
        finally:
            # Clean up temp file
            if os.path.exists(filepath):
                os.remove(filepath)

    @router.command("log", description="Generate a sample log file")
    async def log_handler(message, args):
        """Send a log file attachment."""
        log_content = f"""Bot Log - User Request
========================
Timestamp: {asyncio.get_event_loop().time()}
User: {message.author_name}
User ID: {message.author_id}
Channel ID: {message.channel_id}
Is DM: {message.is_dm}

Processing complete!
"""
        filepath = await create_sample_file(log_content, f"log_{message.author_id}.log")
        
        try:
            await message.reply_with_file(
                content="Here's your activity log:",
                file_path=filepath,
                filename="activity.log"
            )
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    @router.command("data", description="Send sample data as CSV")
    async def data_handler(message, args):
        """Send a CSV file."""
        csv_content = """Name,Value,Timestamp
Command,data_request,{time}
User,{author},{time}
Status,success,{time}
""".format(
            author=message.author_name,
            time=asyncio.get_event_loop().time()
        )
        
        filepath = await create_sample_file(csv_content, f"data_{message.author_id}.csv")
        
        try:
            await message.reply_with_file(
                content="Here's your data export:",
                file_path=filepath,
                filename="data_export.csv"
            )
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    # Start bot
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    logger.info("Attachment example bot ready!")

    try:
        async for message in bridge.listen():
            await router.handle(message)
    except asyncio.CancelledError:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
