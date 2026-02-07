# Discord Bridge Module

A simple, reliable Python library to bridge your application with Discord. This library allows you to easily listen for commands and send replies without dealing with the low-level details of the Discord API.

## Features

- **Simple API** - Listen for commands with a simple `async for` loop
- **Easy Replies** - Convenient `.reply()` method on message objects
- **Command Router** - Decorator-based command registration with built-in help
- **Automatic Message Splitting** - Automatically splits messages longer than 2000 characters
- **Rate Limit Protection** - Respects Discord's rate limits with built-in delays
- **Configuration File** - Easy setup via a `config.yaml` file with Pydantic validation
- **Channel Whitelist** - Restrict bot to specific channels
- **Automatic Reconnection** - Exponential backoff reconnection strategy
- **Graceful Shutdown** - Clean shutdown that processes pending messages
- **Rich Embeds** - Send beautifully formatted embed messages
- **File Attachments** - Upload files with messages
- **Middleware System** - Extend functionality with custom middleware
- **Comprehensive Logging** - Full Python logging integration
- **Type Hints** - Full type annotation support

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
import asyncio
from discord_bridge import Bridge

async def main():
    bridge = Bridge(config_path="config.yaml")
    
    # Start bot in background
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    
    # Listen for messages
    async for message in bridge.listen():
        await message.reply(f"You said: {message.content}")

asyncio.run(main())
```

## Configuration

Create a `config.yaml` file:

```yaml
discord_token: "YOUR_BOT_TOKEN_HERE"
command_prefix: "!"
allowed_channel_ids: []  # Optional: restrict to specific channels
max_reconnect_attempts: 5
reconnect_base_delay: 1.0
```

Get your bot token from the [Discord Developer Portal](https://discord.com/developers/applications).

## Next Steps

- [Installation Guide](getting-started/installation.md) - Detailed installation instructions
- [Quick Start](getting-started/quickstart.md) - Your first bot in 5 minutes
- [Command Router](user-guide/command-router.md) - Structured command handling
- [API Reference](api-reference/bridge.md) - Complete API documentation

## Example: Command Router

```python
from discord_bridge import Bridge, CommandRouter

router = CommandRouter()

@router.command("hello", description="Say hello")
async def hello_handler(message, args):
    await message.reply(f"Hello, {message.author_name}!")

@router.command("help")
async def help_handler(message, args):
    # Built-in help command lists all commands
    pass

# In your main loop:
async for message in bridge.listen():
    await router.handle(message)
```

## Example: Rich Embeds

```python
@router.command("info")
async def info_handler(message, args):
    await message.reply_with_embed(
        title="Bot Information",
        description="A helpful Discord bot",
        color=0x3498db,
        fields=[
            {"name": "Version", "value": "2.0.0", "inline": True},
            {"name": "Status", "value": "Online", "inline": True}
        ],
        footer="Powered by discord_bridge"
    )
```

## License

MIT License - See LICENSE file for details
