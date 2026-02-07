# Quick Start

Get your first Discord bot running in 5 minutes!

## Step 1: Create Configuration

Create `config.yaml`:

```yaml
discord_token: "YOUR_BOT_TOKEN_HERE"
command_prefix: "!"
```

## Step 2: Create Your Bot

Create `mybot.py`:

```python
import asyncio
from discord_bridge import Bridge

async def main():
    # Initialize the bridge
    bridge = Bridge(config_path="config.yaml")
    
    # Start bot in background
    bot_task = asyncio.create_task(bridge.run())
    
    # Wait for bot to connect
    print("Connecting to Discord...")
    await bridge.wait_for_ready()
    print("Bot is ready!")
    
    # Listen for messages
    async for message in bridge.listen():
        print(f"Received: {message.content}")
        
        # Reply to the message
        await message.reply(f"You said: {message.content}")

# Run the bot
asyncio.run(main())
```

## Step 3: Run Your Bot

```bash
python mybot.py
```

You should see:
```
Connecting to Discord...
Bridge is ready. Logged in as YourBotName#1234
Bot is ready!
```

## Step 4: Test It

1. Invite your bot to a Discord server
2. Type `!hello` in any channel
3. Your bot should reply: "You said: hello"

## Next: Add Commands

Use the Command Router for structured command handling:

```python
from discord_bridge import Bridge, CommandRouter

async def main():
    bridge = Bridge(config_path="config.yaml")
    router = CommandRouter()
    
    @router.command("hello")
    async def hello(message, args):
        await message.reply(f"Hello, {message.author_name}!")
    
    @router.command("ping")
    async def ping(message, args):
        await message.reply("Pong!")
    
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    
    async for message in bridge.listen():
        await router.handle(message)

asyncio.run(main())
```

Try:
- `!hello` → "Hello, YourName!"
- `!ping` → "Pong!"
- `!help` → Shows all available commands

## Common Issues

### "Config file not found"
- Make sure `config.yaml` is in the same directory as your script
- Check that the filename is correct

### "Failed to log in"
- Your token might be incorrect
- Copy it again from the Discord Developer Portal
- Make sure there are no extra spaces

### Bot doesn't respond
- Check that your bot has permission to read and send messages
- Verify the command prefix matches (default is `!`)
- Check console for error messages

## Next Steps

- [Basic Usage](../user-guide/basic-usage.md) - Learn more about the API
- [Command Router](../user-guide/command-router.md) - Structured command handling
- [API Reference](../api-reference/bridge.md) - Complete documentation
