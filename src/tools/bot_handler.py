"""Interactive Telegram bot handler for Al Zait News Agent."""

import asyncio
from datetime import datetime
from typing import Optional
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from loguru import logger

from src.utils.config import Config
from src.tools.database import NewsDatabase
from src.utils.translations import get_text, TRANSLATIONS


class AlZaitBot:
    """Interactive Telegram bot for Al Zait News Agent."""
    
    def __init__(self):
        """Initialize the bot handler."""
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.application: Optional[Application] = None
        self.db = NewsDatabase()
        self._news_agent = None  # Lazy load to avoid circular imports
    
    def _get_news_agent(self):
        """Lazy load the news agent."""
        if self._news_agent is None:
            from src.agents.news_agent import AlZaitNewsAgent
            self._news_agent = AlZaitNewsAgent()
        return self._news_agent
    
    def _get_user_lang(self, user_id) -> str:
        """Get user's preferred language."""
        return self.db.get_user_language(str(user_id))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        message = f"{get_text('welcome_title', lang)}\n\n{get_text('welcome_message', lang)}"
        
        await update.message.reply_text(message, parse_mode='HTML')
        logger.info(f"User {user_id} started the bot (lang: {lang})")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        message = f"{get_text('help_title', lang)}\n\n{get_text('help_message', lang)}"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /news command - fetch and send news brief on demand."""
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        logger.info(f"User {user_id} requested news brief (lang: {lang})")
        
        # Send "processing" message
        processing_msg = await update.message.reply_text(
            get_text('processing', lang),
            parse_mode='HTML'
        )
        
        try:
            # Run the news agent with user's language preference
            agent = self._get_news_agent()
            result = agent.run_daily_brief(language=lang)
            
            brief = result.get('brief', '')
            stats_data = result.get('stats', {})
            
            # Check if we have a brief (even if delivery failed, we still have content)
            if brief and len(brief) > 50:
                stats = "\n\n" + get_text('articles_analyzed', lang, 
                    count=stats_data.get('articles_fetched', 0),
                    events=stats_data.get('events_identified', 0)
                )
                
                # Delete processing message
                await processing_msg.delete()
                
                # Send the brief
                await update.message.reply_text(
                    f"{get_text('news_title', lang)}\n📅 <i>{self._get_date(lang)}</i>\n\n{brief}{stats}",
                    parse_mode='HTML'
                )
                logger.info(f"News brief sent to user {user_id}")
            elif stats_data.get('articles_fetched', 0) == 0:
                await processing_msg.edit_text(
                    get_text('no_news', lang),
                    parse_mode='HTML'
                )
                logger.info(f"No new articles found for user {user_id}")
            else:
                await processing_msg.edit_text(
                    get_text('news_error', lang),
                    parse_mode='HTML'
                )
                logger.warning(f"Failed to generate brief for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error generating news for user {user_id}: {e}")
            await processing_msg.edit_text(
                f"{get_text('error', lang)}\n\n<i>{str(e)[:100]}</i>",
                parse_mode='HTML'
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        try:
            stats = self.db.get_statistics()
            recent_briefs = self.db.get_recent_briefs(limit=1)
            
            last_brief = get_text('no_brief_yet', lang)
            if recent_briefs:
                last_time = recent_briefs[0].get('created_at', 'N/A')
                last_status = recent_briefs[0].get('delivery_status', 'N/A')
                last_brief = f"{last_time} ({last_status})"
            
            status_message = f"""{get_text('status_title', lang)}

{get_text('stats', lang)}
{get_text('total_articles', lang, count=stats.get('total_articles', 0))}
{get_text('articles_this_week', lang, count=stats.get('articles_this_week', 0))}
{get_text('success_rate', lang, rate=stats.get('success_rate', 0))}

{get_text('last_brief', lang)}
{last_brief}

{get_text('next_brief', lang)}

{get_text('system_status', lang)}"""
            
            await update.message.reply_text(status_message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await update.message.reply_text(get_text('error', lang), parse_mode='HTML')
    
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command."""
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        message = f"{get_text('about_title', lang)}\n\n{get_text('about_message', lang)}"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command."""
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        lang_name = get_text('language_ar_name', lang) if lang == 'ar' else get_text('language_en_name', lang)
        
        message = f"""{get_text('language_title', lang)}

{get_text('language_current', lang, language=lang_name)}
{get_text('language_options', lang)}"""
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def language_ar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language_ar command - set Arabic."""
        user_id = update.effective_user.id
        self.db.set_user_language(str(user_id), 'ar')
        
        await update.message.reply_text(
            get_text('language_changed', 'ar', lang='العربية 🇸🇩'),
            parse_mode='HTML'
        )
        logger.info(f"User {user_id} changed language to Arabic")
    
    async def language_en_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language_en command - set English."""
        user_id = update.effective_user.id
        self.db.set_user_language(str(user_id), 'en')
        
        await update.message.reply_text(
            get_text('language_changed', 'en', lang='English 🇬🇧'),
            parse_mode='HTML'
        )
        logger.info(f"User {user_id} changed language to English")
    
    async def refresh_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /refresh command - clear processed articles (admin only)."""
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        admin_id = int(Config.TELEGRAM_CHAT_ID) if Config.TELEGRAM_CHAT_ID else None
        
        if admin_id and user_id != admin_id:
            await update.message.reply_text(get_text('admin_only', lang), parse_mode='HTML')
            return
        
        try:
            self.db.clear_processed_urls()
            await update.message.reply_text(get_text('db_refreshed', lang), parse_mode='HTML')
            logger.info(f"Database refreshed by user {user_id}")
        except Exception as e:
            logger.error(f"Error refreshing database: {e}")
            await update.message.reply_text(get_text('error', lang))
    
    def _get_date(self, lang: str) -> str:
        """Get current date in user's language."""
        if lang == 'ar':
            arabic_months = [
                "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
            ]
            now = datetime.now()
            return f"{now.day} {arabic_months[now.month - 1]} {now.year}"
        else:
            return datetime.now().strftime("%B %d, %Y")
    
    async def setup_commands(self, application: Application):
        """Set up bot commands in Telegram."""
        commands = [
            BotCommand("news", "احصل على الأخبار / Get news"),
            BotCommand("status", "حالة الروبوت / Bot status"),
            BotCommand("language", "تغيير اللغة / Change language"),
            BotCommand("help", "المساعدة / Help"),
            BotCommand("about", "عن الوكالة / About"),
            BotCommand("start", "بدء / Start"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands registered")
    
    def run(self):
        """Run the bot with polling."""
        if not self.bot_token:
            logger.error("No bot token configured")
            return
        
        logger.info("Starting Al Zait interactive bot...")
        
        # Build application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("news", self.news_command))
        self.application.add_handler(CommandHandler("latest", self.news_command))  # Alias
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("about", self.about_command))
        self.application.add_handler(CommandHandler("language", self.language_command))
        self.application.add_handler(CommandHandler("language_ar", self.language_ar_command))
        self.application.add_handler(CommandHandler("language_en", self.language_en_command))
        self.application.add_handler(CommandHandler("refresh", self.refresh_command))
        
        # Set up commands menu
        self.application.post_init = self.setup_commands
        
        # Start polling
        logger.info("Bot is running. Press Ctrl+C to stop.")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def run_bot():
    """Entry point to run the bot."""
    bot = AlZaitBot()
    bot.run()


if __name__ == "__main__":
    run_bot()
