# Bridge

The main class for connecting to Discord and handling messages.

## Overview

```python
from discord_bridge import Bridge

bridge = Bridge(config_path="config.yaml")
```

## Constructor

### `Bridge.__init__(config_path: str) -> None`

Initialize the Bridge with configuration.

**Parameters:**
- `config_path` (str): Path to the YAML configuration file

**Raises:**
- `ConfigurationError`: If config file is not found or invalid

**Example:**
```python
bridge = Bridge(config_path="config.yaml")
```

## Methods

### `run() -> None`

Start the bot and connect to Discord.

This method starts the Discord client and begins listening for messages. It will block until the connection is closed.

**Raises:**
- `ConnectionError`: If login fails (invalid token)
- `ReconnectExhaustedError`: If all reconnection attempts are exhausted

**Example:**
```python
bot_task = asyncio.create_task(bridge.run())
```

### `stop() -> None`

Gracefully stop the bot and disconnect from Discord.

This method will:
1. Set the shutdown flag to stop accepting new messages
2. Wait for pending messages in the queue to be processed
3. Close the Discord client connection

**Example:**
```python
await bridge.stop()
```

### `wait_for_ready() -> None`

Wait until the bot is connected and ready to receive messages.

This method blocks until the bot has successfully connected to Discord and is ready to process messages.

**Example:**
```python
await bridge.wait_for_ready()
print("Bot is ready!")
```

### `listen() -> AsyncIterator[SmartMessage]`

Async iterator that yields messages received from Discord.

This is the main interface for receiving messages. Use it in an async for loop to process incoming commands.

**Yields:**
- `SmartMessage`: A wrapped message object with convenient reply method

**Example:**
```python
async for message in bridge.listen():
    print(f"Received: {message.content}")
    await message.reply(f"You said: {message.content}")
```

## Attributes

### `config_path: str`

Path to the configuration file.

### `is_ready: bool`

Whether the bot is connected and ready.

### `bot_user_id: int | None`

The Discord user ID of the bot (set after connection).

### `token: str`

The Discord bot token (loaded from config).

### `prefix: str`

The command prefix (loaded from config, default: "!").

### `allowed_channels: List[int]`

List of whitelisted channel IDs (empty = all channels allowed).

### `max_reconnect_attempts: int`

Maximum reconnection attempts on disconnect.

### `reconnect_base_delay: float`

Base delay in seconds for exponential backoff during reconnection.

## Complete Example

```python
import asyncio
from discord_bridge import Bridge, ConfigurationError, setup_logging
import logging

async def main():
    # Setup logging
    logger = setup_logging(level=logging.INFO)
    
    # Initialize bridge
    try:
        bridge = Bridge(config_path="config.yaml")
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Start bot
    bot_task = asyncio.create_task(bridge.run())
    
    # Wait for ready
    logger.info("Waiting for bot to be ready...")
    await bridge.wait_for_ready()
    logger.info("Bot is ready!")
    
    # Listen for messages
    try:
        async for message in bridge.listen():
            logger.info(f"Received: {message.content}")
            await message.reply(f"Echo: {message.content}")
    except asyncio.CancelledError:
        logger.info("Shutting down...")
        await bridge.stop()
        await bot_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
```
