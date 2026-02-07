# Replies & Embeds

Learn how to send text replies and rich embed messages.

## Text Replies

### Basic Reply

```python
async for message in bridge.listen():
    await message.reply("Hello!")
```

### Long Messages

Messages longer than 2000 characters are automatically split:

```python
# This will be sent as multiple messages
long_text = "A" * 5000
await message.reply(long_text)  # Sends 3 messages with rate limiting
```

### Dynamic Content

```python
@router.command("info")
async def info_handler(message, args):
    response = f"""**User Information:**
    Name: {message.author_name}
    ID: {message.author_id}
    Channel: {message.channel_id}
    Is DM: {message.is_dm}"""
    
    await message.reply(response)
```

## Rich Embeds

Embeds provide beautiful, formatted messages with colors, fields, and images.

### Basic Embed

```python
@router.command("status")
async def status_handler(message, args):
    await message.reply_with_embed(
        title="Bot Status",
        description="Everything is running smoothly!",
        color=0x00FF00  # Green color
    )
```

### Embed with Fields

```python
@router.command("server")
async def server_handler(message, args):
    await message.reply_with_embed(
        title="Server Information",
        description="Current server statistics",
        color=0x3498DB,  # Blue
        fields=[
            {"name": "Users", "value": "150", "inline": True},
            {"name": "Channels", "value": "25", "inline": True},
            {"name": "Uptime", "value": "99.9%", "inline": True},
            {"name": "Features", "value": "Auto-moderation, Logging", "inline": False}
        ]
    )
```

### Embed with Footer and Images

```python
@router.command("profile")
async def profile_handler(message, args):
    await message.reply_with_embed(
        title=f"{message.author_name}'s Profile",
        description="User profile information",
        color=0x9B59B6,  # Purple
        fields=[
            {"name": "ID", "value": str(message.author_id), "inline": True},
            {"name": "Status", "value": "Active", "inline": True}
        ],
        footer="Requested just now",
        thumbnail_url="https://example.com/avatar.png"
    )
```

## Embed Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | str | Embed title |
| `description` | str | Main content text |
| `color` | int | Color code (hex, e.g., 0xFF0000 for red) |
| `fields` | list | List of field dictionaries |
| `footer` | str | Footer text |
| `image_url` | str | Main image URL |
| `thumbnail_url` | str | Thumbnail image URL |

### Field Format

Each field is a dictionary:

```python
{
    "name": "Field Name",      # Required
    "value": "Field Value",    # Required
    "inline": True             # Optional, default False
}
```

## Color Codes

Common colors:

```python
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF
YELLOW = 0xFFFF00
PURPLE = 0x9B59B6
ORANGE = 0xE67E22
BLACK = 0x000000
WHITE = 0xFFFFFF
```

## Error Embeds

```python
@router.command("error-demo")
async def error_demo(message, args):
    try:
        # Some operation
        result = 1 / 0
    except Exception as e:
        await message.reply_with_embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=0xFF0000,  # Red
            fields=[
                {"name": "Error Type", "value": type(e).__name__, "inline": True}
            ]
        )
```

## Success Embeds

```python
@router.command("success")
async def success_handler(message, args):
    await message.reply_with_embed(
        title="Success!",
        description="Operation completed successfully.",
        color=0x00FF00,
        fields=[
            {"name": "Action", "value": "Data Updated", "inline": True},
            {"name": "Time", "value": "Just now", "inline": True}
        ],
        footer="Thank you for using our bot!"
    )
```

## Complete Example

```python
import asyncio
from discord_bridge import Bridge, CommandRouter
import random

router = CommandRouter()

@router.command("status")
async def status(message, args):
    colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF]
    
    await message.reply_with_embed(
        title="🤖 Bot Status",
        description="Current system status",
        color=random.choice(colors),
        fields=[
            {"name": "Status", "value": "Online", "inline": True},
            {"name": "Latency", "value": "24ms", "inline": True},
            {"name": "Uptime", "value": "5 days", "inline": True},
            {"name": "Features", "value": "Embeds, Files, Commands", "inline": False}
        ],
        footer="Last updated: Just now"
    )

@router.command("user")
async def user_info(message, args):
    await message.reply_with_embed(
        title=f"👤 {message.author_name}",
        description="User information",
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

## Tips

1. **Use colors consistently**: Red for errors, green for success, blue for info
2. **Keep fields organized**: Group related fields together
3. **Use inline wisely**: Inline fields save space but can look cluttered
4. **Add footers**: Great for timestamps or additional context
5. **Test on mobile**: Embeds render differently on mobile devices
