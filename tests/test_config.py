import yaml
import pytest
from pathlib import Path
from discord_bridge.config import load_config
from discord_bridge.exceptions import ConfigurationError

def test_load_config_success(tmp_path: Path):
    config_content = {
        "discord_token": "test_token",
        "command_prefix": "!",
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    token, prefix = load_config(config_file)
    assert token == "test_token"
    assert prefix == "!"

def test_load_config_missing_token_raises_error(tmp_path: Path):
    config_content = {"command_prefix": "!"}
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)
    
    with pytest.raises(ConfigurationError, match="discord_token not found"):
        load_config(config_file)