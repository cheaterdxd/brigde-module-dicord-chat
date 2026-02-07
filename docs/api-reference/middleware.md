# Middleware

Middleware system for extending Discord Bridge functionality.

## MiddlewareManager

Manager for middleware chain execution.

### Overview

Middleware allows you to intercept and modify messages before they reach command handlers. Each middleware can:

- Execute code before the command
- Execute code after the command
- Cancel message processing
- Add metadata to the context

```python
from discord_bridge import MiddlewareManager

manager = MiddlewareManager()
```

## Constructor

### `MiddlewareManager.__init__() -> None`

Initialize the middleware manager.

**Example:**
```python
manager = MiddlewareManager()
```

## Methods

### `use(middleware: MiddlewareFunction) -> MiddlewareFunction`

Decorator to register a middleware function.

**Parameters:**
- `middleware`: Async function with signature `async def middleware(ctx: MiddlewareContext, next: Callable) -> None`

**Returns:**
- The middleware function (for decorator usage)

**Example:**
```python
@manager.use
async def my_middleware(ctx, next):
    # Before command handling
    print("Before")
    await next()
    # After command handling
    print("After")
```

### `remove(middleware: MiddlewareFunction) -> bool`

Remove a middleware from the chain.

**Parameters:**
- `middleware`: The middleware function to remove

**Returns:**
- `bool`: True if removed, False if not found

**Example:**
```python
removed = manager.remove(my_middleware)
if removed:
    print("Middleware removed")
```

### `clear() -> None`

Remove all middleware from the chain.

**Example:**
```python
manager.clear()  # Remove all middleware
```

### `execute(message: SmartMessage, handler: Callable[[SmartMessage], Awaitable[None]]) -> bool`

Execute the middleware chain and final handler.

**Parameters:**
- `message` (SmartMessage): The message to process
- `handler`: The final handler to execute (e.g., `router.handle`)

**Returns:**
- `bool`: True if message was handled, False if cancelled

**Example:**
```python
was_handled = await manager.execute(message, router.handle)
if not was_handled:
    print("Message was cancelled by middleware")
```

## MiddlewareContext

Context object passed through middleware chain.

### Attributes

#### `message: SmartMessage`

The SmartMessage being processed.

#### `metadata: dict`

Dictionary for middleware to store/retrieve data. Empty by default.

#### `cancelled: bool`

If True, message processing should stop. Set this to cancel processing.

**Example:**
```python
@manager.use
async def block_spam(ctx, next):
    if is_spam(ctx.message.content):
        ctx.cancelled = True  # Stop processing
        await ctx.message.reply("Message blocked as spam")
        return
    await next()
```

## Built-in Middleware

### logging_middleware

Built-in middleware that logs all message processing.

```python
from discord_bridge.middleware import logging_middleware

manager.use(logging_middleware)
```

### rate_limit_middleware

Limits each user to a certain number of requests per time window.

```python
from discord_bridge.middleware import rate_limit_middleware
from functools import partial

# Allow 5 requests per 60 seconds per user
manager.use(partial(rate_limit_middleware, max_requests=5, window_seconds=60))
```

**Parameters:**
- `ctx`: Middleware context
- `next`: Next middleware in chain
- `max_requests`: Maximum requests allowed per window (default: 5)
- `window_seconds`: Time window in seconds (default: 60)

### dm_only_middleware

Restrict all commands to DMs only.

```python
from discord_bridge.middleware import dm_only_middleware

manager.use(dm_only_middleware)
```

### admin_only_middleware

Restrict commands to admin users only.

```python
from discord_bridge.middleware import admin_only_middleware
from functools import partial

admin_ids = [123456789, 987654321]
manager.use(partial(admin_only_middleware, admin_ids=admin_ids))
```

## Creating Custom Middleware

### Simple Logging

```python
@manager.use
async def log_commands(ctx, next):
    print(f"[{ctx.message.author_name}] {ctx.message.content}")
    await next()
```

### Cancel Processing

```python
@manager.use
async def block_banned_users(ctx, next):
    banned_ids = [111222333]
    if ctx.message.author_id in banned_ids:
        await ctx.message.reply("You are banned from using this bot.")
        ctx.cancelled = True
        return
    await next()
```

### Add Metadata

```python
import time

@manager.use
async def track_requests(ctx, next):
    # Add custom data to context
    ctx.metadata['start_time'] = time.time()
    await next()
    ctx.metadata['end_time'] = time.time()
    duration = ctx.metadata['end_time'] - ctx.metadata['start_time']
    print(f"Request took {duration:.2f}s")
```

## Middleware Chain Order

Middleware executes in registration order:

```python
@manager.use
async def first(ctx, next):
    print("1 - Before")
    await next()
    print("1 - After")

@manager.use
async def second(ctx, next):
    print("2 - Before")
    await next()
    print("2 - After")

# Output:
# 1 - Before
# 2 - Before
# [Command Handler]
# 2 - After
# 1 - After
```

## Complete Example

```python
import asyncio
import time
from discord_bridge import Bridge, CommandRouter, MiddlewareManager, setup_logging

async def main():
    setup_logging()
    bridge = Bridge(config_path="config.yaml")
    router = CommandRouter()
    manager = MiddlewareManager()
    
    # Add logging middleware
    @manager.use
    async def logger(ctx, next):
        start = time.time()
        print(f"[START] {ctx.message.author_name}: {ctx.message.content}")
        await next()
        duration = time.time() - start
        print(f"[END] Took {duration:.2f}s")
    
    # Add rate limiting
    user_requests = {}
    @manager.use
    async def rate_limit(ctx, next):
        user_id = ctx.message.author_id
        now = time.time()
        
        # Clean old requests
        if user_id in user_requests:
            user_requests[user_id] = [t for t in user_requests[user_id] if now - t < 60]
        else:
            user_requests[user_id] = []
        
        # Check limit
        if len(user_requests[user_id]) >= 5:
            await ctx.message.reply("Rate limited! Please wait.")
            ctx.cancelled = True
            return
        
        user_requests[user_id].append(now)
        await next()
    
    @router.command("hello")
    async def hello(message, args):
        await message.reply(f"Hello, {message.author_name}!")
    
    bot_task = asyncio.create_task(bridge.run())
    await bridge.wait_for_ready()
    
    async for message in bridge.listen():
        await manager.execute(message, router.handle)

asyncio.run(main())
```

## See Also

- [User Guide - Middleware](../user-guide/middleware.md)
