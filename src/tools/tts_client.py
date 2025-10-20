"""Text-to-Speech client for Al Zait News Agent supporting multiple TTS providers."""

import os
import tempfile
from pathlib import Path
from typing import Optional, Union
from loguru import logger
from src.utils.config import Config

class TTSClient:
    """Text-to-Speech client with multiple provider support."""
    
    def __init__(self):
        """Initialize TTS client."""
        self.temp_dir = Path("data/audio")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize providers
        self.gtts_available = self._check_gtts()
        # Future: Add other providers (OpenAI, ElevenLabs, Azure)
        
        logger.info(f"TTS Client initialized - gTTS: {self.gtts_available}")
    
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
        Convert text to audio file.
        
        Args:
            text: Arabic text to convert to speech
            filename: Optional filename (will generate if not provided)
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not text or not text.strip():
            logger.error("No text provided for TTS conversion")
            return None
        
        # Generate filename if not provided
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"al_zait_digest_{timestamp}.mp3"
        
        # Ensure .mp3 extension
        if not filename.endswith('.mp3'):
            filename += '.mp3'
            
        output_path = self.temp_dir / filename
        
        # Try different TTS providers in order of preference
        audio_path = self._create_with_gtts(text, output_path)
        
        if audio_path and os.path.exists(audio_path):
            logger.info(f"Audio brief created successfully: {audio_path}")
            return str(audio_path)
        else:
            logger.error("Failed to create audio brief with all available providers")
            return None
    
    def _create_with_gtts(self, text: str, output_path: Path) -> Optional[str]:
        """Create audio using Google Text-to-Speech."""
        if not self.gtts_available:
            return None
            
        try:
            from gtts import gTTS
            
            # Clean text for TTS (remove markdown, emojis, etc.)
            clean_text = self._clean_text_for_tts(text)
            
            if not clean_text:
                logger.error("No valid text after cleaning for TTS")
                return None
            
            # Create TTS object with Arabic language
            logger.info("Creating Arabic audio with gTTS...")
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
                logger.info(f"gTTS audio created: {output_path} ({output_path.stat().st_size} bytes)")
                return str(output_path)
            else:
                logger.error("gTTS created empty or invalid audio file")
                return None
                
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS pronunciation."""
        import re
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        text = re.sub(r'_(.*?)_', r'\1', text)        # Underline
        
        # Remove emojis and special characters that TTS can't handle well
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
    
    def create_intro_outro(self) -> tuple[Optional[str], Optional[str]]:
        """Create intro and outro audio clips for the podcast."""
        intro_text = """بسم الله الرحمن الرحيم
        مرحباً بكم في الموجز الصباحي لأخبار السودان
        من وكالة الزيت للأنباء
        إعداد الذكاء الاصطناعي"""
        
        outro_text = """شكراً لاستماعكم للموجز الصباحي
        وكالة الزيت للأنباء
        نراقب الأخبار على مدار الساعة
        السلام عليكم ورحمة الله وبركاته"""
        
        intro_path = self.create_audio_brief(intro_text, "intro.mp3")
        outro_path = self.create_audio_brief(outro_text, "outro.mp3")
        
        return intro_path, outro_path
    
    def combine_audio_segments(self, intro_path: str, content_path: str, 
                             outro_path: str, output_filename: str) -> Optional[str]:
        """Combine intro, content, and outro into final podcast."""
        try:
            from pydub import AudioSegment
            
            # Load audio segments
            intro = AudioSegment.from_mp3(intro_path) if intro_path else AudioSegment.empty()
            content = AudioSegment.from_mp3(content_path)
            outro = AudioSegment.from_mp3(outro_path) if outro_path else AudioSegment.empty()
            
            # Add short pauses between segments
            pause = AudioSegment.silent(duration=1000)  # 1 second pause
            
            # Combine segments
            final_audio = intro + pause + content + pause + outro
            
            # Export final podcast
            output_path = self.temp_dir / output_filename
            final_audio.export(str(output_path), format="mp3", bitrate="128k")
            
            if output_path.exists():
                duration = len(final_audio) / 1000  # Duration in seconds
                logger.info(f"Final podcast created: {output_path} (Duration: {duration:.1f}s)")
                return str(output_path)
            
        except ImportError:
            logger.warning("pydub not available for audio combination")
            return content_path  # Return content only
        except Exception as e:
            logger.error(f"Error combining audio segments: {e}")
            return content_path  # Return content only
        
        return None
    
    def create_full_podcast(self, digest_text: str) -> Optional[str]:
        """Create complete podcast with intro, content, and outro."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create main content audio
        content_filename = f"content_{timestamp}.mp3"
        content_path = self.create_audio_brief(digest_text, content_filename)
        
        if not content_path:
            logger.error("Failed to create main content audio")
            return None
        
        # Create intro and outro
        intro_path, outro_path = self.create_intro_outro()
        
        # Combine all segments
        final_filename = f"al_zait_podcast_{timestamp}.mp3"
        podcast_path = self.combine_audio_segments(
            intro_path, content_path, outro_path, final_filename
        )
        
        # Cleanup individual segments
        try:
            for path in [intro_path, outro_path, content_path]:
                if path and os.path.exists(path) and path != podcast_path:
                    os.remove(path)
                    logger.debug(f"Cleaned up temporary audio: {path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary audio files: {e}")
        
        return podcast_path
    
    def get_audio_info(self, audio_path: str) -> dict:
        """Get information about an audio file."""
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_mp3(audio_path)
            
            return {
                'duration_seconds': len(audio) / 1000,
                'duration_minutes': len(audio) / 60000,
                'file_size_mb': os.path.getsize(audio_path) / (1024 * 1024),
                'sample_rate': audio.frame_rate,
                'channels': audio.channels
            }
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            return {}
    
    def cleanup_old_audio(self, days_to_keep: int = 7):
        """Clean up old audio files."""
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
                logger.info(f"Cleaned up {cleaned_count} old audio files")
                
        except Exception as e:
            logger.error(f"Error cleaning up old audio files: {e}")
    
    def test_tts_connection(self) -> dict:
        """Test TTS functionality with all available providers."""
        results = {'gtts': False}
        
        test_text = "مرحباً، هذا اختبار للتحويل من النص إلى الكلام"
        
        # Test gTTS
        if self.gtts_available:
            try:
                test_path = self.create_audio_brief(test_text, "test_gtts.mp3")
                if test_path and os.path.exists(test_path):
                    results['gtts'] = True
                    os.remove(test_path)  # Cleanup test file
            except Exception as e:
                logger.error(f"gTTS test failed: {e}")
        
        logger.info(f"TTS test results: {results}")
        return results
