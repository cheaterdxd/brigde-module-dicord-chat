import asyncio
import os
import shutil
from discord_bridge import Bridge, ConfigurationError

# --- Example AI Function ---
async def get_ai_response(prompt: str) -> str:
    """A simple function that simulates an AI processing a message."""
    print(f"  -> AI processing prompt: '{prompt}'")
    # In a real app, this would call OpenAI, Gemini, etc.
    await asyncio.sleep(0.5) # Simulate network latency
    return f"The AI processed your prompt: '{prompt}'"


async def main():
    # --- Initial Setup ---
    # Create a real config file from the example if it doesn't exist
    if not os.path.exists("config.yaml"):
        print("config.yaml not found, creating one from example...")
        try:
            shutil.copy("config.yaml.example", "config.yaml")
            print("
IMPORTANT: Please open 'config.yaml' and fill in your 'discord_token'.")
            return
        except FileNotFoundError:
            print("ERROR: config.yaml.example not found! Please create a config.yaml.")
            return

    # --- Bot Initialization ---
    try:
        bridge = Bridge(config_path="config.yaml")
    except ConfigurationError as e:
        print(f"ERROR: Configuration failed. {e}")
        print("
Please ensure your 'config.yaml' is set up correctly.")
        return

    # Create a task to run the bot in the background
    bot_task = asyncio.create_task(bridge.run())
    
    print("Bot is starting... waiting for it to be ready.")
    await bridge.wait_for_ready()
    print("Bridge is connected and ready! Listening for commands...")

    # --- Main Application Loop ---
    # Start listening for commands from Discord
    async for message in bridge.listen():
        try:
            print(f"
[+] Received command from user {message.author_id}: '{message.content}'")
            
            # Get a response from our application logic (the "AI")
            response_text = await get_ai_response(message.content)

            # Send the response back to the same channel
            await message.reply(response_text)
            print(f"  Replied to user {message.author_id}.")

        except Exception as e:
            print(f"[!] An error occurred while processing a message: {e}")
            # Attempt to send an error message back to the user
            try:
                await message.reply("Sorry, an error occurred while processing your request.")
            except Exception as reply_e:
                print(f"[!] Failed to send error reply: {reply_e}")
    
    # This part is only reached if the bot_task somehow finishes
    await bot_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("
Shutting down bot.")
    except Exception as e:
        print(f"
An unexpected error occurred in main: {e}")

