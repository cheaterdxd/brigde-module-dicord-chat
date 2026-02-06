import discord
from .exceptions import MessageSendError

class SmartMessage:
    def __init__(self, original_message: discord.Message, prefix: str):
        self._original = original_message
        self.content = original_message.content.removeprefix(prefix).strip()
        self.author_id = original_message.author.id
        self.channel_id = original_message.channel.id

    async def reply(self, text: str):
        """
        Sends a reply to the channel the message came from.
        Automatically handles message splitting and wraps exceptions.
        """
        try:
            if len(text) <= 2000:
                await self._original.channel.send(text)
            else:
                # Split the message into chunks of 2000 characters
                for i in range(0, len(text), 2000):
                    chunk = text[i:i+2000]
                    await self._original.channel.send(chunk)
        except discord.HTTPException as e:
            # Catch potential discord.py errors and wrap them in our custom exception
            raise MessageSendError(f"Failed to send message: {e.status} {e.text}") from e