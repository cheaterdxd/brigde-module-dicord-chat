# Basic Bot Example

A simple example showing the basic usage of the Discord Bridge library.

## Code

```python
import asyncio
import os
import shutil
import logging

from discord_bridge import Bridge, ConfigurationError, setup_logging


# --- Example AI Function ---
async def get_ai_response(prompt: str) -> str:
    """A simple function that simulates an AI processing a message."""
    logging.getLogger("discord_bridge").info(f"AI processing prompt: '{prompt}'")
    # In a real app, this would call OpenAI, Gemini, etc.
    await asyncio.sleep(0.5)  # Simulate network latency
    return f"The AI processed your prompt: '{prompt}'"


async def main():
    # Setup logging first
    logger = setup_logging(level=logging.INFO)
    
    # --- Initial Setup ---
    # Create a real config file from the example if it doesn't exist
    if not os.path.exists("config.yaml"):
        logger.info("config.yaml not found, creating one from example...")
        try:
            shutil.copy("config.yaml.example", "config.yaml")
            logger.warning("IMPORTANT: Please open 'config.yaml' and fill in your 'discord_token'.")
            return
        except FileNotFoundError:
            logger.error("ERROR: config.yaml.example not found! Please create a config.yaml.")
            return

    # --- Bot Initialization ---
    try:
        bridge = Bridge(config_path="config.yaml")
    except ConfigurationError as e:
        logger.error(f"Configuration failed: {e}")
        logger.error("Please ensure your 'config.yaml' is set up correctly.")
        return

    # Create a task to run the bot in the background
    bot_task = asyncio.create_task(bridge.run())
    
    logger.info("Bot is starting... waiting for it to be ready.")
    await bridge.wait_for_ready()
    logger.info("Bridge is connected and ready! Listening for commands...")

    # --- Main Application Loop ---
    # Start listening for commands from Discord
    try:
        async for message in bridge.listen():
            try:
                logger.info(f"Received command from {message.author_name}: '{message.content}'")
                
                # Get a response from our application logic (the "AI")
                response_text = await get_ai_response(message.content)

                # Send the response back to the same channel
                await message.reply(response_text)
                logger.info(f"Replied to {message.author_name}")

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Attempt to send an error message back to the user
                try:
                    await message.reply("Sorry, an error occurred while processing your request.")
                except Exception as reply_e:
                    logger.error(f"Failed to send error reply: {reply_e}")
    
    except asyncio.CancelledError:
        logger.info("Received shutdown signal, stopping gracefully...")
        await bridge.stop()
        await bot_task
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        await bridge.stop()
        await bot_task
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
        await bridge.stop()
        await bot_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down bot.")
    except Exception as e:
        print(f"\nAn unexpected error occurred in main: {e}")
```

## What This Example Demonstrates

1. **Logging Setup**: Using `setup_logging()` for structured logging
2. **Configuration Management**: Auto-creating config from example
3. **Bridge Initialization**: Creating and starting the Bridge
4. **Message Listening**: Using `async for` to receive messages
5. **Replying**: Sending responses back to Discord
6. **Error Handling**: Catching and logging errors
7. **Graceful Shutdown**: Using `bridge.stop()` on signals

## Running the Example

```bash
# Make sure you have a config.yaml with your token
python examples/main.py
```

## Expected Behavior

1. Bot connects to Discord
2. Logs "Bridge is connected and ready!"
3. When you type `!hello` (or your prefix + message):
   - Bot receives the message
   - Simulates AI processing (0.5s delay)
   - Replies with: "The AI processed your prompt: 'hello'"

## Key Concepts

### Setup Logging

```python
logger = setup_logging(level=logging.INFO)
```

This configures Python's logging module with a consistent format across the library.

### Bridge Lifecycle

```python
bridge = Bridge(config_path="config.yaml")
bot_task = asyncio.create_task(bridge.run())
await bridge.wait_for_ready()
```

1. Create Bridge instance (validates config)
2. Start bot in background task
3. Wait for connection to be ready

### Message Loop

```python
async for message in bridge.listen():
    # message.content has the text (without prefix)
    # message.author_name has the user's name
    # message.reply() sends a response
```

### Graceful Shutdown

```python
except asyncio.CancelledError:
    await bridge.stop()  # Waits for queue to drain
    await bot_task
```

This ensures all pending messages are processed before disconnecting.
