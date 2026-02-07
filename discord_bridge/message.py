import asyncio
import discord
from .exceptions import MessageSendError
from .logger import get_logger

logger = get_logger(__name__)


class SmartMessage:
    """A wrapper around Discord messages with convenient reply functionality.
    
    This class provides a simplified interface for accessing message content
    and sending replies. It automatically handles long message splitting
    and respects Discord's rate limits.
    
    Attributes:
        content: The message content without the command prefix
        author_id: The Discord ID of the message author
        author_name: The display name of the message author
        channel_id: The Discord ID of the channel where the message was sent
        is_dm: Whether the message was sent in a DM (direct message)
    
    Example:
        >>> async for message in bridge.listen():
        ...     print(f"{message.author_name} said: {message.content}")
        ...     await message.reply("Thanks for your message!")
    """
    
    # Discord rate limit: ~5 messages per 5 seconds per channel
    # We use 1.2 second delay to be safe
    CHUNK_DELAY: float = 1.2
    MAX_MESSAGE_LENGTH: int = 2000
    
    def __init__(self, original_message: discord.Message, prefix: str) -> None:
        """Initialize SmartMessage from a Discord message.
        
        Args:
            original_message: The raw Discord message object
            prefix: The command prefix to strip from content
        """
        self._original: discord.Message = original_message
        self.content: str = original_message.content.removeprefix(prefix).strip()
        self.author_id: int = original_message.author.id
        self.author_name: str = (
            original_message.author.display_name 
            if hasattr(original_message.author, 'display_name') 
            else str(original_message.author)
        )
        self.channel_id: int = original_message.channel.id
        self.is_dm: bool = isinstance(original_message.channel, discord.DMChannel)
        
        logger.debug(
            f"SmartMessage created: author={self.author_name}, "
            f"content='{self.content[:50]}...', is_dm={self.is_dm}"
        )

    async def reply(self, text: str) -> None:
        """Send a reply to the channel where the message was received.
        
        Automatically splits messages longer than 2000 characters and
        adds delays between chunks to respect Discord's rate limits.
        
        Args:
            text: The text to send as a reply
            
        Raises:
            MessageSendError: If the message fails to send
            
        Example:
            >>> await message.reply("This is my response!")
            >>> # Long messages are automatically split:
            >>> await message.reply("a" * 5000)  # Sends as 3 messages
        """
        try:
            if len(text) <= self.MAX_MESSAGE_LENGTH:
                logger.debug(f"Sending single message ({len(text)} chars)")
                await self._original.channel.send(text)
            else:
                # Split the message into chunks and send with delays
                chunks = self._split_message(text)
                logger.info(
                    f"Message too long ({len(text)} chars), "
                    f"splitting into {len(chunks)} chunks"
                )
                
                for i, chunk in enumerate(chunks):
                    await self._original.channel.send(chunk)
                    logger.debug(f"Sent chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
                    
                    # Add delay between chunks to respect rate limits
                    if i < len(chunks) - 1:
                        logger.debug(f"Waiting {self.CHUNK_DELAY}s before next chunk")
                        await asyncio.sleep(self.CHUNK_DELAY)
                        
        except discord.HTTPException as e:
            logger.error(f"Failed to send message: {e.status} {e.text}")
            raise MessageSendError(f"Failed to send message: {e.status} {e.text}") from e
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            raise MessageSendError(f"Failed to send message: {e}") from e

    def _split_message(self, text: str) -> list[str]:
        """Split text into chunks that fit Discord's message limit.
        
        Args:
            text: The text to split
            
        Returns:
            List of message chunks
        """
        chunks = []
        for i in range(0, len(text), self.MAX_MESSAGE_LENGTH):
            chunk = text[i:i + self.MAX_MESSAGE_LENGTH]
            chunks.append(chunk)
        return chunks

    async def reply_with_file(
        self, 
        content: str | None = None, 
        file_path: str | None = None,
        filename: str | None = None
    ) -> None:
        """Send a reply with an attached file.
        
        Args:
            content: Optional text content to include with the file
            file_path: Path to the file to upload
            filename: Optional custom filename (uses basename if not provided)
            
        Raises:
            MessageSendError: If the file fails to send
            FileNotFoundError: If the file doesn't exist
            
        Example:
            >>> await message.reply_with_file(
            ...     content="Here's your file!",
            ...     file_path="/path/to/document.pdf"
            ... )
        """
        try:
            from pathlib import Path
            
            if file_path and not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file = discord.File(file_path, filename=filename)
            await self._original.channel.send(content=content, file=file)
            logger.debug(f"Sent file reply: {filename or file_path}")
            
        except FileNotFoundError:
            raise
        except discord.HTTPException as e:
            logger.error(f"Failed to send file: {e.status} {e.text}")
            raise MessageSendError(f"Failed to send file: {e.status} {e.text}") from e
        except Exception as e:
            logger.error(f"Unexpected error sending file: {e}")
            raise MessageSendError(f"Failed to send file: {e}") from e

    async def reply_with_embed(
        self,
        title: str | None = None,
        description: str | None = None,
        color: int = 0x3498db,
        fields: list[dict] | None = None,
        footer: str | None = None,
        image_url: str | None = None,
        thumbnail_url: str | None = None
    ) -> None:
        """Send a reply with a Discord embed (rich formatting).
        
        Args:
            title: Embed title
            description: Embed description text
            color: Integer color code (default: blue)
            fields: List of field dicts with 'name', 'value', and optional 'inline' keys
            footer: Footer text
            image_url: URL for main image
            thumbnail_url: URL for thumbnail image
            
        Raises:
            MessageSendError: If the embed fails to send
            
        Example:
            >>> await message.reply_with_embed(
            ...     title="My Response",
            ...     description="Here's some information",
            ...     color=0x00ff00,  # Green
            ...     fields=[
            ...         {"name": "Field 1", "value": "Value 1", "inline": True},
            ...         {"name": "Field 2", "value": "Value 2", "inline": True}
            ...     ],
            ...     footer="Powered by discord_bridge"
            ... )
        """
        try:
            embed = discord.Embed(
                title=title,
                description=description,
                color=color
            )
            
            if fields:
                for field in fields:
                    embed.add_field(
                        name=field.get("name", ""),
                        value=field.get("value", ""),
                        inline=field.get("inline", False)
                    )
            
            if footer:
                embed.set_footer(text=footer)
            
            if image_url:
                embed.set_image(url=image_url)
            
            if thumbnail_url:
                embed.set_thumbnail(url=thumbnail_url)
            
            await self._original.channel.send(embed=embed)
            logger.debug(f"Sent embed reply: title='{title}'")
            
        except discord.HTTPException as e:
            logger.error(f"Failed to send embed: {e.status} {e.text}")
            raise MessageSendError(f"Failed to send embed: {e.status} {e.text}") from e
        except Exception as e:
            logger.error(f"Unexpected error sending embed: {e}")
            raise MessageSendError(f"Failed to send embed: {e}") from e
