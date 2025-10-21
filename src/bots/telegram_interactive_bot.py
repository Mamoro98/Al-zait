"""Telegram Interactive Bot for Al Zait - Direct Q&A with users."""

import asyncio
import os
from typing import Dict, Any, Optional
from loguru import logger
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from src.agents.interactive_analyst import InteractiveAnalyst
from src.tools.database import NewsDatabase
from src.utils.config import Config

class TelegramInteractiveBot:
    """Interactive Telegram bot for direct Q&A with users."""
    
    def __init__(self):
        """Initialize the interactive bot."""
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.analyst = InteractiveAnalyst()
        self.db = NewsDatabase()
        
        # Bot application
        self.application = None
        
        # Bot statistics
        self.stats = {
            'total_questions': 0,
            'successful_answers': 0,
            'unique_users': set(),
            'popular_topics': {}
        }
        
        logger.info("Telegram Interactive Bot initialized")
    
    def is_available(self) -> bool:
        """Check if the bot is properly configured."""
        # Bot is available if it has a token, regardless of vector DB status
        # It can still respond to commands and basic questions
        return bool(self.bot_token)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or "مستخدم"
        
        self.stats['unique_users'].add(user_id)
        
        welcome_message = f"""🤖 مرحباً {username}! أهلاً بك في وكالة الزيت للأنباء

أنا الخبير الإخباري الذكي، يمكنني الإجابة على جميع أسئلتك حول أخبار السودان!

🔍 **ماذا يمكنني أن أفعل؟**
• الإجابة على أسئلتك حول آخر الأخبار
• البحث في قاعدة البيانات الإخبارية  
• تقديم تحليلات ذكية مع المصادر
• إنشاء ملخصات صوتية للأخبار

💡 **أمثلة على الأسئلة:**
• ما آخر التطورات السياسية؟
• كيف هو الوضع الاقتصادي الحالي؟
• أخبرني عن الوضع في دارفور
• ما هي آخر أخبار الخرطوم؟

📋 **الأوامر المتاحة:**
/help - المساعدة والأوامر
/stats - إحصائيات النظام
/latest - آخر الأخبار
/audio - طلب نسخة صوتية

🚀 ابدأ بسؤالك الآن! أنا هنا لمساعدتك على مدار الساعة."""

        await update.message.reply_text(welcome_message, parse_mode='HTML')
        logger.info(f"New user started bot: {username} (ID: {user_id})")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """📚 **دليل استخدام الخبير الإخباري**

🔍 **كيفية طرح الأسئلة:**
اكتب سؤالك مباشرة وسأجيب عليه باستخدام آخر المعلومات المتوفرة

**أمثلة جيدة:**
• ما آخر التطورات في الوضع السياسي؟
• كيف هو الوضع الاقتصادي الآن؟
• أخبرني عن مشاريع التنمية الجديدة
• What's the latest news from Khartoum?

📋 **الأوامر المفيدة:**
/start - البداية والترحيب
/help - هذه المساعدة
/stats - إحصائيات النظام وقاعدة البيانات
/latest - عرض آخر الملخصات اليومية
/audio - طلب نسخة صوتية للإجابة
/clear - مسح تاريخ المحادثة

🎯 **نصائح للحصول على أفضل النتائج:**
• اكتب أسئلة واضحة ومحددة
• يمكنك السؤال بالعربية أو الإنجليزية
• استخدم /audio لطلب نسخة صوتية من الإجابة
• ابحث عن مواضيع محددة (مثل: دارفور، الخرطوم، الاقتصاد)

🤖 أنا متاح 24/7 لمساعدتك!"""

        await update.message.reply_text(help_message, parse_mode='HTML')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        # Get system stats
        system_status = self.analyst.get_system_status()
        db_stats = self.analyst.vector_db.get_collection_stats()
        
        # Format stats message
        stats_message = f"""📊 **إحصائيات الخبير الإخباري**

🤖 **النظام:**
• الحالة: {'✅ نشط' if system_status['available'] else '❌ غير متاح'}
• المحادثات النشطة: {system_status['active_conversations']}
• إجمالي الرسائل: {system_status['total_messages']}

📰 **قاعدة البيانات:**
• إجمالي المقالات: {db_stats.get('total_articles', 0)}
• اللغات المتاحة: {', '.join(db_stats.get('languages', {}).keys()) or 'غير محدد'}
• المصادر الرئيسية: {len(db_stats.get('top_sources', {}))}

📈 **إحصائيات الاستخدام:**
• إجمالي الأسئلة: {self.stats['total_questions']}
• الإجابات الناجحة: {self.stats['successful_answers']}
• المستخدمين الفريدين: {len(self.stats['unique_users'])}
• معدل النجاح: {(self.stats['successful_answers']/max(self.stats['total_questions'], 1)*100):.1f}%

🔄 آخر تحديث: {system_status['initialized_at'][:19]}"""

        await update.message.reply_text(stats_message, parse_mode='HTML')
    
    async def latest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /latest command - show recent news digest."""
        try:
            # Get latest brief from database
            recent_briefs = self.db.get_recent_briefs(limit=1)
            
            if recent_briefs:
                latest_brief = recent_briefs[0]
                brief_message = f"""📰 **آخر موجز إخباري**
