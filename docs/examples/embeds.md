# Embeds Example

A complete example demonstrating rich embed messages with Discord Bridge.

## Code

```python
"""Example: Sending rich embed messages with formatting."""
import asyncio
import os
import shutil
import logging
import random

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

    @router.command("status")
    async def status_handler(message, args):
        """Send a status embed."""
        colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF]
        
        await message.reply_with_embed(
            title="Bot Status",
            description="Everything is running smoothly!",
            color=random.choice(colors),
            fields=[
                {"name": "Uptime", "value": "Online", "inline": True},
                {"name": "Version", "value": "2.0.0", "inline": True},
                {"name": "Commands", "value": str(len(router.get_commands())), "inline": True}
            ],
            footer="Powered by discord_bridge",
            thumbnail_url="https://cdn.discordapp.com/embed/avatars/0.png"
        )

    @router.command("server")
    async def server_handler(message, args):
        """Send server info embed."""
        await message.reply_with_embed(
            title="Server Information",
            description="This is an example embed with rich formatting",
            color=0x3498DB,
            fields=[
                {"name": "Feature 1", "value": "Automatic message splitting", "inline": False},
                {"name": "Feature 2", "value": "Rate limit protection", "inline": False},
                {"name": "Feature 3", "value": "Command routing", "inline": False},
                {"name": "Feature 4", "value": "Rich embeds", "inline": False}
            ],
            footer="discord_bridge - Making Discord bots simple"
        )

    @router.command("error")
    async def error_handler(message, args):
        """Send an error-style embed."""
        await message.reply_with_embed(
            title="Error Example",
            description="This is what an error embed looks like",
            color=0xFF0000,
            fields=[
                {"name": "Error Code", "value": "404", "inline": True},
                {"name": "Status", "value": "Not Found", "inline": True}
            ]
        )

    @router.command("colors")
    async def colors_handler(message, args):
        """Send multiple embeds with different colors."""
        colors = [
            (0xFF0000, "Red"),
            (0x00FF00, "Green"),
            (0x0000FF, "Blue"),
            (0xFFFF00, "Yellow"),
            (0xFF00FF, "Magenta"),
            (0x00FFFF, "Cyan")
        ]
        
        for color, name in colors:
            await message.reply_with_embed(
                title=f"{name} Color",
                description=f"Hex code: {hex(color)}",
                color=color
            )
            await asyncio.sleep(0.5)

    # Start bot
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    logger.info("Embed example bot ready!")

    try:
        async for message in bridge.listen():
            await router.handle(message)
    except asyncio.CancelledError:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

## What This Example Demonstrates

1. **Basic Embeds**: Creating simple embeds with title and description
2. **Embed Colors**: Using different colors for different message types
3. **Inline Fields**: Organizing information in columns
4. **Footer and Images**: Adding footer text and thumbnail images
5. **Multiple Embeds**: Sending multiple embeds in sequence

## Available Commands

| Command | Description |
|---------|-------------|
| `!status` | Shows bot status with random color |
| `!server` | Displays server information with features |
| `!error` | Shows error-style embed (red) |
| `!colors` | Sends 6 embeds with different colors |

## Key Concepts

### Basic Embed

```python
await message.reply_with_embed(
    title="My Title",
    description="My description",
    color=0x3498DB  # Blue
)
```

### Embed with Fields

```python
await message.reply_with_embed(
    title="Status",
    fields=[
        {"name": "Uptime", "value": "Online", "inline": True},
        {"name": "Version", "value": "2.0.0", "inline": True}
    ]
)
```

### Error vs Success Embeds

```python
# Error - red color
await message.reply_with_embed(
    title="Error",
    color=0xFF0000
)

# Success - green color
await message.reply_with_embed(
    title="Success",
    color=0x00FF00
)
```

## Color Reference

Common Discord embed colors:

| Color | Hex Code | Usage |
|-------|----------|-------|
| Red | `0xFF0000` | Errors |
| Green | `0x00FF00` | Success |
| Blue | `0x0000FF` | Information |
| Yellow | `0xFFFF00` | Warnings |
| Purple | `0x9B59B6` | Special |

## Running the Example

```bash
python examples/embeds.py
```

## Testing Commands

Try these commands to see different embed styles:

1. `!status` - Colorful status embed with fields
2. `!server` - Information embed with feature list
3. `!error` - Red error-style embed
4. `!colors` - Six different colored embeds

## Best Practices

1. **Use colors consistently**: Red for errors, green for success
2. **Limit inline fields**: 3 per row looks best
3. **Keep titles concise**: Under 256 characters
4. **Use footers**: Great for timestamps
5. **Test on mobile**: Embeds render differently
