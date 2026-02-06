# Discord Bridge Module

A simple, reliable Python library to bridge your application with Discord. This library allows you to easily listen for commands and send replies without dealing with the low-level details of the Discord API.

It's built on top of `discord.py` and provides a clean, modern `asyncio` interface.

## Features

- **Simple API**: Listen for commands with a simple `async for` loop.
- **Easy Replies**: A convenient `.reply()` method on message objects.
- **Automatic Message Splitting**: Automatically splits messages longer than 2000 characters.
- **Configuration File**: Easy setup via a `config.yaml` file.
- **Reliable**: Built on the robust `discord.py` library, it handles rate limits and reconnection automatically.
- **Custom Exceptions**: Clear error handling for configuration, connection, and message-sending issues.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd discord-bridge-module
    ```

2.  **Create a virtual environment:** (Recommended)
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Configure the Bot:**
    - Rename `config.yaml.example` to `config.yaml`.
    - Open `config.yaml` and paste your Discord Bot Token into the `discord_token` field. You can get a token from the [Discord Developer Portal](https://discord.com/developers/applications).
    - Make sure your bot has the **Message Content Intent** enabled in the Developer Portal.

2.  **Run the Example:**
    - The `examples/main.py` file shows a complete, working example of how to use the library.
    - To run it, simply execute:
    ```bash
    python examples/main.py
    ```

3.  **How it works:**
    - The bot will start and connect to Discord.
    - In any channel the bot is in, type `!hello` (or whatever `command_prefix` you set).
    - The application will receive the command, process it through a dummy "AI" function, and send a reply back to the channel.

## Integrating into Your Own Project

You can import and use the `Bridge` class just like in the example:

```python
import asyncio
from discord_bridge import Bridge

async def my_app():
    bridge = Bridge(config_path="config.yaml")
    
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()

    async for message in bridge.listen():
        # Your custom logic here
        await message.reply(f"You said: {message.content}")

if __name__ == "__main__":
    asyncio.run(my_app())
```
