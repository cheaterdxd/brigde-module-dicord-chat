import asyncio
from unittest.mock import Mock, patch

import pytest
from discord_bridge import Bridge, SmartMessage

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

# By patching 'load_config' at the module level, all tests in this file
# will use the mock instead of the real function, avoiding the FileNotFoundError.
@pytest.fixture(autouse=True)
def mock_config_load():
    with patch("discord_bridge.bridge.load_config") as mock_load:
        # Provide a dummy token and prefix for all tests
        mock_load.return_value = ("dummy_token", "!")
        yield mock_load

async def test_listen_yields_message_from_queue():
    bridge = Bridge("config.yaml")
    # Manually create the queue for the test
    bridge._incoming_queue = asyncio.Queue()

    # Create a mock discord.Message and wrap it
    mock_discord_msg = Mock()
    mock_discord_msg.content = "!test"
    mock_discord_msg.author.id = 123
    mock_discord_msg.channel.id = 456
    smart_msg = SmartMessage(mock_discord_msg, "!")

    # Put the message into the queue
    await bridge._incoming_queue.put(smart_msg)

    # Listen for the message
    async def listen_and_check():
        async for received_message in bridge.listen():
            assert received_message is smart_msg
            break # Exit after one message
    
    # Run the listener with a timeout
    await asyncio.wait_for(listen_and_check(), timeout=1.0)

async def test_on_message_handler_puts_to_queue():
    bridge = Bridge("config.yaml")
    bridge.is_ready = True # Pretend the bot is ready
    # The prefix is now set by the mock_config_load fixture
    # bridge.prefix = "!" 
    bridge.bot_user_id = 999 # Set a fake bot id
    bridge._incoming_queue = asyncio.Queue()

    # Create a message from a user
    user_msg = Mock()
    user_msg.author.id = 123
    user_msg.content = "!hello"

    # Simulate the on_message event
    await bridge._handle_on_message(user_msg)
    
    # Check that the message arrived in the queue
    received = await asyncio.wait_for(bridge._incoming_queue.get(), timeout=1.0)
    assert isinstance(received, SmartMessage)
    assert received.content == "hello"

async def test_on_message_handler_ignores_self():
    bridge = Bridge("config.yaml")
    bridge.is_ready = True
    bridge.bot_user_id = 123 # Bot's own ID
    bridge._incoming_queue = asyncio.Queue()

    # Create a message from the bot itself
    bot_msg = Mock()
    bot_msg.author.id = 123 
    bot_msg.content = "!hello"

    # Simulate the event and assert the queue remains empty
    await bridge._handle_on_message(bot_msg)
    assert bridge._incoming_queue.empty()

async def test_on_message_handler_ignores_no_prefix():
    bridge = Bridge("config.yaml")
    bridge.is_ready = True
    bridge.bot_user_id = 999
    bridge._incoming_queue = asyncio.Queue()

    # Create a message without the prefix
    no_prefix_msg = Mock()
    no_prefix_msg.author.id = 123
    no_prefix_msg.content = "hello world"

    # Simulate the event and assert the queue remains empty
    await bridge._handle_on_message(no_prefix_msg)
    assert bridge._incoming_queue.empty()