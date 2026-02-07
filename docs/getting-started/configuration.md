# Configuration

Discord Bridge uses a YAML configuration file to manage bot settings.

## Configuration File

Create a file named `config.yaml` in your project root:

```yaml
# Required: Your Discord bot token
discord_token: "YOUR_DISCORD_BOT_TOKEN_HERE"

# Optional: Command prefix (default: "!")
command_prefix: "!"

# Optional: Whitelist specific channel IDs
# Leave empty to allow all channels
allowed_channel_ids: []

# Optional: Maximum reconnection attempts (default: 5)
max_reconnect_attempts: 5

# Optional: Base delay for reconnection backoff in seconds (default: 1.0)
reconnect_base_delay: 1.0
```

## Getting Your Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot" and confirm
5. Click "Reset Token" and copy the new token
6. **Keep this token secret!** Never commit it to version control

## Bot Permissions

### Required Intents

Your bot needs these intents enabled:

- **Message Content Intent** - Required to read message content

To enable:
1. In Developer Portal, go to "Bot" section
2. Scroll to "Privileged Gateway Intents"
3. Enable "MESSAGE CONTENT INTENT"

### OAuth2 URL Generator

To invite your bot to a server:

1. Go to "OAuth2" → "URL Generator"
2. Select scopes:
   - `bot`
   - `applications.commands` (optional, for slash commands later)
3. Select bot permissions:
   - Send Messages
   - Read Messages/View Channels
   - Read Message History (optional)

4. Copy the generated URL and open it in your browser
5. Select the server to add the bot to

## Channel Whitelist

To restrict the bot to specific channels:

```yaml
allowed_channel_ids:
  - "123456789012345678"
  - "987654321098765432"
```

Get channel IDs by:
1. Enabling Developer Mode in Discord (User Settings → Advanced)
2. Right-clicking a channel
3. Selecting "Copy Channel ID"

## Environment Variables

You can also use environment variables for sensitive values:

```yaml
discord_token: "${DISCORD_TOKEN}"
```

Set the environment variable before running:

```bash
export DISCORD_TOKEN="your_token_here"
python bot.py
```

## Validation

The configuration is validated using Pydantic on startup:

- Token must not be the placeholder value
- Prefix must be 1-10 characters
- Channel IDs are automatically converted to integers
- Reconnect settings have reasonable defaults

Invalid configurations will raise `ConfigurationError` with clear error messages.

## Example Configurations

### Minimal Config

```yaml
discord_token: "your_token_here"
```

### Development Config

```yaml
discord_token: "your_token_here"
command_prefix: "?"
allowed_channel_ids:
  - "123456789"  # Test channel only
```

### Production Config

```yaml
discord_token: "your_token_here"
command_prefix: "!"
allowed_channel_ids: []
max_reconnect_attempts: 10
reconnect_base_delay: 2.0
```

## Next Steps

- [Quick Start](quickstart.md) - Build your first bot
- [Basic Usage](../user-guide/basic-usage.md) - Learn the core API
