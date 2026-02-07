# Discord Bridge Module

A simple, reliable Python library to bridge your application with Discord. This library allows you to easily listen for commands and send replies without dealing with the low-level details of the Discord API.

It's built on top of `discord.py` and provides a clean, modern `asyncio` interface.

## Features

- **Simple API** - Listen for commands with a simple `async for` loop
- **Easy Replies** - A convenient `.reply()` method on message objects
- **Command Router** - Decorator-based command registration with built-in help command
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

1. **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd discord-bridge-module
    ```

2. **Create a virtual environment:** (Recommended)
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3. **Install dependencies:**
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

## Usage Examples

### Basic Bot

```python
import asyncio
from discord_bridge import Bridge, setup_logging
import logging

async def main():
    # Setup logging
    setup_logging(level=logging.INFO)
    
    bridge = Bridge(config_path="config.yaml")
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    
    async for message in bridge.listen():
        await message.reply(f"Echo: {message.content}")

asyncio.run(main())
```

### Command Router

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

async for message in bridge.listen():
    await router.handle(message)
```

### Rich Embeds

```python
await message.reply_with_embed(
    title="Bot Status",
    description="Everything is running smoothly!",
    color=0x00FF00,
    fields=[
        {"name": "Version", "value": "2.0.0", "inline": True},
        {"name": "Status", "value": "Online", "inline": True}
    ],
    footer="Powered by discord_bridge"
)
```

### File Attachments

```python
await message.reply_with_file(
    content="Here's your file!",
    file_path="/path/to/document.pdf",
    filename="report.pdf"
)
```

### Graceful Shutdown

```python
import asyncio

async for message in bridge.listen():
    if message.content == "shutdown":
        await message.reply("Shutting down...")
        await bridge.stop()  # Waits for pending messages
        break
```

## Documentation

Full documentation is available at: [https://cheaterdxd.github.io/discord-bridge-module](https://cheaterdxd.github.io/discord-bridge-module)

Or build locally:

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs serve
```

## Examples

See the `examples/` directory for complete working examples:

- `main.py` - Basic bot with logging
- `advanced_router.py` - Command router with multiple commands
- `embeds.py` - Rich embed messages
- `attachments.py` - File uploads
- `dm_handler.py` - DM vs channel handling

## Development

### Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

### Linting

```bash
pip install ruff
ruff check discord_bridge/
ruff format discord_bridge/
```

### Type Checking

```bash
pip install mypy
mypy discord_bridge/ --ignore-missing-imports
```

## CI/CD

This project uses GitHub Actions for:
- Automated testing on Python 3.8-3.12
- Code linting with ruff
- Type checking with mypy
- Documentation building
- Automatic PyPI publishing on releases

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

If you have any questions or issues, please open an issue on GitHub.
