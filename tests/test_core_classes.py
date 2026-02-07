from unittest.mock import Mock
from discord_bridge.message import SmartMessage
from discord_bridge.bridge import Bridge


def test_smart_message_properties():
    """Test that SmartMessage extracts properties correctly."""
    mock_discord_msg = Mock()
    mock_discord_msg.content = "!hello world"
    mock_discord_msg.author.id = 123
    mock_discord_msg.author.display_name = "TestUser"
    mock_discord_msg.channel.id = 456
    mock_discord_msg.channel.__class__ = Mock()
    
    smart_msg = SmartMessage(mock_discord_msg, "!")
    
    assert smart_msg.content == "hello world"
    assert smart_msg.author_id == 123
    assert smart_msg.author_name == "TestUser"
    assert smart_msg.channel_id == 456


def test_bridge_initialization():
    """Test that Bridge initializes with correct default values."""
    bridge = Bridge("path/to/config.yaml")
    assert bridge.config_path == "path/to/config.yaml"
    assert not bridge.is_ready
    assert bridge.bot_user_id is None
