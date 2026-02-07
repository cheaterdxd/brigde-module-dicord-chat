# Basic Usage

This guide covers the core concepts of using the Discord Bridge library.

## The Bridge Class

The `Bridge` class is the main entry point for interacting with Discord.

### Initialization

```python
from discord_bridge import Bridge

bridge = Bridge(config_path="config.yaml")
```

### Starting the Bot

```python
import asyncio

async def main():
    bridge = Bridge(config_path="config.yaml")
    
    # Start the bot (non-blocking)
    bot_task = asyncio.create_task(bridge.run())
    
    # Wait for connection
    await bridge.wait_for_ready()
    print("Bot is ready!")
    
    # Listen for messages
    async for message in bridge.listen():
        print(f"Received: {message.content}")
        await message.reply(f"Echo: {message.content}")

asyncio.run(main())
```

## SmartMessage Object

When you receive a message via `bridge.listen()`, you get a `SmartMessage` object with useful properties and methods.

### Properties

```python
async for message in bridge.listen():
    # Message content (without command prefix)
    content = message.content
    
    # Author information
    author_id = message.author_id      # Discord user ID
    author_name = message.author_name  # Display name
    
    # Channel information
    channel_id = message.channel_id    # Channel ID
    is_dm = message.is_dm              # True if direct message
```

### Replying to Messages

```python
# Simple text reply
await message.reply("Hello!")

# Long messages are automatically split
await message.reply("a" * 5000)  # Sends as 3 messages with rate limiting
```

## Graceful Shutdown

Always implement graceful shutdown to process pending messages:

```python
import asyncio

async def main():
    bridge = Bridge(config_path="config.yaml")
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    
    try:
        async for message in bridge.listen():
            await message.reply("Processing...")
    except asyncio.CancelledError:
        print("Shutting down...")
        await bridge.stop()  # Waits for queue to drain
        await bot_task

# Handle Ctrl+C
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutdown complete")
```

## Configuration

The bot behavior is controlled via `config.yaml`:

```yaml
discord_token: "your_token_here"
command_prefix: "!"
allowed_channel_ids: []  # Empty = all channels
max_reconnect_attempts: 5
reconnect_base_delay: 1.0
```

## Error Handling

Always handle potential errors:

```python
from discord_bridge import Bridge, ConfigurationError, ConnectionError

try:
    bridge = Bridge(config_path="config.yaml")
except ConfigurationError as e:
    print(f"Config error: {e}")
    exit(1)

try:
    await bridge.run()
except ConnectionError as e:
    print(f"Connection failed: {e}")
```

## Next Steps

- [Command Router](command-router.md) - Structured command handling
- [Replies & Embeds](replies-embeds.md) - Rich message formatting
- [File Attachments](attachments.md) - Uploading files
