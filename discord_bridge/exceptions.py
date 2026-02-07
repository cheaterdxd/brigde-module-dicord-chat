"""Custom exceptions for the Discord Bridge library."""


class BridgeException(Exception):
    """Base exception for all bridge-related errors.

    All custom exceptions in this library inherit from this base class,
    making it easy to catch any bridge-related error.

    Example:
        >>> try:
        ...     bridge = Bridge("config.yaml")
        ... except BridgeException as e:
        ...     print(f"Bridge error: {e}")
    """

    pass


class ConfigurationError(BridgeException):
    """Raised when there's an error with the configuration.

    This can occur when:
    - The config file is missing
    - The config file has invalid YAML syntax
    - Required fields (like discord_token) are missing
    - Field values don't pass validation

    Example:
        >>> try:
        ...     bridge = Bridge("missing_config.yaml")
        ... except ConfigurationError as e:
        ...     print(f"Config error: {e}")
    """

    pass


class ConnectionError(BridgeException):
    """Raised when the bot fails to connect to Discord.

    This typically occurs when:
    - The Discord token is invalid
    - Discord's servers are unreachable
    - Network connectivity issues

    Example:
        >>> try:
        ...     await bridge.run()
        ... except ConnectionError as e:
        ...     print(f"Failed to connect: {e}")
    """

    pass


class MessageSendError(BridgeException):
    """Raised when sending a message fails.

    This can occur when:
    - The bot lacks permissions to send messages in a channel
    - Discord's rate limits are exceeded
    - The message content is invalid
    - Network issues during sending

    Example:
        >>> try:
        ...     await message.reply("Hello!")
        ... except MessageSendError as e:
        ...     print(f"Failed to send: {e}")
    """

    pass


class ReconnectExhaustedError(ConnectionError):
    """Raised when all reconnection attempts have been exhausted.

    This occurs when the bot loses connection to Discord and fails
    to reconnect after the maximum number of retry attempts.

    Attributes:
        attempts: Number of reconnection attempts made
        last_error: The last error that caused reconnection to fail

    Example:
        >>> try:
        ...     await bridge.run()
        ... except ReconnectExhaustedError as e:
        ...     print(f"Failed after {e.attempts} attempts: {e.last_error}")
    """

    def __init__(
        self, message: str, attempts: int = 0, last_error: Exception | None = None
    ) -> None:
        """Initialize the exception with retry information.

        Args:
            message: Error message
            attempts: Number of reconnection attempts made
            last_error: The last exception that caused failure
        """
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error
