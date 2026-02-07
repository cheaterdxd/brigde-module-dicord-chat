# Configuration

Configuration validation and management using Pydantic.

## BridgeConfig

Pydantic model for Discord Bridge configuration.

### Attributes

#### `discord_token: str`

Discord bot token from Discord Developer Portal.

**Validation:**
- Required field
- Minimum length: 1
- Cannot be placeholder value: "YOUR_DISCORD_BOT_TOKEN_HERE"

**Example:**
```yaml
discord_token: "MTAxMDIyMDY1NTQwOTExMjQ1MA.G1b8F0.xxx"
```

#### `command_prefix: str`

Prefix for bot commands.

**Default:** `"!"`

**Validation:**
- Minimum length: 1
- Maximum length: 10

**Example:**
```yaml
command_prefix: "?"
```

#### `allowed_channel_ids: List[int]`

List of whitelisted Discord channel IDs.

**Default:** `[]` (empty list allows all channels)

**Validation:**
- String channel IDs are automatically converted to integers

**Example:**
```yaml
allowed_channel_ids:
  - "123456789012345678"
  - "987654321098765432"
```

#### `max_reconnect_attempts: int`

Maximum reconnection attempts on disconnect.

**Default:** `5`

**Validation:**
- Minimum: 1
- Maximum: 20

**Example:**
```yaml
max_reconnect_attempts: 10
```

#### `reconnect_base_delay: float`

Base delay in seconds for exponential backoff.

**Default:** `1.0`

**Validation:**
- Minimum: 0.1
- Maximum: 60.0

**Example:**
```yaml
reconnect_base_delay: 2.0
```

## load_config Function

### `load_config(path: Path) -> tuple[str, str, List[int], int, float]`

Load and validate configuration from YAML file.

**Parameters:**
- `path` (Path): Path to the YAML configuration file

**Returns:**
- Tuple of `(token, prefix, allowed_channels, max_reconnect_attempts, reconnect_base_delay)`

**Raises:**
- `ConfigurationError`: If config file is not found or invalid

**Example:**
```python
from pathlib import Path
from discord_bridge.config import load_config

token, prefix, channels, max_retries, delay = load_config(Path("config.yaml"))
print(f"Token: {token}")
print(f"Prefix: {prefix}")
print(f"Allowed channels: {channels}")
```

## Validation Behavior

The configuration is automatically validated when loaded:

### Token Validation
```yaml
# ❌ Raises error - placeholder
discord_token: "YOUR_DISCORD_BOT_TOKEN_HERE"

# ❌ Raises error - empty
discord_token: ""

# ✅ Valid
discord_token: "actual_token_here"
```

### Channel ID Conversion
```yaml
# Both formats work - strings are converted to integers
allowed_channel_ids:
  - "123456789"      # String
  - 987654321        # Integer
```

### Type Coercion
Pydantic automatically converts types when possible:
```yaml
# String numbers are converted
max_reconnect_attempts: "5"    # Becomes integer 5
reconnect_base_delay: "1.5"    # Becomes float 1.5
```

## Error Messages

Clear error messages are provided for invalid configurations:

```python
from discord_bridge import Bridge, ConfigurationError

try:
    bridge = Bridge("config.yaml")
except ConfigurationError as e:
    print(e)
    # Possible outputs:
    # "Config file not found at: config.yaml"
    # "Invalid configuration: discord_token not found in config file"
    # "Invalid configuration: Please replace the placeholder token"
    # "Invalid YAML format in config file: ..."
```

## Complete Configuration Example

```yaml
# Required - your Discord bot token
discord_token: "MTAxMDIyMDY1NTQwOTExMjQ1MA.G1b8F0.xxx"

# Optional - command prefix (default: "!")
command_prefix: "!"

# Optional - restrict to specific channels
# Empty list = all channels allowed
allowed_channel_ids:
  - "123456789012345678"    # General channel
  - "987654321098765432"    # Bot commands channel

# Optional - reconnection settings
max_reconnect_attempts: 5
reconnect_base_delay: 1.0
```

## Environment Variables

You can use environment variables in your configuration:

```yaml
discord_token: "${DISCORD_TOKEN}"
```

Load with:
```bash
export DISCORD_TOKEN="your_token_here"
python bot.py
```

**Note:** Environment variable substitution requires additional setup. For basic usage, use direct values in the YAML file.

## Best Practices

1. **Keep token secret**: Never commit `config.yaml` to version control
   ```bash
   # Add to .gitignore
   config.yaml
   ```

2. **Use example file**: Provide `config.yaml.example` without real tokens

3. **Validate early**: Configuration errors are caught immediately on startup

4. **Use type hints**: The returned values are fully typed

5. **Handle errors gracefully**:
   ```python
   try:
       bridge = Bridge("config.yaml")
   except ConfigurationError as e:
       logger.error(f"Configuration error: {e}")
       sys.exit(1)
   ```

## See Also

- [Getting Started - Configuration](../getting-started/configuration.md)
- [Exceptions](exceptions.md) - ConfigurationError details
