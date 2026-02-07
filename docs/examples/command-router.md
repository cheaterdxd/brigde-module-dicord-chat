# Command Router Example

A complete example demonstrating the CommandRouter for structured command handling.

## Code

```python
"""Example: Using the Command Router for structured command handling."""
import asyncio
import os
import shutil
import logging
from datetime import datetime

from discord_bridge import Bridge, ConfigurationError, setup_logging, CommandRouter


async def main():
    # Setup logging
    logger = setup_logging(level=logging.INFO)
    
    # Create config if needed
    if not os.path.exists("config.yaml"):
        shutil.copy("config.yaml.example", "config.yaml")
        logger.warning("Please configure config.yaml with your Discord token")
        return

    # Initialize bridge
    try:
        bridge = Bridge(config_path="config.yaml")
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return

    # Create command router
    router = CommandRouter()

    # Register commands using decorators
    @router.command("hello")
    async def hello_handler(message, args):
        """Handle !hello command."""
        await message.reply(f"Hello, {message.author_name}! ")

    @router.command("time")
    async def time_handler(message, args):
        """Handle !time command."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(f"Current time: {current_time}")

    @router.command("echo")
    async def echo_handler(message, args):
        """Handle !echo command."""
        if args:
            await message.reply(f"You said: {args}")
        else:
            await message.reply("Please provide a message to echo. Usage: !echo <message>")

    @router.command("dm")
    async def dm_handler(message, args):
        """Handle !dm command."""
        if message.is_dm:
            await message.reply("This is a direct message!")
        else:
            await message.reply(f"This is a channel message (Channel ID: {message.channel_id})")

    @router.command("info")
    async def info_handler(message, args):
        """Handle !info command."""
        info = f"""**Your Info:**
Name: {message.author_name}
ID: {message.author_id}
Channel: {message.channel_id}
Is DM: {message.is_dm}"""
        await message.reply(info)

    # Start bot
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    logger.info("Bot ready! Commands registered: " + ", ".join(router.get_commands().keys()))

    # Main loop - use the router to handle messages
    try:
        async for message in bridge.listen():
            handled = await router.handle(message)
            if not handled:
                logger.warning(f"Unhandled message: {message.content}")
    except asyncio.CancelledError:
        logger.info("Shutting down...")
        await bridge.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
```

## What This Example Demonstrates

1. **Command Registration**: Using `@router.command()` decorator
2. **Command Arguments**: Parsing and using command arguments
3. **Built-in Help**: Automatic `!help` command generation
4. **Message Properties**: Accessing author, channel, and DM status
5. **Command Discovery**: Listing registered commands

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!hello` | Say hello | `!hello` → "Hello, UserName!" |
| `!time` | Get current time | `!time` → "Current time: 2024-01-15 10:30:45" |
| `!echo` | Echo back message | `!echo hello world` → "You said: hello world" |
| `!dm` | Check if DM | `!dm` → "This is a direct message!" or channel info |
| `!info` | Show user info | `!info` → Displays name, ID, channel, DM status |
| `!help` | Show help | Lists all commands automatically |

## Key Concepts

### Creating the Router

```python
router = CommandRouter()
```

### Registering Commands

```python
@router.command("hello")
async def hello_handler(message, args):
    await message.reply(f"Hello, {message.author_name}!")
```

### Using Arguments

```python
@router.command("echo")
async def echo_handler(message, args):
    # args contains everything after the command
    # !echo hello world → args = "hello world"
    if args:
        await message.reply(f"You said: {args}")
```

### Handling Messages

```python
async for message in bridge.listen():
    handled = await router.handle(message)
    if not handled:
        print(f"Unknown command: {message.content}")
```

### Getting Command Info

```python
commands = router.get_commands()
for name, info in commands.items():
    print(f"{name}: {info.description}")
```

## Running the Example

```bash
python examples/advanced_router.py
```

## Testing Commands

1. `!hello` - Simple greeting
2. `!time` - Shows current timestamp
3. `!echo Hello World` - Echoes your message
4. `!echo` (no args) - Shows usage hint
5. `!dm` - Tells you if you're in DM or channel
6. `!info` - Shows your Discord info
7. `!help` - Lists all available commands
8. `!unknown` - Shows that unregistered commands aren't handled

## Extending the Example

Add more commands:

```python
@router.command("ping")
async def ping_handler(message, args):
    await message.reply("Pong!")

@router.command("roll")
async def roll_handler(message, args):
    import random
    sides = int(args) if args and args.isdigit() else 6
    result = random.randint(1, sides)
    await message.reply(f"Rolled {result} (1-{sides})")
```
