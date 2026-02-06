class BridgeException(Exception):
    """Base exception for the bridge library."""
    pass

class ConfigurationError(BridgeException):
    """Raised for configuration-related errors."""
    pass