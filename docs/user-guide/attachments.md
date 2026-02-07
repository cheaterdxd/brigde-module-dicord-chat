# File Attachments

Learn how to send files with your Discord messages.

## Basic File Upload

```python
await message.reply_with_file(
    content="Here's your file!",
    file_path="/path/to/document.pdf"
)
```

## Upload with Custom Filename

```python
await message.reply_with_file(
    content="Your report is ready",
    file_path="/tmp/generated_report_12345.pdf",
    filename="monthly_report.pdf"  # User sees this name
)
```

## Common Use Cases

### Generated Reports

```python
import tempfile
import os

@router.command("report")
async def generate_report(message, args):
    # Generate report content
    report_content = f"""Report for {message.author_name}
Generated: {datetime.now()}
User ID: {message.author_id}
    
Data: ...
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(report_content)
        temp_path = f.name
    
    try:
        # Send file
        await message.reply_with_file(
            content="Here's your personalized report",
            file_path=temp_path,
            filename=f"report_{message.author_id}.txt"
        )
    finally:
        # Clean up
        os.unlink(temp_path)
```

### Image Upload

```python
@router.command("screenshot")
async def send_screenshot(message, args):
    await message.reply_with_file(
        content="Here's the screenshot you requested",
        file_path="/path/to/screenshot.png",
        filename="screenshot.png"
    )
```

### CSV Data Export

```python
import csv
import tempfile

@router.command("export")
async def export_data(message, args):
    # Create CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Value', 'Date'])
        writer.writerow(['Item 1', '100', '2024-01-01'])
        writer.writerow(['Item 2', '200', '2024-01-02'])
        temp_path = f.name
    
    try:
        await message.reply_with_file(
            content="Data export complete",
            file_path=temp_path,
            filename="data_export.csv"
        )
    finally:
        os.unlink(temp_path)
```

### Log Files

```python
@router.command("logs")
async def send_logs(message, args):
    log_path = "/var/log/myapp.log"
    
    if os.path.exists(log_path):
        await message.reply_with_file(
            content="Recent log entries",
            file_path=log_path,
            filename="application_logs.txt"
        )
    else:
        await message.reply("Log file not found")
```

## Error Handling

Always handle potential errors:

```python
@router.command("upload")
async def safe_upload(message, args):
    file_path = args.strip() if args else ""
    
    if not file_path:
        await message.reply("Please provide a file path")
        return
    
    try:
        await message.reply_with_file(
            content="File attached",
            file_path=file_path
        )
    except FileNotFoundError:
        await message.reply(f"File not found: {file_path}")
    except PermissionError:
        await message.reply("Permission denied accessing the file")
    except Exception as e:
        await message.reply(f"Error uploading file: {e}")
```

## File Size Limits

Discord has file size limits:
- Regular users: 8 MB
- Nitro users: 50 MB (bots can upload up to this)

Check file size before uploading:

```python
import os

MAX_FILE_SIZE = 8 * 1024 * 1024  # 8 MB

async def safe_file_send(message, file_path):
    size = os.path.getsize(file_path)
    
    if size > MAX_FILE_SIZE:
        await message.reply(f"File too large ({size / 1024 / 1024:.1f} MB). Max: 8 MB")
        return
    
    await message.reply_with_file(
        content="File attached",
        file_path=file_path
    )
```

## Combining with Embeds

Send an embed with a file:

```python
# First send embed
await message.reply_with_embed(
    title="Report Generated",
    description="Your data analysis is complete",
    color=0x00FF00
)

# Then send file
await message.reply_with_file(
    file_path="/path/to/report.pdf",
    filename="analysis_report.pdf"
)
```

## Complete Example

```python
import asyncio
import tempfile
import os
from datetime import datetime
from discord_bridge import Bridge, CommandRouter

router = CommandRouter()

@router.command("textfile")
async def create_text(message, args):
    """Create and send a text file"""
    content = f"""Hello {message.author_name}!

This file was generated just for you.
Generated at: {datetime.now()}
"""
    
    # Create temp file
    fd, temp_path = tempfile.mkstemp(suffix='.txt')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        
        await message.reply_with_file(
            content="Here's your personalized file!",
            file_path=temp_path,
            filename=f"hello_{message.author_name}.txt"
        )
    finally:
        os.unlink(temp_path)

@router.command("data")
async def send_data(message, args):
    """Send sample data file"""
    lines = [
        "id,name,value",
        "1,Alpha,100",
        "2,Beta,200",
        "3,Gamma,300"
    ]
    
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write('\n'.join(lines))
        
        await message.reply_with_file(
            content="Sample data export",
            file_path=temp_path,
            filename="sample_data.csv"
        )
    finally:
        os.unlink(temp_path)

async def main():
    bridge = Bridge(config_path="config.yaml")
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    
    async for message in bridge.listen():
        await router.handle(message)

asyncio.run(main())
```

## Security Considerations

1. **Never send sensitive files**: Don't upload config files, databases, or secrets
2. **Validate file paths**: Prevent directory traversal attacks
3. **Clean up temp files**: Always delete temporary files after sending
4. **Check file sizes**: Prevent abuse with large files
5. **Rate limit uploads**: Prevent spam with file uploads

## Tips

1. **Use temporary files**: Generate files on-demand to save storage
2. **Clean up**: Always delete temp files in `finally` blocks
3. **Custom filenames**: Use descriptive names instead of temp file names
4. **Error messages**: Provide clear feedback when files can't be sent
5. **Combine approaches**: Use embeds for context, files for data
