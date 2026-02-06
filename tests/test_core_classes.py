from unittest.mock import Mock
from discord_bridge.message import SmartMessage
from discord_bridge.bridge import Bridge

def test_smart_message_properties():
    mock_discord_msg = Mock()
    mock_discord_msg.content = "!hello world"
    mock_discord_msg.author.id = 123
    mock_discord_msg.channel.id = 456
    
    # Assume prefix is '!'
    smart_msg = SmartMessage(mock_discord_msg, "!")
    
    assert smart_msg.content == "hello world"
    assert smart_msg.author_id == 123
    assert smart_msg.channel_id == 456

def test_bridge_initialization():
    # This is a simple test to ensure the class can be instantiated
    bridge = Bridge("path/to/config.yaml")
    assert bridge.config_path == "path/to/config.yaml"
    assert not bridge.is_ready
