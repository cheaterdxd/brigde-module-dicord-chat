import discord

class SmartMessage:
    def __init__(self, original_message: discord.Message, prefix: str):
        self._original = original_message
        self.content = original_message.content.removeprefix(prefix).strip()
        self.author_id = original_message.author.id
        self.channel_id = original_message.channel.id
