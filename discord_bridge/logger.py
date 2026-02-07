"""Logging utilities for discord_bridge module."""
import logging
import sys


def setup_logging(
    level: int = logging.INFO,
    format_string: str | None = None,
    handler: logging.Handler | None = None,
) -> logging.Logger:
    """Setup logging configuration for the discord_bridge module.
    
    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string for log messages
        handler: Custom log handler (default: StreamHandler to stdout)
    
    Returns:
        Configured logger instance
    
    Example:
        >>> import logging
        >>> from discord_bridge.logger import setup_logging
        >>> logger = setup_logging(level=logging.DEBUG)
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logger = logging.getLogger("discord_bridge")
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    if handler is None:
        handler = logging.StreamHandler(sys.stdout)
    
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance for the discord_bridge module.
    
    Args:
        name: Optional submodule name (e.g., 'bridge', 'message')
    
    Returns:
        Logger instance
    
    Example:
        >>> from discord_bridge.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("This is a log message")
    """
    if name:
        return logging.getLogger(f"discord_bridge.{name}")
    return logging.getLogger("discord_bridge")
