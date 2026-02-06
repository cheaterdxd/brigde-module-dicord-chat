# Discord Bridge Module Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create an easy-to-use, reliable Python library for two-way communication with Discord.

**Architecture:** A `Bridge` class will wrap `discord.py`, providing a simplified API with an async iterator for receiving commands and a convenient `.reply()` method on message objects.

**Tech Stack:** Python 3.9+, `discord.py`, `PyYAML`, `asyncio`

---

### Task 1: Project Scaffolding and Dependencies

**Files:**
- Create: `discord_bridge/`
- Create: `tests/`
- Create: `docs/`
- Create: `requirements.txt`
- Create: `discord_bridge/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create project directories**
Run: `mkdir discord_bridge tests docs`

**Step 2: Create `requirements.txt`**
Content for `requirements.txt`:
```
discord.py>=2.0.0
PyYAML>=6.0
```

**Step 3: Create initial package structure**
Run: `New-Item discord_bridge/__init__.py -ItemType File; New-Item tests/__init__.py -ItemType File`

**Step 4: Commit**
```bash
git init
git add .
git commit -m "Initial project structure and dependencies"
```

---

### Task 2: Configuration and Custom Exceptions

**Files:**
- Create: `discord_bridge/exceptions.py`
- Create: `discord_bridge/config.py`
- Create: `tests/test_config.py`

**Step 1: Write failing test for config loading**
In `tests/test_config.py`:
```python
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
```

**Step 2: Create Exception and Config modules**
In `discord_bridge/exceptions.py`:
```python
class BridgeException(Exception):
    """Base exception for the bridge library."""
    pass

class ConfigurationError(BridgeException):
    """Raised for configuration-related errors."""
    pass
```
In `discord_bridge/config.py`:
```python
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
```

**Step 3: Run tests to verify**
Run: `pytest tests/test_config.py -v`
Expected: 2 PASS

**Step 4: Commit**
```bash
git add .
git commit -m "feat: Add configuration loading and custom exceptions"
```

---

### Task 3: Core `Bridge` and `SmartMessage` Classes

**Files:**
- Create: `discord_bridge/message.py`
- Create: `discord_bridge/bridge.py`
- Modify: `discord_bridge/__init__.py`
- Create: `tests/test_core_classes.py`

**Step 1: Write tests for basic class structure**
In `tests/test_core_classes.py`:
```python
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
```

**Step 2: Implement the classes**
In `discord_bridge/message.py`:
```python
import discord

class SmartMessage:
    def __init__(self, original_message: discord.Message, prefix: str):
        self._original = original_message
        self.content = original_message.content.removeprefix(prefix).strip()
        self.author_id = original_message.author.id
        self.channel_id = original_message.channel.id
```
In `discord_bridge/bridge.py`:
```python
import asyncio
import discord

class Bridge:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.is_ready = False
        self._client = discord.Client(intents=discord.Intents.default())
        # More to come...
```
In `discord_bridge/__init__.py`:
```python
from .bridge import Bridge
from .exceptions import *
```

**Step 3: Run tests to verify**
Run: `pytest tests/test_core_classes.py -v`
Expected: 2 PASS

**Step 4: Commit**
```bash
git add .
git commit -m "feat: Implement core Bridge and SmartMessage classes"
```

---
### Task 4: Full Implementation Plan

The full plan is extensive. The subsequent tasks would involve:
- Implementing the `async` logic for `listen()` using an `asyncio.Queue`.
- Wiring up the `on_message` and `on_ready` events from `discord.py`.
- Implementing the `.reply()` method with message-splitting logic.
- Writing tests for each of these features, likely involving mocking the `discord.py` objects.
- Creating the final `main.py` example and a `README.md`.

This abbreviated plan covers the initial, critical TDD cycles.
