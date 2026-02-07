# Command Router

The Command Router provides a clean, decorator-based way to handle Discord commands.

## Basic Usage

```python
from discord_bridge import Bridge, CommandRouter

router = CommandRouter()

@router.command("hello", description="Say hello")
async def hello_handler(message, args):
    await message.reply(f"Hello, {message.author_name}!")

@router.command("ping", description="Check if bot is alive")
async def ping_handler(message, args):
    await message.reply("Pong!")

# In your main loop
async for message in bridge.listen():
    await router.handle(message)
```

## Command Arguments

Arguments are automatically parsed and passed to your handler:

```python
@router.command("echo", description="Echo back your message", usage="<message>")
async def echo_handler(message, args):
    if args:
        await message.reply(f"You said: {args}")
    else:
        await message.reply("Please provide a message to echo")
```

Usage:
- `!echo Hello World` → args = "Hello World"
- `!echo` → args = ""

## Help Command

The router automatically generates a help command:

```python
# User types: !help
# Bot responds with:
# **Available Commands:**
# `!hello` - Say hello
# `!ping` - Check if bot is alive
# `!echo` - Echo back your message
#   Usage: `!echo <message>`
```

## Default Handler

Handle unknown commands:

```python
@router.default
async def unknown_handler(message, args):
    await message.reply(
        f"Unknown command. Type `!help` for available commands."
    )
```

## Command Information

Add metadata to commands:

```python
@router.command(
    "status",
    description="Show bot status",
    usage="[details]"
)
async def status_handler(message, args):
    # ...
```

## Checking Registered Commands

```python
# Get all commands
commands = router.get_commands()
for name, info in commands.items():
    print(f"{name}: {info.description}")

# Check if command exists
if router.has_command("hello"):
    print("Hello command is registered")
```

## Complete Example

```python
import asyncio
from discord_bridge import Bridge, CommandRouter, setup_logging
import logging

async def main():
    setup_logging(level=logging.INFO)
    
    bridge = Bridge(config_path="config.yaml")
    router = CommandRouter()
    
    @router.command("hello")
    async def hello(message, args):
        await message.reply(f"Hello, {message.author_name}!")
    
    @router.command("info")
    async def info(message, args):
        info_text = f"""**User Info:**
Name: {message.author_name}
ID: {message.author_id}
Channel: {message.channel_id}
DM: {message.is_dm}"""
        await message.reply(info_text)
    
    @router.default
    async def unknown(message, args):
        await message.reply("Unknown command. Try !help")
    
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    
    async for message in bridge.listen():
        await router.handle(message)

asyncio.run(main())
```

## Next Steps

- [Middleware](middleware.md) - Add preprocessing to commands
- [Replies & Embeds](replies-embeds.md) - Rich formatting
