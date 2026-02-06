from pathlib import Path
import yaml
from .exceptions import ConfigurationError

def load_config(path: Path):
    # This will fail the second test initially
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    
    token = config.get("discord_token")
    if not token:
        raise ConfigurationError("discord_token not found in config file.")
        
    prefix = config.get("command_prefix", "!") # Default prefix
    return token, prefix