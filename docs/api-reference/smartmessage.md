# SmartMessage

A wrapper around Discord messages with convenient reply functionality.

## Overview

```python
async for message in bridge.listen():
    # message is a SmartMessage instance
    await message.reply("Hello!")
```

## Constructor

### `SmartMessage.__init__(original_message: discord.Message, prefix: str) -> None`

Initialize SmartMessage from a Discord message.

**Parameters:**
- `original_message` (discord.Message): The raw Discord message object
- `prefix` (str): The command prefix to strip from content

**Note:** This is typically called internally by the Bridge class.

## Properties

### `content: str`

The message content without the command prefix.

**Example:**
```python
# User sends: !hello world
async for message in bridge.listen():
    print(message.content)  # "hello world"
```

### `author_id: int`

The Discord ID of the message author.

### `author_name: str`

The display name of the message author.

### `channel_id: int`

The Discord ID of the channel where the message was sent.

### `is_dm: bool`

Whether the message was sent in a DM (direct message).

**Example:**
```python
async for message in bridge.listen():
    if message.is_dm:
        await message.reply("This is a private conversation!")
    else:
        await message.reply("Hello from the channel!")
```

## Methods

### `reply(text: str) -> None`

Send a reply to the channel where the message was received.

Automatically splits messages longer than 2000 characters and adds delays between chunks to respect Discord's rate limits.

**Parameters:**
- `text` (str): The text to send as a reply

**Raises:**
- `MessageSendError`: If the message fails to send

**Example:**
```python
await message.reply("This is my response!")

# Long messages are automatically split
await message.reply("a" * 5000)  # Sends as 3 messages
```

### `reply_with_file(content: str | None = None, file_path: str | None = None, filename: str | None = None) -> None`

Send a reply with an attached file.

**Parameters:**
- `content` (str | None): Optional text content to include with the file
- `file_path` (str | None): Path to the file to upload
- `filename` (str | None): Optional custom filename (uses basename if not provided)

**Raises:**
- `MessageSendError`: If the file fails to send
- `FileNotFoundError`: If the file doesn't exist

**Example:**
```python
await message.reply_with_file(
    content="Here's your file!",
    file_path="/path/to/document.pdf",
    filename="report.pdf"
)
```

### `reply_with_embed(title: str | None = None, description: str | None = None, color: int = 0x3498db, fields: list[dict] | None = None, footer: str | None = None, image_url: str | None = None, thumbnail_url: str | None = None) -> None`

Send a reply with a Discord embed (rich formatting).

**Parameters:**
- `title` (str | None): Embed title
- `description` (str | None): Embed description text
- `color` (int): Integer color code (default: 0x3498db - blue)
- `fields` (list[dict] | None): List of field dicts with 'name', 'value', and optional 'inline' keys
- `footer` (str | None): Footer text
- `image_url` (str | None): URL for main image
- `thumbnail_url` (str | None): URL for thumbnail image

**Raises:**
- `MessageSendError`: If the embed fails to send

**Example:**
```python
await message.reply_with_embed(
    title="My Response",
    description="Here's some information",
    color=0x00FF00,  # Green
    fields=[
        {"name": "Field 1", "value": "Value 1", "inline": True},
        {"name": "Field 2", "value": "Value 2", "inline": True}
    ],
    footer="Powered by discord_bridge"
)
```

## Class Attributes

### `CHUNK_DELAY: float = 1.2`

Delay in seconds between message chunks to respect Discord rate limits.

### `MAX_MESSAGE_LENGTH: int = 2000`

Maximum length of a Discord message before splitting.

## Complete Example

```python
import asyncio
from discord_bridge import Bridge, CommandRouter

router = CommandRouter()

@router.command("info")
async def info_handler(message, args):
    # Use different reply methods based on needs
    
    # Simple text reply
    await message.reply(f"Hello, {message.author_name}!")
    
    # Rich embed
    await message.reply_with_embed(
        title="User Information",
        description=f"Details for {message.author_name}",
        color=0x3498DB,
        fields=[
            {"name": "ID", "value": str(message.author_id), "inline": True},
            {"name": "Channel", "value": str(message.channel_id), "inline": True},
            {"name": "Is DM", "value": str(message.is_dm), "inline": True}
        ]
    )

async def main():
    bridge = Bridge(config_path="config.yaml")
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    
    async for message in bridge.listen():
        await router.handle(message)

asyncio.run(main())
```
