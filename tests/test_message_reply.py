import pytest
from unittest.mock import Mock, AsyncMock, patch
from discord_bridge import SmartMessage, MessageSendError
import discord

pytestmark = pytest.mark.asyncio

@pytest.fixture
def smart_message():
    """Provides a SmartMessage instance with a mocked original message."""
    mock_discord_msg = Mock()
    # AsyncMock is needed for async methods like 'send'
    mock_discord_msg.channel.send = AsyncMock() 
    
    # Attach the mock to the message object itself for reply testing
    mock_discord_msg.reply = AsyncMock()
    
    return SmartMessage(mock_discord_msg, "!")

async def test_reply_sends_short_message(smart_message):
    reply_text = "This is a short reply."
    await smart_message.reply(reply_text)

    # Check that the underlying channel.send was called once with the correct text
    smart_message._original.channel.send.assert_called_once_with(reply_text)

async def test_reply_splits_long_message(smart_message):
    # Create a long text (e.g., 2001 chars)
    long_text = "a" * 2001
    
    await smart_message.reply(long_text)

    # We expect it to be split into two chunks
    assert smart_message._original.channel.send.call_count == 2
    
    # Check the content of each call
    first_call_args = smart_message._original.channel.send.call_args_list[0].args
    second_call_args = smart_message._original.channel.send.call_args_list[1].args

    assert len(first_call_args[0]) == 2000
    assert first_call_args[0] == "a" * 2000
    
    assert len(second_call_args[0]) == 1
    assert second_call_args[0] == "a"

async def test_reply_wraps_discord_exception(smart_message):
    # Configure the mock to raise a discord.py specific error
    smart_message._original.channel.send.side_effect = discord.Forbidden(
        Mock(), "Missing Permissions"
    )

    with pytest.raises(MessageSendError, match="Failed to send message"):
        await smart_message.reply("This will fail.")
