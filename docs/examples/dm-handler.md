# DM Handler Example

A complete example demonstrating how to handle direct messages differently from channel messages.

## Code

```python
"""Example: Handling direct messages (DMs) differently from channel messages."""
import asyncio
import os
import shutil
import logging

from discord_bridge import Bridge, ConfigurationError, setup_logging, CommandRouter


async def main():
    logger = setup_logging(level=logging.INFO)
    
    if not os.path.exists("config.yaml"):
        shutil.copy("config.yaml.example", "config.yaml")
        logger.warning("Please configure config.yaml")
        return

    try:
        bridge = Bridge(config_path="config.yaml")
    except ConfigurationError as e:
        logger.error(f"Config error: {e}")
        return

    router = CommandRouter()

    @router.command("hello")
    async def hello_handler(message, args):
        """Handle hello differently in DMs vs channels."""
        if message.is_dm:
            await message.reply(
                f"Hey {message.author_name}! Thanks for messaging me privately. "
                f"Feel free to ask me anything here!"
            )
        else:
            await message.reply(f"Hello {message.author_name}! ")

    @router.command("support")
    async def support_handler(message, args):
        """Provide support info."""
        if message.is_dm:
            await message.reply(
                "Thanks for reaching out privately!\n\n"
                "For support, please describe your issue and I'll help you.\n"
                "Your message is confidential in this DM."
            )
        else:
            await message.reply(
                f"Hi {message.author_name}! For private support, "
                f"please DM me directly. I'm happy to help!"
            )

    @router.command("secret")
    async def secret_handler(message, args):
        """Only works in DMs."""
        if message.is_dm:
            await message.reply(
                "Here's your secret: The bot was built with discord_bridge! "
            )
        else:
            await message.reply(
                "This command only works in direct messages! "
                "Please DM me to get your secret."
            )

    @router.command("channel")
    async def channel_handler(message, args):
        """Show channel/DM info."""
        if message.is_dm:
            await message.reply(
                "You're in a **Direct Message** with me.\n"
                f"Your User ID: {message.author_id}\n"
                "This is a private conversation!"
            )
        else:
            await message.reply(
                f"You're in a **Server Channel** (ID: {message.channel_id})\n"
                f"Your User ID: {message.author_id}\n"
                "Others can see this conversation."
            )

    @router.command("broadcast")
    async def broadcast_handler(message, args):
        """Only works in channels."""
        if message.is_dm:
            await message.reply("Broadcasting only works in server channels!")
            return
        
        if not args:
            await message.reply("Usage: !broadcast <message>")
            return
        
        await message.reply(f" Broadcasting: {args}")

    # Log message types
    async def message_logger(message):
        """Log whether message is DM or channel."""
        msg_type = "DM" if message.is_dm else "Channel"
        logger.info(f"[{msg_type}] {message.author_name}: {message.content}")
        return True

    # Start bot
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    logger.info("DM handler bot ready!")

    try:
        async for message in bridge.listen():
            await message_logger(message)
            await router.handle(message)
    except asyncio.CancelledError:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

## What This Example Demonstrates

1. **DM Detection**: Using `message.is_dm` to check message type
2. **Different Responses**: Handling the same command differently
3. **DM-Only Commands**: Commands that only work in DMs
4. **Channel-Only Commands**: Commands that only work in channels
5. **Logging**: Tracking whether messages are DMs or channel messages

## Available Commands

| Command | DM Response | Channel Response |
|---------|-------------|------------------|
| `!hello` | Personal greeting | Standard greeting |
| `!support` | Confidential help | Suggests DM |
| `!secret` | Gives secret | Asks to use DM |
| `!channel` | Shows DM info | Shows channel info |
| `!broadcast` | Error message | Broadcasts message |

## Key Concepts

### Checking if DM

```python
if message.is_dm:
    await message.reply("This is a private DM!")
else:
    await message.reply("Hello from the channel!")
```

### DM-Only Command

```python
@router.command("private")
async def private_cmd(message, args):
    if not message.is_dm:
        await message.reply("This only works in DMs!")
        return
    
    # Handle private command
    await message.reply("Secret info...")
```

### Channel-Only Command

```python
@router.command("announce")
async def announce_cmd(message, args):
    if message.is_dm:
        await message.reply("Announcements only work in channels!")
        return
    
    # Handle announcement
    await message.reply(f"Announcement: {args}")
```

### Different Behavior

```python
@router.command("help")
async def help_cmd(message, args):
    if message.is_dm:
        # Detailed help for DM
        await message.reply("Detailed private help...")
    else:
        # Brief help for channel
        await message.reply("Quick help reference...")
```

## Running the Example

```bash
python examples/dm_handler.py
```

## Testing Commands

### In a Server Channel:
1. `!hello` → "Hello UserName!"
2. `!secret` → "This command only works in direct messages!"
3. `!broadcast Hello everyone` → " Broadcasting: Hello everyone"
4. `!channel` → Shows channel info

### In Direct Messages:
1. `!hello` → Personal greeting message
2. `!secret` → "Here's your secret: ..."
3. `!broadcast` → "Broadcasting only works in server channels!"
4. `!channel` → Shows DM info

## Use Cases

### Private Support
```python
@router.command("ticket")
async def ticket_cmd(message, args):
    if not message.is_dm:
        await message.reply("Please create tickets via DM for privacy")
        return
    
    # Create private support ticket
    ticket_id = create_ticket(message.author_id, args)
    await message.reply(f"Ticket #{ticket_id} created!")
```

### Admin Commands
```python
@router.command("admin")
async def admin_cmd(message, args):
    # Require DM for admin commands
    if not message.is_dm:
        await message.reply("Admin commands must be used in DMs")
        return
    
    # Verify admin status
    if message.author_id not in ADMIN_IDS:
        await message.reply("Not authorized")
        return
    
    # Execute admin command
```

### Personalized Content
```python
@router.command("profile")
async def profile_cmd(message, args):
    if message.is_dm:
        # Show full profile in DM
        await message.reply(get_full_profile(message.author_id))
    else:
        # Show limited profile in channel
        await message.reply(get_public_profile(message.author_id))
```
