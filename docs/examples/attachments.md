# Attachments Example

A complete example demonstrating file uploads and attachments with Discord Bridge.

## Code

```python
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

    @router.command("textfile")
    async def textfile_handler(message, args):
        """Send a sample text file."""
        content = f"Hello {message.author_name}!\n\nThis is a sample text file.\nGenerated at: {asyncio.get_event_loop().time()}"
        filepath = await create_sample_file(content, f"hello_{message.author_id}.txt")
        
        try:
            await message.reply_with_file(
                content="Here's your personalized text file!",
                file_path=filepath
            )
            logger.info(f"Sent text file to {message.author_name}")
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    @router.command("log")
    async def log_handler(message, args):
        """Send a log file."""
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

    @router.command("data")
    async def data_handler(message, args):
        """Send sample data as CSV."""
        csv_content = """id,name,value
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
```

## What This Example Demonstrates

1. **File Upload**: Sending text files with messages
2. **Custom Filenames**: Renaming files for the recipient
3. **Temporary Files**: Creating and cleaning up temp files
4. **Error Handling**: Using try/finally to ensure cleanup
5. **Personalized Content**: Including user info in files

## Available Commands

| Command | Description | File Type |
|---------|-------------|-----------|
| `!textfile` | Sends personalized text file | .txt |
| `!log` | Sends activity log | .log |
| `!data` | Sends CSV data export | .csv |

## Key Concepts

### Basic File Upload

```python
await message.reply_with_file(
    content="Here's your file!",
    file_path="/path/to/file.txt"
)
```

### Custom Filename

```python
await message.reply_with_file(
    content="Report ready",
    file_path="/tmp/temp_12345.pdf",
    filename="monthly_report.pdf"  # User sees this name
)
```

### Temporary Files (Best Practice)

```python
import tempfile
import os

# Create temp file
fd, temp_path = tempfile.mkstemp(suffix='.txt')
try:
    with os.fdopen(fd, 'w') as f:
        f.write("Content")
    
    # Send file
    await message.reply_with_file(
        file_path=temp_path,
        filename="report.txt"
    )
finally:
    # Always clean up
    os.unlink(temp_path)
```

## File Size Limits

Discord has limits:
- Regular: 8 MB
- With Nitro: 50 MB

```python
MAX_SIZE = 8 * 1024 * 1024  # 8 MB

if os.path.getsize(filepath) > MAX_SIZE:
    await message.reply("File too large!")
else:
    await message.reply_with_file(file_path=filepath)
```

## Running the Example

```bash
python examples/attachments.py
```

## Testing Commands

1. `!textfile` - Creates and sends personalized text file
2. `!log` - Generates activity log with user info
3. `!data` - Exports sample CSV data

## Security Best Practices

1. **Never send secrets**: Don't upload config files or databases
2. **Validate paths**: Prevent directory traversal
3. **Clean up**: Always delete temp files
4. **Check permissions**: Ensure bot can read files
5. **Rate limit**: Prevent abuse

## Common Use Cases

### Reports
```python
# Generate PDF report
report_path = generate_pdf_report(user_id)
await message.reply_with_file(
    content="Your report is ready",
    file_path=report_path,
    filename="report.pdf"
)
```

### Data Export
```python
# Export user data
csv_data = export_user_data(user_id)
with open(temp_file, 'w') as f:
    f.write(csv_data)
await message.reply_with_file(file_path=temp_file)
```

### Images
```python
# Send generated image
await message.reply_with_file(
    content="Here's your image",
    file_path="/path/to/generated.png"
)
```
