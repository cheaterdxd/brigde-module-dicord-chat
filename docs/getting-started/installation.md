# Installation

## Prerequisites

- Python 3.8 or higher
- A Discord account
- A Discord bot token

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/discord-bridge-module.git
cd discord-bridge-module
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `discord.py>=2.0.0` - Discord API wrapper
- `PyYAML>=6.0` - YAML configuration parsing
- `pydantic>=2.0.0` - Configuration validation

## Step 4: Install Development Dependencies (Optional)

For running tests:

```bash
pip install pytest pytest-asyncio
```

For documentation:

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
```

## Verify Installation

Test the installation:

```python
from discord_bridge import Bridge
print("Installation successful!")
```

## Next Steps

- [Configuration](configuration.md) - Set up your bot token
- [Quick Start](quickstart.md) - Build your first bot
