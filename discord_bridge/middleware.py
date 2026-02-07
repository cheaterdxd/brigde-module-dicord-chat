"""Middleware system for extending Discord Bridge functionality."""

from typing import Callable, Awaitable, List
from dataclasses import dataclass

from .message import SmartMessage
from .logger import get_logger

logger = get_logger(__name__)

# Type alias for middleware functions
MiddlewareFunction = Callable[
    [SmartMessage, Callable[[SmartMessage], Awaitable[None]]], Awaitable[None]
]


@dataclass
class MiddlewareContext:
    """Context object passed through middleware chain.

    Attributes:
        message: The SmartMessage being processed
        metadata: Dictionary for middleware to store/retrieve data
        cancelled: If True, message processing should stop
    """

    message: SmartMessage
    metadata: dict = None
    cancelled: bool = False

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MiddlewareManager:
    """Manager for middleware chain execution.

    Middleware allows you to intercept and modify messages before they
    reach command handlers. Each middleware can:
    - Log messages
    - Add metadata
    - Cancel message processing
    - Modify the message
    - Execute code before/after command handling

    Example:
        >>> manager = MiddlewareManager()
        >>>
        >>> @manager.use
        >>> async def logging_middleware(ctx, next):
        ...     print(f"Processing: {ctx.message.content}")
        ...     await next(ctx)
        ...     print(f"Completed: {ctx.message.content}")
        >>>
        >>> @manager.use
        >>> async def rate_limit_middleware(ctx, next):
        ...     if ctx.metadata.get('rate_limited'):
        ...         await ctx.message.reply("Rate limited!")
        ...         return
        ...     await next(ctx)
        >>>
        >>> # In your main loop:
        >>> async for message in bridge.listen():
        ...     await manager.execute(message, router.handle)
    """

    def __init__(self) -> None:
        """Initialize the middleware manager."""
        self._middlewares: List[MiddlewareFunction] = []
        logger.debug("MiddlewareManager initialized")

    def use(self, middleware: MiddlewareFunction) -> MiddlewareFunction:
        """Decorator to register a middleware function.

        Args:
            middleware: Async function with signature:
                async def middleware(ctx: MiddlewareContext, next: Callable) -> None

        Returns:
            The middleware function (for decorator usage)

        Example:
            >>> @manager.use
            >>> async def my_middleware(ctx, next):
            ...     # Before command handling
            ...     print("Before")
            ...     await next(ctx)
            ...     # After command handling
            ...     print("After")
        """
        self._middlewares.append(middleware)
        logger.debug(f"Registered middleware: {middleware.__name__}")
        return middleware

    def remove(self, middleware: MiddlewareFunction) -> bool:
        """Remove a middleware from the chain.

        Args:
            middleware: The middleware function to remove

        Returns:
            True if removed, False if not found
        """
        if middleware in self._middlewares:
            self._middlewares.remove(middleware)
            logger.debug(f"Removed middleware: {middleware.__name__}")
            return True
        return False

    def clear(self) -> None:
        """Remove all middleware from the chain."""
        self._middlewares.clear()
        logger.debug("All middleware cleared")

    async def execute(
        self, message: SmartMessage, handler: Callable[[SmartMessage], Awaitable[None]]
    ) -> bool:
        """Execute the middleware chain and final handler.

        Args:
            message: The message to process
            handler: The final handler to execute (e.g., router.handle)

        Returns:
            True if message was handled, False if cancelled
        """
        ctx = MiddlewareContext(message=message)

        # Build the execution chain
        async def execute_chain(index: int) -> None:
            if ctx.cancelled:
                logger.debug("Message processing cancelled by middleware")
                return

            if index < len(self._middlewares):
                # Execute next middleware
                middleware = self._middlewares[index]
                logger.debug(f"Executing middleware: {middleware.__name__}")

                async def next_middleware():
                    await execute_chain(index + 1)

                await middleware(ctx, next_middleware)
            else:
                # Execute final handler
                logger.debug("Executing final handler")
                await handler(message)

        await execute_chain(0)
        return not ctx.cancelled


# Built-in middleware examples


async def logging_middleware(ctx: MiddlewareContext, next: Callable) -> None:
    """Built-in middleware that logs all message processing.

    Example:
        >>> manager = MiddlewareManager()
        >>> manager.use(logging_middleware)
    """
    logger.info(
        f"[START] Processing command from {ctx.message.author_name}: {ctx.message.content}"
    )
    await next()
    logger.info(f"[END] Finished processing command from {ctx.message.author_name}")


async def rate_limit_middleware(
    ctx: MiddlewareContext,
    next: Callable,
    max_requests: int = 5,
    window_seconds: float = 60.0,
) -> None:
    """Built-in middleware for rate limiting.

    Limits each user to a certain number of requests per time window.

    Args:
        ctx: Middleware context
        next: Next middleware in chain
        max_requests: Maximum requests allowed per window
        window_seconds: Time window in seconds

    Example:
        >>> manager = MiddlewareManager()
        >>> # Using functools.partial to configure
        >>> from functools import partial
        >>> manager.use(partial(rate_limit_middleware, max_requests=3, window_seconds=10))
    """
    import time
    from collections import defaultdict

    # This would normally be stored in a persistent way
    # For demo purposes, using a simple dict (resets on restart)
    if not hasattr(rate_limit_middleware, "_user_requests"):
        rate_limit_middleware._user_requests = defaultdict(list)

    user_id = ctx.message.author_id
    current_time = time.time()

    # Clean old requests
    rate_limit_middleware._user_requests[user_id] = [
        req_time
        for req_time in rate_limit_middleware._user_requests[user_id]
        if current_time - req_time < window_seconds
    ]

    # Check rate limit
    if len(rate_limit_middleware._user_requests[user_id]) >= max_requests:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        await ctx.message.reply(
            f"You're sending commands too fast! Please wait {window_seconds} seconds."
        )
        ctx.cancelled = True
        return

    # Record this request
    rate_limit_middleware._user_requests[user_id].append(current_time)

    await next()


async def dm_only_middleware(ctx: MiddlewareContext, next: Callable) -> None:
    """Built-in middleware to restrict commands to DMs only.

    Example:
        >>> manager = MiddlewareManager()
        >>> manager.use(dm_only_middleware)
    """
    if not ctx.message.is_dm:
        logger.debug(f"Ignoring non-DM message from {ctx.message.author_name}")
        await ctx.message.reply("This command only works in direct messages!")
        ctx.cancelled = True
        return

    await next()


async def admin_only_middleware(
    ctx: MiddlewareContext, next: Callable, admin_ids: List[int]
) -> None:
    """Built-in middleware to restrict commands to admin users.

    Args:
        ctx: Middleware context
        next: Next middleware in chain
        admin_ids: List of admin user IDs

    Example:
        >>> manager = MiddlewareManager()
        >>> from functools import partial
        >>> admin_ids = [123456789, 987654321]
        >>> manager.use(partial(admin_only_middleware, admin_ids=admin_ids))
    """
    if ctx.message.author_id not in admin_ids:
        logger.warning(f"Non-admin user {ctx.message.author_id} tried admin command")
        await ctx.message.reply("You don't have permission to use this command.")
        ctx.cancelled = True
        return

    await next()