📅 {latest_brief['created_at'][:19]}

{latest_brief['brief_content'][:1500]}...

💡 للحصول على المزيد من التفاصيل، اسأل عن أي موضوع محدد!"""
            else:
                brief_message = """📰 **لا توجد موجزات متاحة حالياً**

🔍 يمكنك طرح أسئلة محددة وسأبحث لك في قاعدة البيانات الإخبارية:
• ما آخر الأخبار السياسية؟
• كيف هو الوضع الاقتصادي؟
• أخبرني عن آخر التطورات"""

            await update.message.reply_text(brief_message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error fetching latest brief: {e}")
            await update.message.reply_text("❌ حدث خطأ في استرجاع آخر الأخبار. يرجى المحاولة لاحقاً.")
    
    async def audio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /audio command - provide audio version of last response."""
        user_id = str(update.effective_user.id)
        
        # Get user's last conversation
        conversation = self.analyst.get_conversation_context(user_id, limit=2)
        
        if not conversation or len(conversation) < 2:
            await update.message.reply_text("❌ لا توجد إجابة سابقة لتحويلها إلى صوت. اطرح سؤالاً أولاً!")
            return
        
        # Get the last assistant response
        last_response = None
        for msg in reversed(conversation):
            if msg['role'] == 'assistant':
                last_response = msg['content']
                break
        
        if not last_response:
            await update.message.reply_text("❌ لا توجد إجابة سابقة متاحة لتحويلها إلى صوت.")
            return
        
        try:
            # Create audio version
            from src.tools.tts_client import TTSClient
            tts_client = TTSClient()
            
            await update.message.reply_text("🎙️ جاري إنشاء النسخة الصوتية...")
            
            audio_path = tts_client.create_audio_brief(last_response, f"user_audio_{user_id}.mp3")
            
            if audio_path:
                # Send audio file
                with open(audio_path, 'rb') as audio_file:
                    await update.message.reply_audio(
                        audio=audio_file,
                        caption="🎙️ النسخة الصوتية من إجابتي السابقة\n🤖 وكالة الزيت للأنباء",
                        parse_mode='HTML'
                    )
                
                # Clean up file
                os.remove(audio_path)
                logger.info(f"Sent audio response to user {user_id}")
            else:
                await update.message.reply_text("❌ فشل في إنشاء النسخة الصوتية. يرجى المحاولة لاحقاً.")
                
        except Exception as e:
            logger.error(f"Error creating audio response: {e}")
            await update.message.reply_text("❌ حدث خطأ في إنشاء النسخة الصوتية.")
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command - clear conversation history."""
        user_id = str(update.effective_user.id)
        
        # Clear conversation history
        if user_id in self.analyst.conversation_history:
            del self.analyst.conversation_history[user_id]
        
        await update.message.reply_text("🗑️ تم مسح تاريخ المحادثة بنجاح!\n\n🔄 يمكنك البدء من جديد الآن.")
    
    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user questions."""
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or "مستخدم"
        question = update.message.text.strip()
        
        # Update statistics
        self.stats['total_questions'] += 1
        self.stats['unique_users'].add(user_id)
        
        # Track popular topics (simple keyword extraction)
        keywords = ['سياسة', 'اقتصاد', 'أمن', 'دارفور', 'خرطوم', 'politics', 'economy', 'security']
        for keyword in keywords:
            if keyword.lower() in question.lower():
                self.stats['popular_topics'][keyword] = self.stats['popular_topics'].get(keyword, 0) + 1
        
        logger.info(f"Question from {username} (ID: {user_id}): {question[:50]}...")
        
        # Show typing indicator
        await update.message.reply_chat_action("typing")
        
        try:
            # Get response from analyst
            response = self.analyst.handle_user_question(question, user_id)
            
            # Format response for Telegram
            formatted_response = self._format_response_for_telegram(response)
            
            # Send response
            await update.message.reply_text(formatted_response, parse_mode='HTML')
            
            # Update success statistics
            if response['confidence'] > 30:  # Consider it successful if confidence > 30%
                self.stats['successful_answers'] += 1
            
            # Offer audio version if response is substantial
            if len(response['answer']) > 100 and response['confidence'] > 50:
                await update.message.reply_text("🎙️ هل تريد النسخة الصوتية؟ اكتب /audio")
            
            logger.info(f"Responded to {username} with confidence {response['confidence']}%")
            
        except Exception as e:
            logger.error(f"Error handling question from {username}: {e}")
            await update.message.reply_text(
                "❌ عذراً، حدث خطأ أثناء معالجة سؤالك.\n"
                "🔄 يرجى المحاولة مرة أخرى أو كتابة السؤال بطريقة أخرى."
            )
    
    def _format_response_for_telegram(self, response: Dict[str, Any]) -> str:
        """Format analyst response for Telegram."""
        answer = response['answer']
        confidence = response['confidence']
        sources = response.get('sources', [])
        
        # Add confidence indicator
        if confidence > 80:
            confidence_emoji = "🟢"
            confidence_text = "عالية"
        elif confidence > 50:
            confidence_emoji = "🟡"
            confidence_text = "متوسطة"
        else:
            confidence_emoji = "🔴"
            confidence_text = "منخفضة"
        
        # Format the response
        formatted = f"{answer}\n\n"
        
        # Add sources if available
        if sources:
            formatted += f"📚 <b>المصادر ({len(sources)}):</b>\n"
            for i, source in enumerate(sources[:3], 1):  # Show max 3 sources
                formatted += f"{i}. {source['title'][:60]}{'...' if len(source['title']) > 60 else ''}\n"
                formatted += f"   📡 {source['source']}\n"
            
            if len(sources) > 3:
                formatted += f"... و {len(sources) - 3} مصادر أخرى\n"
        
        # Add confidence and footer
        formatted += f"\n{confidence_emoji} <b>مستوى الثقة:</b> {confidence_text} ({confidence}%)\n"
        formatted += f"🤖 <i>الخبير الإخباري - وكالة الزيت للأنباء</i>"
        
        return formatted
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the bot."""
        logger.error(f"Bot error: {context.error}")
        
        if isinstance(update, Update) and update.message:
            await update.message.reply_text(
                "❌ حدث خطأ مؤقت في النظام.\n"
                "🔄 يرجى المحاولة مرة أخرى خلال دقائق قليلة."
            )
    
    def setup_handlers(self):
        """Setup bot command and message handlers."""
        if not self.application:
            logger.error("Application not initialized")
            return
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("latest", self.latest_command))
        self.application.add_handler(CommandHandler("audio", self.audio_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        
        # Message handler for questions
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_question)
        )
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Bot handlers configured successfully")
    
    async def start_bot(self):
        """Start the interactive bot."""
        if not self.is_available():
            logger.error("Bot not properly configured or analyst not available")
            return False
        
        try:
            # Initialize application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Setup handlers
            self.setup_handlers()
            
            # Start the bot
            logger.info("Starting Telegram Interactive Bot...")
            await self.application.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            return False
    
    def start_bot_sync(self):
        """Synchronous wrapper to start the bot."""
        try:
            # Check if there's already a running event loop
            try:
                loop = asyncio.get_running_loop()
                logger.info("Found existing event loop, creating task...")
                # If there's already a loop, create a task
                task = loop.create_task(self.start_bot())
                return task
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                logger.info("No existing event loop, creating new one...")
                asyncio.run(self.start_bot())
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
    
    def get_bot_stats(self) -> Dict[str, Any]:
        """Get bot usage statistics."""
        return {
            'total_questions': self.stats['total_questions'],
            'successful_answers': self.stats['successful_answers'],
            'unique_users': len(self.stats['unique_users']),
            'success_rate': (self.stats['successful_answers'] / max(self.stats['total_questions'], 1)) * 100,
            'popular_topics': dict(sorted(self.stats['popular_topics'].items(), key=lambda x: x[1], reverse=True)[:5]),
            'bot_available': self.is_available()
        }
