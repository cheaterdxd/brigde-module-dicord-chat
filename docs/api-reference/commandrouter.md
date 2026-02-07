# CommandRouter

Router for handling Discord commands with decorator-based registration.

## Overview

```python
from discord_bridge import CommandRouter

router = CommandRouter()

@router.command("hello")
async def hello_handler(message, args):
    await message.reply(f"Hello, {message.author_name}!")
```

## Constructor

### `CommandRouter.__init__() -> None`

Initialize the command router.

**Example:**
```python
router = CommandRouter()
```

## Methods

### `command(name: str, description: str = "", usage: str = "") -> Callable`

Decorator to register a command handler.

**Parameters:**
- `name` (str): The command name (without prefix, e.g., "hello" for "!hello")
- `description` (str): Description shown in help text
- `usage` (str): Usage example shown in help text

**Returns:**
- Decorator function

**Example:**
```python
@router.command("hello", description="Say hello", usage="[name]")
async def hello_handler(message, args):
    name = args or message.author_name
    await message.reply(f"Hello, {name}!")
```

### `default(handler: Callable[[SmartMessage, str], Awaitable[None]]) -> None`

Set a default handler for unrecognized commands.

**Parameters:**
- `handler`: Async function to handle unknown commands

**Example:**
```python
@router.default
async def unknown_handler(message, args):
    await message.reply("Unknown command. Type !help for available commands.")
```

### `handle(message: SmartMessage) -> bool`

Handle an incoming message by routing to the appropriate command.

**Parameters:**
- `message` (SmartMessage): The SmartMessage to handle

**Returns:**
- `bool`: True if a handler was found and executed, False otherwise

**Example:**
```python
async for message in bridge.listen():
    handled = await router.handle(message)
    if not handled:
        print(f"Unhandled message: {message.content}")
```

### `get_commands() -> dict[str, CommandInfo]`

Get a dictionary of all registered commands.

**Returns:**
- Dictionary mapping command names to CommandInfo objects

**Example:**
```python
commands = router.get_commands()
for name, info in commands.items():
    print(f"{name}: {info.description}")
```

### `has_command(name: str) -> bool`

Check if a command is registered.

**Parameters:**
- `name` (str): The command name to check

**Returns:**
- `bool`: True if the command is registered, False otherwise

**Example:**
```python
if router.has_command("hello"):
    print("Hello command is registered")
```

## Built-in Commands

### `help`

The router automatically provides a `!help` command that lists all registered commands with their descriptions and usage information.

**Example Output:**
```
**Available Commands:**
`!hello` - Say hello
`!echo` - Echo back your message
  Usage: `!echo <message>`
```

## CommandInfo

Dataclass containing information about a registered command.

### Attributes

- `name` (str): The command name
- `handler` (Callable): The async function that handles the command
- `description` (str): Description for help text
- `usage` (str): Usage example

## Complete Example

```python
import asyncio
from discord_bridge import Bridge, CommandRouter

async def main():
    bridge = Bridge(config_path="config.yaml")
    router = CommandRouter()

    @router.command("hello", description="Say hello")
    async def hello_handler(message, args):
        await message.reply(f"Hello, {message.author_name}!")

    @router.command("echo", description="Echo back your message", usage="<message>")
    async def echo_handler(message, args):
        if args:
            await message.reply(f"Echo: {args}")
        else:
            await message.reply("Please provide a message to echo")

    @router.command("info")
    async def info_handler(message, args):
        info = f"""**Your Info:**
Name: {message.author_name}
ID: {message.author_id}
Channel: {message.channel_id}"""
        await message.reply(info)

    @router.default
    async def unknown_handler(message, args):
        await message.reply("Unknown command. Try !help")

    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()

    async for message in bridge.listen():
        await router.handle(message)

asyncio.run(main())
```
