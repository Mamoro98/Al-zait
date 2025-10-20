"""Telegram bot client for Al Zait News Agent."""

import asyncio
import os
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from src.utils.config import Config

class TelegramClient:
    """Telegram bot client for sending news briefs."""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """Initialize the Telegram client."""
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or Config.TELEGRAM_CHAT_ID
        self.bot = None
        
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
        else:
            logger.error("No Telegram bot token provided")
    
    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send a message to the configured chat."""
        if not self.bot or not self.chat_id:
            logger.error("Telegram bot or chat ID not configured")
            return False
        
        try:
            # Split long messages if needed (Telegram has a 4096 character limit)
            if len(message) > 4000:
                await self.send_long_message(message, parse_mode)
            else:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=parse_mode
                )
            
            logger.info(f"Successfully sent message to chat {self.chat_id}")
            return True
        
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    async def send_long_message(self, message: str, parse_mode: str = 'HTML'):
        """Send a long message by splitting it into chunks."""
        # Split message into chunks of 4000 characters
        chunks = []
        current_chunk = ""
        
        lines = message.split('\n')
        
        for line in lines:
            if len(current_chunk) + len(line) + 1 > 4000:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = line
                else:
                    # If single line is too long, split it
                    while len(line) > 4000:
                        chunks.append(line[:4000])
                        line = line[4000:]
                    current_chunk = line
            else:
                current_chunk += '\n' + line if current_chunk else line
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # Send each chunk
        for i, chunk in enumerate(chunks):
            if i > 0:
                # Add continuation indicator
                chunk = f"📰 (المتابعة {i+1})\n\n" + chunk
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=chunk,
                parse_mode=parse_mode
            )
            
            # Small delay between messages
            await asyncio.sleep(1)
    
    def send_message_sync(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Synchronous wrapper for sending messages."""
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                # Create new event loop if none exists or is closed
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async function
            result = loop.run_until_complete(self.send_message(message, parse_mode))
            return result
        except Exception as e:
            logger.error(f"Error in sync message send: {e}")
            # Try alternative sync approach
            try:
                import requests
                return self._send_message_requests(message, parse_mode)
            except Exception as e2:
                logger.error(f"Fallback send also failed: {e2}")
                return False
    
    async def send_formatted_brief(self, brief: str, title: str = "موجز الزيت الإخباري") -> bool:
        """Send a formatted news brief with proper HTML formatting."""
        # Format the message with HTML
        formatted_message = f"""
<b>🗞️ {title}</b>
<i>📅 {self._get_arabic_date()}</i>

{brief}

<i>📡 وكالة الزيت للأنباء</i>
<i>🤖 تقرير آلي مدعوم بالذكاء الاصطناعي</i>
        """.strip()
        
        return await self.send_message(formatted_message, parse_mode='HTML')
    
    def send_formatted_brief_sync(self, brief: str, title: str = "موجز الزيت الإخباري") -> bool:
        """Synchronous wrapper for sending formatted brief."""
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                # Create new event loop if none exists or is closed
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.send_formatted_brief(brief, title))
            return result
        except Exception as e:
            logger.error(f"Error in sync brief send: {e}")
            # Try direct approach
            try:
                formatted_message = f"""<b>🗞️ {title}</b>
<i>📅 {self._get_arabic_date()}</i>

{brief}

<i>📡 وكالة الزيت للأنباء</i>
<i>🤖 تقرير آلي مدعوم بالذكاء الاصطناعي</i>"""
                return self._send_message_requests(formatted_message, 'HTML')
            except Exception as e2:
                logger.error(f"Fallback brief send failed: {e2}")
                return False
    
    def _get_arabic_date(self) -> str:
        """Get current date in Arabic format."""
        from datetime import datetime
        import locale
        
        try:
            # Arabic month names
            arabic_months = [
                "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
            ]
            
            now = datetime.now()
            arabic_month = arabic_months[now.month - 1]
            
            return f"{now.day} {arabic_month} {now.year}"
        
        except Exception:
            # Fallback to English date
            return datetime.now().strftime("%Y-%m-%d")
    
    async def test_connection(self) -> bool:
        """Test the Telegram bot connection."""
        if not self.bot:
            logger.error("Bot not initialized")
            return False
        
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Bot connection successful. Bot: {bot_info.username}")
            return True
        
        except Exception as e:
            logger.error(f"Bot connection test failed: {e}")
            return False
    
    def test_connection_sync(self) -> bool:
        """Synchronous wrapper for testing connection."""
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                # Create new event loop if none exists or is closed
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.test_connection())
            return result
        except Exception as e:
            logger.error(f"Error in sync connection test: {e}")
            return False
    
    def _send_message_requests(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Fallback method using requests library instead of async."""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully via requests fallback")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Requests fallback failed: {e}")
            return False
    
    async def send_audio_file(self, audio_path: str, caption: str = "") -> bool:
        """Send audio file to Telegram channel."""
        if not self.bot:
            logger.error("Bot not initialized")
            return False
        
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return False
        
        try:
            with open(audio_path, 'rb') as audio_file:
                await self.bot.send_audio(
                    chat_id=Config.TELEGRAM_CHAT_ID,
                    audio=audio_file,
                    caption=caption,
                    parse_mode='HTML'
                )
            logger.info(f"Audio file sent successfully: {audio_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send audio file: {e}")
            return False
    
    def send_audio_file_sync(self, audio_path: str, caption: str = "") -> bool:
        """Synchronous wrapper for sending audio files."""
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.send_audio_file(audio_path, caption))
            return result
        except Exception as e:
            logger.error(f"Error in sync audio send: {e}")
            return False
