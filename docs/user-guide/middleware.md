# Middleware

Middleware allows you to intercept and process messages before they reach command handlers.

## Basic Concept

Middleware functions form a chain. Each middleware can:
- Execute code before the command
- Execute code after the command
- Cancel message processing
- Add metadata to the context

## Creating Middleware

```python
from discord_bridge import MiddlewareManager

manager = MiddlewareManager()

@manager.use
async def logging_middleware(ctx, next):
    print(f"Processing: {ctx.message.content}")
    await next()  # Continue to next middleware/handler
    print(f"Completed: {ctx.message.content}")
```

## Built-in Middleware

### Logging Middleware

```python
from discord_bridge.middleware import logging_middleware

manager.use(logging_middleware)
```

### Rate Limiting Middleware

```python
from discord_bridge.middleware import rate_limit_middleware
from functools import partial

# Allow 5 requests per 60 seconds per user
manager.use(partial(rate_limit_middleware, max_requests=5, window_seconds=60))
```

### DM-Only Middleware

```python
from discord_bridge.middleware import dm_only_middleware

# Restrict all commands to DMs only
manager.use(dm_only_middleware)
```

### Admin-Only Middleware

```python
from discord_bridge.middleware import admin_only_middleware
from functools import partial

admin_ids = [123456789, 987654321]
manager.use(partial(admin_only_middleware, admin_ids=admin_ids))
```

## Custom Middleware

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
        ctx.cancelled = True  # Stop processing
        return
    await next()
```

### Add Metadata

```python
@manager.use
async def track_requests(ctx, next):
    # Add custom data to context
    ctx.metadata['start_time'] = time.time()
    await next()
    ctx.metadata['end_time'] = time.time()
    duration = ctx.metadata['end_time'] - ctx.metadata['start_time']
    print(f"Request took {duration:.2f}s")
```

## Using Middleware with Router

```python
from discord_bridge import Bridge, CommandRouter, MiddlewareManager

bridge = Bridge(config_path="config.yaml")
router = CommandRouter()
manager = MiddlewareManager()

# Register middleware
@manager.use
async def log_middleware(ctx, next):
    print(f"Command: {ctx.message.content}")
    await next()

# Register commands
@router.command("hello")
async def hello(message, args):
    await message.reply("Hello!")

# In main loop, use middleware
async for message in bridge.listen():
    await manager.execute(message, router.handle)
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

## Managing Middleware

```python
# Remove specific middleware
manager.remove(my_middleware)

# Remove all middleware
manager.clear()

# Check if message was handled
was_handled = await manager.execute(message, handler)
if not was_handled:
    print("Message was cancelled by middleware")
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
