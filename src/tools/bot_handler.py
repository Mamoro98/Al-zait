"""Interactive Telegram bot handler for Al Zait News Agent."""

import asyncio
from datetime import datetime
from typing import Optional
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from loguru import logger

from src.utils.config import Config
from src.tools.database import NewsDatabase


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
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """
🗞️ <b>مرحباً بك في وكالة الزيت للأنباء!</b>

أنا روبوت إخباري ذكي أتابع أخبار السودان من مصادر متعددة وأقدم لك ملخصات يومية.

<b>📌 الأوامر المتاحة:</b>
/news - احصل على آخر الأخبار الآن
/status - حالة الروبوت وإحصائيات
/help - عرض المساعدة
/about - عن وكالة الزيت

<b>⏰ الموجز اليومي:</b>
يتم إرسال موجز الأخبار تلقائياً كل يوم الساعة 7 صباحاً.

<i>للحصول على الأخبار الآن، أرسل /news</i>
        """.strip()
        
        await update.message.reply_text(welcome_message, parse_mode='HTML')
        logger.info(f"User {update.effective_user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📚 <b>دليل استخدام وكالة الزيت</b>

<b>الأوامر:</b>

🗞️ /news - <i>احصل على موجز إخباري فوري</i>
يجمع آخر الأخبار من المصادر ويقدم ملخصاً عربياً

📊 /status - <i>عرض حالة الروبوت</i>
إحصائيات وموعد آخر موجز

ℹ️ /about - <i>معلومات عن المشروع</i>

🔄 /refresh - <i>تحديث قاعدة البيانات</i>
(للمشرفين فقط)

<b>ملاحظات:</b>
• الموجز اليومي يُرسل الساعة 7 صباحاً
• يمكنك طلب الأخبار في أي وقت بـ /news
• المصادر: الجزيرة، BBC عربي، سودان تريبيون
        """.strip()
        
        await update.message.reply_text(help_message, parse_mode='HTML')
    
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /news command - fetch and send news brief on demand."""
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested news brief")
        
        # Send "processing" message
        processing_msg = await update.message.reply_text(
            "⏳ <i>جاري جمع وتحليل الأخبار...</i>\n\nقد يستغرق هذا بضع ثوانٍ.",
            parse_mode='HTML'
        )
        
        try:
            # Run the news agent
            agent = self._get_news_agent()
            result = agent.run_daily_brief()
            
            brief = result.get('brief', '')
            stats_data = result.get('stats', {})
            
            # Check if we have a brief (even if delivery failed, we still have content)
            if brief and len(brief) > 50:
                stats = f"\n\n📈 <i>تم تحليل {stats_data.get('articles_fetched', 0)} مقال من {stats_data.get('events_identified', 0)} حدث</i>"
                
                # Delete processing message
                await processing_msg.delete()
                
                # Send the brief
                await update.message.reply_text(
                    f"🗞️ <b>موجز الزيت الإخباري</b>\n📅 <i>{self._get_arabic_date()}</i>\n\n{brief}{stats}",
                    parse_mode='HTML'
                )
                logger.info(f"News brief sent to user {user_id}")
            elif stats_data.get('articles_fetched', 0) == 0:
                await processing_msg.edit_text(
                    "📭 <b>لا توجد أخبار جديدة حالياً</b>\n\n"
                    "لم يتم العثور على أخبار جديدة عن السودان. حاول مرة أخرى لاحقاً.",
                    parse_mode='HTML'
                )
                logger.info(f"No new articles found for user {user_id}")
            else:
                await processing_msg.edit_text(
                    "❌ <b>عذراً، لم أتمكن من جمع الأخبار</b>\n\n"
                    "قد تكون المصادر غير متاحة حالياً. حاول مرة أخرى لاحقاً.",
                    parse_mode='HTML'
                )
                logger.warning(f"Failed to generate brief for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error generating news for user {user_id}: {e}")
            await processing_msg.edit_text(
                f"❌ <b>حدث خطأ</b>\n\n<i>{str(e)[:100]}</i>",
                parse_mode='HTML'
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        try:
            stats = self.db.get_statistics()
            recent_briefs = self.db.get_recent_briefs(limit=1)
            
            last_brief = "لم يتم إرسال أي موجز بعد"
            if recent_briefs:
                last_time = recent_briefs[0].get('created_at', 'غير معروف')
                last_status = recent_briefs[0].get('delivery_status', 'غير معروف')
                last_brief = f"{last_time} ({last_status})"
            
            status_message = f"""
📊 <b>حالة وكالة الزيت</b>

<b>إحصائيات:</b>
• إجمالي المقالات: {stats.get('total_articles', 0)}
• مقالات هذا الأسبوع: {stats.get('articles_this_week', 0)}
• نسبة النجاح: {stats.get('success_rate', 0):.1f}%

<b>آخر موجز:</b>
{last_brief}

<b>الموجز القادم:</b>
الساعة 7:00 صباحاً

<b>حالة النظام:</b> 🟢 يعمل
            """.strip()
            
            await update.message.reply_text(status_message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await update.message.reply_text(
                "❌ خطأ في جلب الحالة",
                parse_mode='HTML'
            )
    
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command."""
        about_message = """
🗞️ <b>وكالة الزيت للأنباء (Al Zait)</b>

<b>الوصف:</b>
روبوت ذكي مستقل يتابع أخبار السودان يومياً من مصادر متعددة عربية وإنجليزية، ويقدم ملخصات محايدة باللغة العربية الفصحى.

<b>المصادر:</b>
• قناة الجزيرة
• BBC عربي  
• سودان تريبيون
• وكالات أنباء متعددة

<b>المميزات:</b>
✅ تجميع الأخبار المتشابهة
✅ كشف التحيز وتقديم رؤية محايدة
✅ ملخصات بالعربية الفصحى
✅ تحديث يومي تلقائي

<b>التقنيات:</b>
🤖 LangGraph + Groq AI
📡 Telegram Bot API

<i>صُنع بـ ❤️ للمجتمع السوداني في كل مكان</i>

🔗 GitHub: github.com/Mamoro98/Al-zait
        """.strip()
        
        await update.message.reply_text(about_message, parse_mode='HTML')
    
    async def refresh_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /refresh command - clear processed articles (admin only)."""
        # For now, allow all users. Add admin check later if needed.
        user_id = update.effective_user.id
        admin_id = int(Config.TELEGRAM_CHAT_ID) if Config.TELEGRAM_CHAT_ID else None
        
        if admin_id and user_id != admin_id:
            await update.message.reply_text(
                "❌ هذا الأمر للمشرفين فقط",
                parse_mode='HTML'
            )
            return
        
        try:
            # Clear the database
            self.db.clear_processed_urls()
            await update.message.reply_text(
                "✅ <b>تم تحديث قاعدة البيانات</b>\n\nسيتم جمع جميع الأخبار من جديد.",
                parse_mode='HTML'
            )
            logger.info(f"Database refreshed by user {user_id}")
        except Exception as e:
            logger.error(f"Error refreshing database: {e}")
            await update.message.reply_text("❌ خطأ في التحديث")
    
    def _get_arabic_date(self) -> str:
        """Get current date in Arabic format."""
        arabic_months = [
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ]
        now = datetime.now()
        return f"{now.day} {arabic_months[now.month - 1]} {now.year}"
    
    async def setup_commands(self, application: Application):
        """Set up bot commands in Telegram."""
        commands = [
            BotCommand("news", "احصل على آخر الأخبار"),
            BotCommand("status", "حالة الروبوت"),
            BotCommand("help", "المساعدة"),
            BotCommand("about", "عن الوكالة"),
            BotCommand("start", "بدء المحادثة"),
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
