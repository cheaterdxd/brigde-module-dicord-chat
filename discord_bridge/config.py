from pathlib import Path
from typing import List
import yaml
from pydantic import BaseModel, Field, validator
from .exceptions import ConfigurationError
from .logger import get_logger

logger = get_logger(__name__)


class BridgeConfig(BaseModel):
    """Pydantic model for Discord Bridge configuration.
    
    This model validates and provides type-safe access to configuration
    values from the YAML config file.
    
    Attributes:
        discord_token: Discord bot token (required)
        command_prefix: Prefix for bot commands (default: "!")
        allowed_channel_ids: List of whitelisted channel IDs (optional)
        max_reconnect_attempts: Max retry attempts on disconnect (default: 5)
        reconnect_base_delay: Initial delay for exponential backoff in seconds (default: 1.0)
    """
    
    discord_token: str = Field(
        ...,
        description="Discord bot token from Discord Developer Portal",
        min_length=1
    )
    command_prefix: str = Field(
        default="!",
        description="Prefix for bot commands",
        min_length=1,
        max_length=10
    )
    allowed_channel_ids: List[int] = Field(
        default_factory=list,
        description="List of whitelisted Discord channel IDs"
    )
    max_reconnect_attempts: int = Field(
        default=5,
        description="Maximum reconnection attempts on disconnect",
        ge=1,
        le=20
    )
    reconnect_base_delay: float = Field(
        default=1.0,
        description="Base delay in seconds for exponential backoff",
        ge=0.1,
        le=60.0
    )
    
    @validator('discord_token')
    def token_not_placeholder(cls, v):
        """Ensure token is not the placeholder value."""
        if v == "YOUR_DISCORD_BOT_TOKEN_HERE":
            raise ValueError("Please replace the placeholder token with your actual Discord bot token")
        return v
    
    @validator('allowed_channel_ids', pre=True)
    def parse_channel_ids(cls, v):
        """Convert string channel IDs to integers."""
        if isinstance(v, list):
            return [int(x) for x in v]
        return v


def load_config(path: Path) -> tuple[str, str, List[int], int, float]:
    """Load and validate configuration from YAML file.
    
    Args:
        path: Path to the YAML configuration file
        
    Returns:
        Tuple of (token, prefix, allowed_channels, max_reconnect_attempts, reconnect_base_delay)
        
    Raises:
        ConfigurationError: If config file is not found or invalid
        
    Example:
        >>> from pathlib import Path
        >>> token, prefix, channels, max_retries, delay = load_config(Path("config.yaml"))
    """
    logger.debug(f"Loading configuration from {path}")
    
    try:
        with open(path, "r") as f:
            raw_config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {path}")
        raise ConfigurationError(f"Config file not found at: {path}")
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in config file: {e}")
        raise ConfigurationError(f"Invalid YAML format in config file: {e}")
    
    if raw_config is None:
        logger.error("Configuration file is empty")
        raise ConfigurationError("Config file is empty")
    
    try:
        config = BridgeConfig(**raw_config)
        logger.info("Configuration validated successfully")
        return (
            config.discord_token,
            config.command_prefix,
            config.allowed_channel_ids,
            config.max_reconnect_attempts,
            config.reconnect_base_delay
        )
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise ConfigurationError(f"Invalid configuration: {e}")
