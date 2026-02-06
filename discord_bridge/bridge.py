import asyncio
import discord

class Bridge:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.is_ready = False
        self._client = discord.Client(intents=discord.Intents.default())
        # More to come...
