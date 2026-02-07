# Exceptions

Custom exceptions for the Discord Bridge library.

## Exception Hierarchy

```
BridgeException (base)
├── ConfigurationError
├── ConnectionError
│   └── ReconnectExhaustedError
└── MessageSendError
```

## BridgeException

Base exception for all bridge-related errors.

All custom exceptions in this library inherit from this base class, making it easy to catch any bridge-related error.

**Example:**
```python
from discord_bridge import Bridge, BridgeException

try:
    bridge = Bridge("config.yaml")
    await bridge.run()
except BridgeException as e:
    print(f"Bridge error: {e}")
```

## ConfigurationError

Raised when there's an error with the configuration.

This can occur when:
- The config file is missing
- The config file has invalid YAML syntax
- Required fields (like discord_token) are missing
- Field values don't pass validation (e.g., placeholder token)

**Example:**
```python
from discord_bridge import Bridge, ConfigurationError

try:
    bridge = Bridge("missing_config.yaml")
except ConfigurationError as e:
    print(f"Config error: {e}")
    # Output: Config error: Config file not found at: missing_config.yaml
```

## ConnectionError

Raised when the bot fails to connect to Discord.

This typically occurs when:
- The Discord token is invalid
- Discord's servers are unreachable
- Network connectivity issues

**Example:**
```python
from discord_bridge import Bridge, ConnectionError

try:
    await bridge.run()
except ConnectionError as e:
    print(f"Failed to connect: {e}")
    # Output: Failed to connect: Failed to log in. Is the discord_token correct?
```

## ReconnectExhaustedError

Raised when all reconnection attempts have been exhausted.

This occurs when the bot loses connection to Discord and fails to reconnect after the maximum number of retry attempts.

### Attributes

- `attempts` (int): Number of reconnection attempts made
- `last_error` (Exception | None): The last error that caused reconnection to fail

**Example:**
```python
from discord_bridge import Bridge, ReconnectExhaustedError

try:
    await bridge.run()
except ReconnectExhaustedError as e:
    print(f"Failed after {e.attempts} attempts")
    print(f"Last error: {e.last_error}")
```

## MessageSendError

Raised when sending a message fails.

This can occur when:
- The bot lacks permissions to send messages in a channel
- Discord's rate limits are exceeded
- The message content is invalid
- Network issues during sending

**Example:**
```python
from discord_bridge import MessageSendError

async for message in bridge.listen():
    try:
        await message.reply("Hello!")
    except MessageSendError as e:
        print(f"Failed to send: {e}")
```

## Complete Error Handling Example

```python
import asyncio
from discord_bridge import (
    Bridge,
    ConfigurationError,
    ConnectionError,
    ReconnectExhaustedError,
    MessageSendError,
    setup_logging
)
import logging

async def main():
    logger = setup_logging(level=logging.INFO)
    
    # Configuration phase
    try:
        bridge = Bridge(config_path="config.yaml")
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your config.yaml file")
        return 1
    
    # Connection phase
    try:
        bot_task = asyncio.create_task(bridge.run())
        await bridge.wait_for_ready()
        logger.info("Bot connected successfully!")
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        logger.error("Please check your Discord token")
        return 1
    except ReconnectExhaustedError as e:
        logger.error(f"Reconnection failed after {e.attempts} attempts")
        logger.error(f"Last error: {e.last_error}")
        return 1
    
    # Message handling phase
    try:
        async for message in bridge.listen():
            try:
                # Process message
                response = f"Echo: {message.content}"
                await message.reply(response)
            except MessageSendError as e:
                logger.error(f"Failed to send message: {e}")
                # Continue processing other messages
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                try:
                    await message.reply("Sorry, an error occurred")
                except MessageSendError:
                    pass
    except asyncio.CancelledError:
        logger.info("Received shutdown signal")
        await bridge.stop()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        await bridge.stop()
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
```

## Best Practices

1. **Catch specific exceptions first**, then general ones:
```python
try:
    await bridge.run()
except ConfigurationError:
    # Handle config issues
    pass
except ConnectionError:
    # Handle connection issues
    pass
except BridgeException:
    # Handle any other bridge errors
    pass
```

2. **Always log errors** for debugging:
```python
import logging

logger = logging.getLogger(__name__)

try:
    await message.reply("Hello")
except MessageSendError as e:
    logger.error(f"Send failed: {e}")
```

3. **Gracefully degrade** when possible:
```python
try:
    await message.reply_with_embed(...)  # Try rich embed
except MessageSendError:
    await message.reply("Message content")  # Fall back to text
```
