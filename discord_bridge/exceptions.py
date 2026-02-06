class BridgeException(Exception):
    """Base exception for the bridge library."""
    pass

class ConfigurationError(BridgeException):
    """Raised for configuration-related errors."""
    pass

class ConnectionError(BridgeException):
    """Raised for connection-related errors."""
    pass

class MessageSendError(BridgeException):
    """Raised when sending a message fails."""
    pass
