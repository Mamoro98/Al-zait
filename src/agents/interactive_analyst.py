"""Interactive News Analyst for Al Zait - Conversational Q&A about Sudan news."""

from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime
from src.tools.vector_db_client import VectorDBClient
from src.tools.llm_client import LLMClient

class InteractiveAnalyst:
    """Interactive news analyst for conversational Q&A about Sudan news."""
    
    def __init__(self):
        """Initialize the interactive analyst."""
        self.vector_db = VectorDBClient()
        self.llm_client = LLMClient()
        
        # Conversation tracking
        self.conversation_history = {}
        
        logger.info("Interactive News Analyst initialized")
    
    def is_available(self) -> bool:
        """Check if the analyst is ready to answer questions."""
        # Always available for basic commands, even without vector DB
        return True
    
    def add_articles_to_knowledge_base(self, articles: List[Dict[str, Any]]) -> int:
        """Add articles to the knowledge base for future Q&A."""
        return self.vector_db.add_articles(articles)
    
    def handle_user_question(self, question: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Handle a user question and provide an intelligent response.
        
        Args:
            question: User's question in Arabic or English
            user_id: Unique identifier for the user (for conversation tracking)
            
        Returns:
            Response dictionary with answer, sources, and metadata
        """
        logger.info(f"Processing question from user {user_id}: {question[:50]}...")
        
        # Check if vector DB is available for advanced Q&A
        vector_db_available = self.vector_db.is_available()
        
        # Clean and validate question
        question = question.strip()
        if len(question) < 3:
            return {
                'answer': 'يرجى كتابة سؤال أكثر وضوحاً.',
                'type': 'error',
                'sources': [],
                'confidence': 0
            }
        
        # Check for special commands
        if question.lower().startswith('/'):
            return self._handle_command(question, user_id)
        
        # Store question in conversation history
        self._add_to_conversation(user_id, 'user', question)
        
        try:
            if vector_db_available:
                # Get answer using RAG
                response = self.vector_db.answer_question(question, context_limit=5)
                
                # Enhance the response
                enhanced_response = self._enhance_response(response, question)
                
                # Store response in conversation history
                self._add_to_conversation(user_id, 'assistant', enhanced_response['answer'])
                
                logger.info(f"Generated response for user {user_id} (confidence: {enhanced_response['confidence']}%)")
                
                return enhanced_response
            else:
                # Provide basic response without vector DB
                basic_response = self._provide_basic_response(question, user_id)
                
                # Store response in conversation history
                self._add_to_conversation(user_id, 'assistant', basic_response['answer'])
                
                logger.info(f"Generated basic response for user {user_id} (no vector DB)")
                
                return basic_response
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                'answer': 'عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى.',
                'type': 'error',
                'sources': [],
                'confidence': 0
            }
    
    def _handle_command(self, command: str, user_id: str) -> Dict[str, Any]:
        """Handle special commands from users."""
        command = command.lower().strip()
        
        if command == '/help' or command == '/مساعدة':
            return {
                'answer': """🤖 مرحباً بك في نظام الخبير الإخباري لوكالة الزيت!

يمكنني الإجابة على أسئلتك حول أخبار السودان. مثلاً:
• ما آخر التطورات السياسية؟
• كيف هو الوضع الاقتصادي؟
• أخبرني عن الوضع الأمني
• ما هي آخر الأخبار من الخرطوم؟

الأوامر المتاحة:
/help - عرض هذه المساعدة
/stats - إحصائيات قاعدة البيانات
/clear - مسح تاريخ المحادثة

💡 نصيحة: اكتب أسئلتك بوضوح للحصول على أفضل الإجابات!""",
                'type': 'help',
                'sources': [],
                'confidence': 100
            }
        
        elif command == '/stats' or command == '/إحصائيات':
            stats = self.vector_db.get_collection_stats()
            
            if stats['available']:
                stats_text = f"""📊 إحصائيات قاعدة البيانات الإخبارية:

📰 إجمالي المقالات: {stats['total_articles']}
🌍 اللغات: {', '.join(stats.get('languages', {}).keys()) or 'غير محدد'}
📡 أهم المصادر: {', '.join(list(stats.get('top_sources', {}).keys())[:5]) or 'غير محدد'}

💾 مسار قاعدة البيانات: {stats['database_path']}
✅ الحالة: نشط ومتاح للاستعلام"""
            else:
                stats_text = "❌ قاعدة البيانات غير متاحة حالياً"
            
            return {
                'answer': stats_text,
                'type': 'stats',
                'sources': [],
                'confidence': 100
            }
        
        elif command == '/clear' or command == '/مسح':
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
            
            return {
                'answer': '🗑️ تم مسح تاريخ المحادثة. يمكنك البدء من جديد!',
                'type': 'system',
                'sources': [],
                'confidence': 100
            }
        
        else:
            return {
                'answer': f'أمر غير معروف: {command}\nاكتب /help للحصول على قائمة الأوامر المتاحة.',
                'type': 'error',
                'sources': [],
                'confidence': 0
            }
    
    def _enhance_response(self, response: Dict[str, Any], original_question: str) -> Dict[str, Any]:
        """Enhance the RAG response with additional information."""
        enhanced = response.copy()
        
        # Add response type
        if enhanced['confidence'] > 70:
            enhanced['type'] = 'confident'
        elif enhanced['confidence'] > 40:
            enhanced['type'] = 'moderate'
        else:
            enhanced['type'] = 'uncertain'
        
        # Add helpful footer if there are sources
        if enhanced['sources'] and enhanced['answer']:
            source_count = len(enhanced['sources'])
            enhanced['answer'] += f"\n\n📚 المصادر: {source_count} مقال"
            
            # Add confidence indicator
            confidence = enhanced['confidence']
            if confidence > 80:
                enhanced['answer'] += f"\n🟢 مستوى الثقة: عالي ({confidence}%)"
            elif confidence > 50:
                enhanced['answer'] += f"\n🟡 مستوى الثقة: متوسط ({confidence}%)"
            else:
                enhanced['answer'] += f"\n🔴 مستوى الثقة: منخفض ({confidence}%)"
        
        # Add timestamp
        enhanced['timestamp'] = datetime.now().isoformat()
        enhanced['question'] = original_question
        
        return enhanced
    
    def _add_to_conversation(self, user_id: str, role: str, content: str):
        """Add message to conversation history."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 messages per user
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    def get_conversation_context(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context for a user."""
        if user_id not in self.conversation_history:
            return []
        
        return self.conversation_history[user_id][-limit:]
    
    def suggest_questions(self) -> List[str]:
        """Suggest interesting questions users can ask."""
        suggestions = [
            "ما آخر التطورات السياسية في السودان؟",
            "كيف هو الوضع الاقتصادي الحالي؟",
            "أخبرني عن الوضع الأمني في البلاد",
            "ما هي آخر الأخبار من الخرطوم؟",
            "كيف هو الوضع الإنساني في دارفور؟",
            "ما التطورات في العلاقات الخارجية للسودان؟",
            "أخبرني عن مشاريع التنمية الجديدة",
            "كيف هو وضع الزراعة والثروة الحيوانية؟"
        ]
        
        # Return 3 random suggestions
        import random
        return random.sample(suggestions, min(3, len(suggestions)))
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the interactive analyst system."""
        vector_db_test = self.vector_db.test_connection()
        db_stats = self.vector_db.get_collection_stats()
        
        return {
            'available': self.is_available(),
            'vector_db_status': vector_db_test,
            'knowledge_base_stats': db_stats,
            'active_conversations': len(self.conversation_history),
            'total_messages': sum(len(conv) for conv in self.conversation_history.values()),
            'initialized_at': datetime.now().isoformat()
        }
    
    def process_batch_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Process multiple questions in batch for testing/demo."""
        results = []
        
        for i, question in enumerate(questions):
            user_id = f"batch_user_{i}"
            response = self.handle_user_question(question, user_id)
            results.append({
                'question': question,
                'response': response
            })
        
        return results
    
    def cleanup_old_conversations(self, days_to_keep: int = 7):
        """Clean up old conversation history."""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for user_id in list(self.conversation_history.keys()):
            # Filter messages by date
            filtered_messages = []
            for message in self.conversation_history[user_id]:
                try:
                    message_date = datetime.fromisoformat(message['timestamp'])
                    if message_date >= cutoff_date:
                        filtered_messages.append(message)
                except:
                    # Keep message if timestamp parsing fails
                    filtered_messages.append(message)
            
            if filtered_messages:
                self.conversation_history[user_id] = filtered_messages
            else:
                del self.conversation_history[user_id]
        
        logger.info(f"Cleaned up old conversations, keeping {days_to_keep} days")
    
    def format_telegram_response(self, response: Dict[str, Any]) -> str:
        """Format response for Telegram delivery."""
        answer = response['answer']
        
        # Add sources if available
        sources = response.get('sources', [])
        if sources and len(sources) > 0:
            answer += "\n\n📚 المصادر:\n"
            for i, source in enumerate(sources[:3], 1):  # Show max 3 sources
                answer += f"{i}. {source['title']} - {source['source']}\n"
        
        # Add footer
        answer += "\n🤖 الخبير الإخباري - وكالة الزيت للأنباء"
        
        return answer
    
    def _provide_basic_response(self, question: str, user_id: str) -> Dict[str, Any]:
        """Provide basic response when vector DB is not available."""
        question_lower = question.lower()
        
        # Handle common questions about Sudan
        if any(word in question_lower for word in ['sudan', 'سودان']):
            if any(word in question_lower for word in ['economy', 'اقتصاد', 'economic']):
                answer = """📊 **الوضع الاقتصادي في السودان:**

🏭 يواجه السودان تحديات اقتصادية كبيرة بما في ذلك:
• التضخم والعملة
• نقص الوقود والكهرباء  
• تأثير الأزمة السياسية

⚠️ **ملاحظة**: هذه معلومات عامة. للحصول على آخر التطورات الدقيقة، يحتاج النظام إلى قاعدة بيانات أكثر تفصيلاً."""

            elif any(word in question_lower for word in ['politics', 'سياسة', 'political']):
                answer = """🏛️ **الوضع السياسي في السودان:**

🔄 يمر السودان بفترة انتقالية معقدة مع:
• تحديات في الحكم والاستقرار
• جهود للتحول الديمقراطي
• تفاعلات إقليمية ودولية

⚠️ **ملاحظة**: للحصول على آخر التطورات السياسية المحدثة، يحتاج النظام إلى الوصول لقاعدة الأخبار."""

            elif any(word in question_lower for word in ['security', 'أمن', 'darfur', 'دارفور']):
                answer = """🛡️ **الوضع الأمني في السودان:**

⚡ التحديات الأمنية تشمل:
• الاستقرار في مناطق مختلفة
• قضايا دارفور والمناطق المتأثرة
• جهود حفظ السلام

⚠️ **ملاحظة**: لمعلومات أمنية محدثة ودقيقة، يحتاج النظام إلى مصادر إخبارية متخصصة."""
            
            else:
                answer = """🇸🇩 **معلومات عامة عن السودان:**

📍 السودان بلد في شمال شرق أفريقيا بتاريخ وثقافة عريقة.

🏛️ **للحصول على معلومات محدثة ومفصلة** عن:
• آخر الأخبار السياسية
• التطورات الاقتصادية  
• الأوضاع الأمنية
• الشؤون الاجتماعية

⚠️ **يحتاج النظام إلى قاعدة بيانات إخبارية متطورة (غير متاحة حالياً)**"""

        else:
            # General response for non-Sudan questions
            answer = """🤖 **مرحباً! أنا وكالة الزيت للأنباء**

🎯 **تخصصي**: الإجابة على أسئلة حول السودان مثل:
• الأخبار السياسية
• التطورات الاقتصادية
• الأوضاع الأمنية
• الشؤون الاجتماعية

⚠️ **حالياً**: النظام في وضع محدود (بدون قاعدة بيانات متقدمة)
✅ **لكن يمكنني**: الرد على الأوامر والأسئلة الأساسية

💡 **جرب سؤالاً عن السودان!**"""

        return {
            'answer': answer,
            'type': 'basic_response',
            'sources': [],
            'confidence': 50  # Medium confidence for basic responses
        }
