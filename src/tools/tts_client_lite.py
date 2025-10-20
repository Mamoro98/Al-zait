"""Lightweight Text-to-Speech client for Railway deployment (under 4GB limit)."""

import os
import tempfile
from pathlib import Path
from typing import Optional
from loguru import logger

class TTSClientLite:
    """Lightweight Text-to-Speech client using only gTTS (Railway-optimized)."""
    
    def __init__(self):
        """Initialize lightweight TTS client."""
        self.temp_dir = Path("data/audio")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Only check gTTS availability
        self.gtts_available = self._check_gtts()
        
        logger.info(f"Lightweight TTS Client initialized - gTTS: {self.gtts_available} (Railway-optimized)")
    
    def _check_gtts(self) -> bool:
        """Check if gTTS is available."""
        try:
            from gtts import gTTS
            return True
        except ImportError:
            logger.warning("gTTS not available. Install with: pip install gTTS")
            return False
    
    def create_audio_brief(self, text: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Convert text to audio file using gTTS only.
        
        Args:
            text: Arabic text to convert to speech
            filename: Optional filename (will generate if not provided)
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not self.gtts_available:
            logger.warning("gTTS not available for audio generation")
            return None
            
        if not text or not text.strip():
            logger.error("No text provided for TTS conversion")
            return None
        
        # Generate filename if not provided
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"al_zait_audio_{timestamp}.mp3"
        
        # Ensure .mp3 extension
        if not filename.endswith('.mp3'):
            filename += '.mp3'
            
        output_path = self.temp_dir / filename
        
        try:
            from gtts import gTTS
            
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            if not clean_text:
                logger.error("No valid text after cleaning for TTS")
                return None
            
            # Create TTS object with Arabic language
            logger.info("Creating Arabic audio with lightweight gTTS...")
            tts = gTTS(
                text=clean_text,
                lang='ar',  # Arabic language
                slow=False,  # Normal speed
                tld='com'    # Use google.com
            )
            
            # Save to file
            tts.save(str(output_path))
            
            # Verify file was created and has content
            if output_path.exists() and output_path.stat().st_size > 1000:  # At least 1KB
                logger.info(f"Lightweight audio created: {output_path} ({output_path.stat().st_size} bytes)")
                return str(output_path)
            else:
                logger.error("gTTS created empty or invalid audio file")
                return None
                
        except Exception as e:
            logger.error(f"Lightweight TTS error: {e}")
            return None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS pronunciation."""
        import re
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        text = re.sub(r'_(.*?)_', r'\1', text)        # Underline
        
        # Remove emojis and special characters
        text = re.sub(r'[🎯🚀📰📊🔍📱🏛️📈🛡️🤝🎭⚽🏥📢🧠💎⭐✅❌]', '', text)
        text = re.sub(r'[•·]', '', text)  # Bullet points
        text = re.sub(r'---+', 'فاصل', text)  # Horizontal lines
        
        # Convert some symbols to Arabic words
        text = text.replace('#', 'هاشتاج ')
        text = text.replace('@', 'آت ')
        text = text.replace('&', ' و ')
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        # Limit length for TTS (gTTS has limits)
        if len(text) > 4000:  # gTTS limit is around 5000 chars
            logger.warning(f"Text too long for TTS ({len(text)} chars), truncating...")
            text = text[:4000] + "... يمكنكم قراءة باقي الأخبار في النص المكتوب."
        
        return text.strip()
    
    def create_simple_audio(self, digest_text: str) -> Optional[str]:
        """Create simple audio without intro/outro (Railway-optimized)."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"al_zait_simple_{timestamp}.mp3"
        
        # Add simple intro to the text
        enhanced_text = f"بسم الله الرحمن الرحيم. الموجز الإخباري من وكالة الزيت للأنباء. {digest_text}. شكراً لاستماعكم."
        
        return self.create_audio_brief(enhanced_text, filename)
    
    def get_audio_info(self, audio_path: str) -> dict:
        """Get basic information about an audio file (simplified version)."""
        try:
            if not os.path.exists(audio_path):
                return {}
            
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            
            # Estimate duration based on file size (rough approximation)
            # gTTS typically produces ~1MB per minute of Arabic speech
            estimated_duration_minutes = file_size_mb
            
            return {
                'duration_minutes': estimated_duration_minutes,
                'file_size_mb': file_size_mb,
                'format': 'MP3',
                'method': 'gTTS_lightweight'
            }
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            return {}
    
    def cleanup_old_audio(self, days_to_keep: int = 3):
        """Clean up old audio files (more frequent for Railway optimization)."""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cleaned_count = 0
            
            for audio_file in self.temp_dir.glob("*.mp3"):
                if audio_file.stat().st_mtime < cutoff_date.timestamp():
                    audio_file.unlink()
                    cleaned_count += 1
                    logger.debug(f"Cleaned up old audio: {audio_file}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old audio files (Railway optimization)")
                
        except Exception as e:
            logger.error(f"Error cleaning up old audio files: {e}")
    
    def test_tts_connection(self) -> dict:
        """Test lightweight TTS functionality."""
        results = {'gtts': False}
        
        if not self.gtts_available:
            return results
        
        test_text = "مرحباً، هذا اختبار للتحويل من النص إلى الكلام للنشر على ريلواي"
        
        try:
            test_path = self.create_audio_brief(test_text, "test_lightweight.mp3")
            if test_path and os.path.exists(test_path):
                results['gtts'] = True
                os.remove(test_path)  # Cleanup test file
                logger.info("Lightweight TTS test successful")
        except Exception as e:
            logger.error(f"Lightweight TTS test failed: {e}")
        
        return results
