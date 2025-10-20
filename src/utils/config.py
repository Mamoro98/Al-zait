"""Configuration management for Al Zait News Agent."""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Al Zait News Agent."""
    
    # API Keys
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Local LLM Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
    
    # Scheduling
    SCHEDULE_HOUR: int = int(os.getenv("SCHEDULE_HOUR", "8"))
    SCHEDULE_MINUTE: int = int(os.getenv("SCHEDULE_MINUTE", "0"))
    
    # Agent Configuration
    MAX_ARTICLES_PER_QUERY: int = int(os.getenv("MAX_ARTICLES_PER_QUERY", "10"))
    SUMMARY_LENGTH_SENTENCES: int = int(os.getenv("SUMMARY_LENGTH_SENTENCES", "3"))
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "800"))  # Max chars per article for LLM
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/news.db")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "data/al_zait.log")
    
    # News Sources
    SEARCH_QUERIES_AR: List[str] = os.getenv(
        "SEARCH_QUERIES_AR", 
        "أخبار السودان اليوم,السياسة السودانية,الاقتصاد السوداني"
    ).split(",")
    
    SEARCH_QUERIES_EN: List[str] = os.getenv(
        "SEARCH_QUERIES_EN",
        "Sudan news today,Sudan political news,Sudan economy news"
    ).split(",")
    
    RSS_FEEDS: List[str] = os.getenv(
        "RSS_FEEDS",
        "https://www.aljazeera.com/xml/rss/all.xml,https://feeds.bbci.co.uk/arabic/rss.xml,http://www.sudantribune.com/spip.php?page=backend"
    ).split(",")
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate that all required configuration values are set."""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if not cls.TELEGRAM_CHAT_ID:
            errors.append("TELEGRAM_CHAT_ID is required")
        
        if not cls.NEWSAPI_KEY:
            errors.append("NEWSAPI_KEY is required")
        
        if not cls.GROQ_API_KEY and not cls.GEMINI_API_KEY:
            errors.append("At least one of GROQ_API_KEY or GEMINI_API_KEY is required for LLM processing")
        
        return errors
    
    @classmethod
    def get_all_search_queries(cls) -> List[str]:
        """Get all search queries (Arabic and English combined)."""
        return cls.SEARCH_QUERIES_AR + cls.SEARCH_QUERIES_EN
