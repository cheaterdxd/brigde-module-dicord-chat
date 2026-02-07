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
