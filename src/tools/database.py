"""Database operations for Al Zait News Agent using SQLite."""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from loguru import logger
from src.utils.config import Config

class NewsDatabase:
    """SQLite database manager for the news agent."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database connection."""
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_database_directory()
        self._initialize_tables()
    
    def _ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable accessing columns by name
        return conn
    
    def _initialize_tables(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            # Table for processed articles
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    language TEXT,
                    summary TEXT
                )
            """)
            
            # Table for execution logs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    articles_fetched INTEGER,
                    articles_processed INTEGER,
                    events_identified INTEGER,
                    success BOOLEAN,
                    error_message TEXT
                )
            """)
            
            # Table for brief history
            conn.execute("""
                CREATE TABLE IF NOT EXISTS brief_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    brief_content TEXT NOT NULL,
                    article_count INTEGER,
                    delivery_status TEXT
                )
            """)
            
            conn.commit()
    
    def is_url_processed(self, url: str) -> bool:
        """Check if a URL has already been processed."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM processed_articles WHERE url = ? LIMIT 1", 
                (url,)
            )
            return cursor.fetchone() is not None
    
    def get_processed_urls(self, days: int = 7) -> List[str]:
        """Get URLs processed in the last N days."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT url FROM processed_articles 
                WHERE processed_at > datetime('now', '-{} days')
            """.format(days))
            return [row[0] for row in cursor.fetchall()]
    
    def mark_articles_processed(self, articles: List[dict]):
        """Mark a list of articles as processed."""
        with self._get_connection() as conn:
            for article in articles:
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO processed_articles 
                        (url, title, source, language, summary)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        article['url'],
                        article['title'],
                        article.get('source', ''),
                        article.get('language', ''),
                        article.get('summary', '')
                    ))
                except sqlite3.Error as e:
                    logger.error(f"Error marking article as processed: {e}")
            conn.commit()
    
    def log_execution(self, stats: dict, success: bool = True, error_message: str = None):
        """Log execution statistics."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO execution_logs 
                (articles_fetched, articles_processed, events_identified, success, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (
                stats.get('articles_fetched', 0),
                stats.get('articles_processed', 0),
                stats.get('events_identified', 0),
                success,
                error_message
            ))
            conn.commit()
    
    def save_brief(self, brief_content: str, article_count: int, delivery_status: str = "pending"):
        """Save a generated brief to the database."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO brief_history (brief_content, article_count, delivery_status)
                VALUES (?, ?, ?)
            """, (brief_content, article_count, delivery_status))
            conn.commit()
            return cursor.lastrowid
    
    def update_brief_delivery_status(self, brief_id: int, status: str):
        """Update the delivery status of a brief."""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE brief_history 
                SET delivery_status = ? 
                WHERE id = ?
            """, (status, brief_id))
            conn.commit()
    
    def get_recent_briefs(self, limit: int = 10) -> List[dict]:
        """Get recent briefs."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM brief_history 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old processed articles and logs."""
        with self._get_connection() as conn:
            # Clean old processed articles
            conn.execute("""
                DELETE FROM processed_articles 
                WHERE processed_at < datetime('now', '-{} days')
            """.format(days_to_keep))
            
            # Clean old execution logs
            conn.execute("""
                DELETE FROM execution_logs 
                WHERE execution_time < datetime('now', '-{} days')
            """.format(days_to_keep))
            
            # Keep brief history longer (90 days)
            conn.execute("""
                DELETE FROM brief_history 
                WHERE created_at < datetime('now', '-90 days')
            """)
            
            conn.commit()
            logger.info(f"Cleaned up database records older than {days_to_keep} days")
    
    def get_statistics(self) -> dict:
        """Get database statistics."""
        with self._get_connection() as conn:
            stats = {}
            
            # Total processed articles
            cursor = conn.execute("SELECT COUNT(*) FROM processed_articles")
            stats['total_articles'] = cursor.fetchone()[0]
            
            # Articles this week
            cursor = conn.execute("""
                SELECT COUNT(*) FROM processed_articles 
                WHERE processed_at > datetime('now', '-7 days')
            """)
            stats['articles_this_week'] = cursor.fetchone()[0]
            
            # Total executions
            cursor = conn.execute("SELECT COUNT(*) FROM execution_logs")
            stats['total_executions'] = cursor.fetchone()[0]
            
            # Success rate
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM execution_logs 
                WHERE execution_time > datetime('now', '-30 days')
            """)
            row = cursor.fetchone()
            if row[0] > 0:
                stats['success_rate'] = (row[1] / row[0]) * 100
            else:
                stats['success_rate'] = 0
            
            return stats
