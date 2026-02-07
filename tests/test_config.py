import pytest
from pathlib import Path
import yaml
from discord_bridge.config import load_config, BridgeConfig
from discord_bridge.exceptions import ConfigurationError


def test_load_config_success(tmp_path: Path):
    """Test loading a valid configuration file."""
    config_content = {
        "discord_token": "test_token_12345",
        "command_prefix": "!",
        "allowed_channel_ids": [],
        "max_reconnect_attempts": 5,
        "reconnect_base_delay": 1.0
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    token, prefix, channels, max_retries, delay = load_config(config_file)
    assert token == "test_token_12345"
    assert prefix == "!"
    assert channels == []
    assert max_retries == 5
    assert delay == 1.0


def test_load_config_with_channels(tmp_path: Path):
    """Test loading config with whitelisted channels."""
    config_content = {
        "discord_token": "test_token_12345",
        "command_prefix": "?",
        "allowed_channel_ids": ["123456789", "987654321"],
        "max_reconnect_attempts": 3,
        "reconnect_base_delay": 2.0
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    token, prefix, channels, max_retries, delay = load_config(config_file)
    assert token == "test_token_12345"
    assert prefix == "?"
    assert channels == [123456789, 987654321]
    assert max_retries == 3
    assert delay == 2.0


def test_load_config_missing_token_raises_error(tmp_path: Path):
    """Test that missing token raises ConfigurationError."""
    config_content = {"command_prefix": "!"}
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)
    
    with pytest.raises(ConfigurationError, match="discord_token"):
        load_config(config_file)


def test_load_config_placeholder_token_raises_error(tmp_path: Path):
    """Test that placeholder token raises ConfigurationError."""
    config_content = {"discord_token": "YOUR_DISCORD_BOT_TOKEN_HERE"}
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)
    
    with pytest.raises(ConfigurationError, match="placeholder"):
        load_config(config_file)


def test_load_config_file_not_found():
    """Test that missing file raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="not found"):
        load_config(Path("/nonexistent/path/config.yaml"))


def test_bridge_config_defaults():
    """Test that BridgeConfig has correct defaults."""
    config = BridgeConfig(discord_token="valid_token")
    assert config.command_prefix == "!"
    assert config.allowed_channel_ids == []
    assert config.max_reconnect_attempts == 5
    assert config.reconnect_base_delay == 1.0
