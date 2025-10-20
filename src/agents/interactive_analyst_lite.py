"""Lightweight Interactive News Analyst for Railway deployment (under 4GB limit)."""

from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime
from src.tools.llm_client import LLMClient

class InteractiveAnalystLite:
    """Lightweight interactive news analyst that adapts to available features."""
    
    def __init__(self, feature_detector=None):
        """Initialize the lightweight analyst."""
        # Import feature detector
        if feature_detector is None:
            from src.utils.feature_detection import feature_detector as fd
            feature_detector = fd
        
        self.feature_detector = feature_detector
        
        # Get appropriate vector DB client based on available features
        self.vector_db = feature_detector.get_vector_db_client()
        self.llm_client = LLMClient()
        
        # Conversation tracking
        self.conversation_history = {}
        
        # Determine capabilities
        self.capabilities = self._determine_capabilities()
        
        logger.info(f"Interactive News Analyst initialized ({self.capabilities['mode']} mode)")
    
    def _determine_capabilities(self) -> Dict[str, Any]:
        """Determine what capabilities are available in current mode."""
        deployment_info = self.feature_detector.get_deployment_info()
        
        return {
            'mode': deployment_info['ai_capabilities'].lower(),
            'search_type': deployment_info['search_type'].lower(),
            'audio_capable': deployment_info['audio_capabilities'] != 'None',
            'vector_search': self.feature_detector.is_feature_available('vector_search'),
            'advanced_features': self.feature_detector.is_feature_available('full_ai_mode'),
            'railway_optimized': self.feature_detector.is_feature_available('railway_mode')
        }
    
    def is_available(self) -> bool:
        """Check if the analyst is ready to answer questions."""
        return self.vector_db.is_available()
    
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
        
        if not self.is_available():
            return {
                'answer': 'عذراً، نظام الخبير الإخباري غير متاح حالياً. يرجى المحاولة لاحقاً.',
                'type': 'error',
                'sources': [],
                'confidence': 0,
                'method': self.capabilities['mode']
            }
        
        # Clean and validate question
        question = question.strip()
        if len(question) < 3:
            return {
                'answer': 'يرجى كتابة سؤال أكثر وضوحاً.',
                'type': 'error',
                'sources': [],
                'confidence': 0,
                'method': self.capabilities['mode']
            }
        
        # Check for special commands
        if question.lower().startswith('/'):
            return self._handle_command(question, user_id)
        
        # Store question in conversation history
        self._add_to_conversation(user_id, 'user', question)
        
        try:
            # Get answer using appropriate method (vector or text search)
            if self.capabilities['vector_search']:
                response = self.vector_db.answer_question(question, context_limit=5)
            else:
                # Use lightweight search with simple answer generation
                response = self._lightweight_qa(question)
            
            # Enhance the response
            enhanced_response = self._enhance_response(response, question)
            
            # Store response in conversation history
            self._add_to_conversation(user_id, 'assistant', enhanced_response['answer'])
            
            logger.info(f"Generated response for user {user_id} (confidence: {enhanced_response['confidence']}%, method: {enhanced_response.get('method', 'unknown')})")
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                'answer': 'عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى.',
                'type': 'error',
                'sources': [],
                'confidence': 0,
                'method': self.capabilities['mode']
            }
    
    def _lightweight_qa(self, question: str) -> Dict[str, Any]:
        """Lightweight Q&A using simple search + basic answer generation."""
        try:
            # Search for relevant articles using lightweight method
            relevant_articles = self.vector_db.search_articles(question, limit=5)
            
            if not relevant_articles:
                return {
                    'answer': 'عذراً، لم أجد معلومات متعلقة بسؤالك في قاعدة البيانات.',
                    'sources': [],
                    'confidence': 0,
                    'method': 'lightweight_search'
                }
            
            # Filter for high-quality matches
            quality_articles = [a for a in relevant_articles if a['similarity_score'] > 0.2]
            
            if not quality_articles:
                return {
                    'answer': 'عذراً، لم أجد معلومات دقيقة كافية للإجابة على سؤالك.',
                    'sources': [],
                    'confidence': 0,
                    'method': 'lightweight_search'
                }
            
            # Try to use LLM for better answer generation if available
            if len(quality_articles) > 0:
                try:
                    # Prepare context from best articles
                    context_parts = []
                    sources = []
                    
                    for article in quality_articles[:3]:  # Use top 3 articles
                        context_parts.append(f"المصدر: {article['source']}\nالعنوان: {article['title']}\nالمحتوى: {article['content'][:400]}...")
                        sources.append({
                            'title': article['title'][:80] + "..." if len(article['title']) > 80 else article['title'],
                            'source': article['source'],
                            'similarity': round(article['similarity_score'], 2),
                            'url': article['url']
                        })
                    
                    context_text = "\n\n".join(context_parts)
                    
                    # Simple LLM prompt for answer generation
                    simple_prompt = f"""أجب على السؤال بناءً على المعلومات المتوفرة:

السؤال: {question}

المعلومات:
{context_text}

التعليمات:
- أجب باللغة العربية
- استخدم المعلومات المتوفرة فقط
- كن مختصراً ودقيقاً
- لا تذكر أنك تستخدم معلومات محددة

الإجابة:"""
                    
                    answer = self.llm_client.generate_response(simple_prompt, max_tokens=300)
                    
                    if answer and len(answer.strip()) > 10:
                        # Calculate confidence based on similarity
                        avg_similarity = sum(s['similarity'] for s in sources) / len(sources) if sources else 0
                        confidence = min(int(avg_similarity * 80), 75)  # Cap at 75% for lightweight mode
                        
                        return {
                            'answer': answer.strip(),
                            'sources': sources,
                            'confidence': confidence,
                            'context_articles': len(relevant_articles),
                            'method': 'lightweight_llm'
                        }
                
                except Exception as e:
                    logger.warning(f"LLM generation failed, using simple answer: {e}")
            
            # Fallback: Simple answer from best match
            best_article = quality_articles[0]
            
            simple_answer = f"بناءً على المعلومات من {best_article['source']}:\n\n"
            simple_answer += f"{best_article['title']}\n\n"
            simple_answer += f"{best_article['content'][:300]}..."
            
            sources = [{
                'title': best_article['title'][:80] + "..." if len(best_article['title']) > 80 else best_article['title'],
                'source': best_article['source'],
                'similarity': round(best_article['similarity_score'], 2),
                'url': best_article['url']
            }]
            
            confidence = min(int(best_article['similarity_score'] * 60), 60)  # Lower confidence for simple method
            
            return {
                'answer': simple_answer,
                'sources': sources,
                'confidence': confidence,
                'context_articles': len(relevant_articles),
                'method': 'lightweight_simple'
            }
            
        except Exception as e:
            logger.error(f"Error in lightweight Q&A: {e}")
            return {
                'answer': 'عذراً، حدث خطأ أثناء البحث عن الإجابة.',
                'sources': [],
                'confidence': 0,
                'method': 'lightweight_error'
            }
    
    def _handle_command(self, command: str, user_id: str) -> Dict[str, Any]:
        """Handle special commands from users."""
        command = command.lower().strip()
        
        if command == '/help' or command == '/مساعدة':
            mode_info = f"({self.capabilities['mode']} mode)" if self.capabilities['railway_optimized'] else ""
            
            return {
                'answer': f"""🤖 مرحباً بك في نظام الخبير الإخباري لوكالة الزيت! {mode_info}

يمكنني الإجابة على أسئلتك حول أخبار السودان. مثلاً:
• ما آخر التطورات السياسية؟
• كيف هو الوضع الاقتصادي؟
• أخبرني عن الوضع الأمني
• ما هي آخر الأخبار من الخرطوم؟

الأوامر المتاحة:
/help - عرض هذه المساعدة
/stats - إحصائيات قاعدة البيانات
/features - قائمة الميزات المتاحة
/clear - مسح تاريخ المحادثة

💡 نصيحة: اكتب أسئلتك بوضوح للحصول على أفضل الإجابات!""",
                'type': 'help',
                'sources': [],
                'confidence': 100,
                'method': self.capabilities['mode']
            }
        
        elif command == '/stats' or command == '/إحصائيات':
            stats = self.vector_db.get_collection_stats()
            
            if stats.get('available', False):
                stats_text = f"""📊 إحصائيات قاعدة البيانات الإخبارية:

📰 إجمالي المقالات: {stats['total_articles']}
🌍 اللغات: {', '.join(stats.get('languages', {}).keys()) or 'غير محدد'}
📡 أهم المصادر: {', '.join(list(stats.get('top_sources', {}).keys())[:5]) or 'غير محدد'}

🔧 نوع قاعدة البيانات: {stats.get('database_type', 'غير محدد')}
🔍 طريقة البحث: {stats.get('similarity_method', 'غير محدد')}
💾 مسار التخزين: {stats.get('database_path', 'غير محدد')}

✅ الحالة: نشط ومتاح للاستعلام"""
            else:
                stats_text = "❌ قاعدة البيانات غير متاحة حالياً"
            
            return {
                'answer': stats_text,
                'type': 'stats',
                'sources': [],
                'confidence': 100,
                'method': self.capabilities['mode']
            }
        
        elif command == '/features' or command == '/ميزات':
            deployment_info = self.feature_detector.get_deployment_info()
            feature_comparison = self.feature_detector.get_feature_comparison()
            
            features_text = f"""🚀 ميزات النظام المتاحة:

🏗️ **وضع النشر:** {deployment_info['mode']}
🧠 **قدرات الذكاء الاصطناعي:** {deployment_info['ai_capabilities']}
🎙️ **معالجة الصوت:** {deployment_info['audio_capabilities']}
🔍 **نوع البحث:** {deployment_info['search_type']}

📋 **التفاصيل التقنية:**
• البحث: {feature_comparison['search_engine']['current']}
• الصوت: {feature_comparison['audio_processing']['current']}
• المعالجة: {feature_comparison['llm_processing']['current']}
• التخزين: {feature_comparison['storage']['current']}
• الذاكرة: {feature_comparison['memory_usage']['current']}

💡 **للترقية:** اكتب /upgrade للحصول على معلومات الترقية"""
            
            return {
                'answer': features_text,
                'type': 'features',
                'sources': [],
                'confidence': 100,
                'method': self.capabilities['mode']
            }
        
        elif command == '/upgrade' or command == '/ترقية':
            suggestions = self.feature_detector.get_upgrade_suggestions()
            
            upgrade_text = "🚀 **خيارات الترقية المتاحة:**\n\n"
            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    upgrade_text += f"{i}. {suggestion}\n"
            else:
                upgrade_text += "✅ جميع الميزات متاحة! النظام يعمل بكامل طاقته."
            
            return {
                'answer': upgrade_text,
                'type': 'upgrade',
                'sources': [],
                'confidence': 100,
                'method': self.capabilities['mode']
            }
        
        elif command == '/clear' or command == '/مسح':
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
            
            return {
                'answer': '🗑️ تم مسح تاريخ المحادثة. يمكنك البدء من جديد!',
                'type': 'system',
                'sources': [],
                'confidence': 100,
                'method': self.capabilities['mode']
            }
        
        else:
            return {
                'answer': f'أمر غير معروف: {command}\nاكتب /help للحصول على قائمة الأوامر المتاحة.',
                'type': 'error',
                'sources': [],
                'confidence': 0,
                'method': self.capabilities['mode']
            }
    
    def _enhance_response(self, response: Dict[str, Any], original_question: str) -> Dict[str, Any]:
        """Enhance the response with additional information."""
        enhanced = response.copy()
        
        # Add response type based on confidence
        confidence = enhanced.get('confidence', 0)
        if confidence > 70:
            enhanced['type'] = 'confident'
        elif confidence > 40:
            enhanced['type'] = 'moderate'
        else:
            enhanced['type'] = 'uncertain'
        
        # Add mode indicator for Railway users
        if self.capabilities['railway_optimized']:
            method = enhanced.get('method', self.capabilities['mode'])
            enhanced['answer'] += f"\n\n💡 وضع التشغيل: {method}"
        
        # Add helpful footer if there are sources
        if enhanced.get('sources') and enhanced.get('answer'):
            source_count = len(enhanced['sources'])
            enhanced['answer'] += f"\n\n📚 المصادر: {source_count} مقال"
            
            # Add confidence indicator
            if confidence > 60:
                enhanced['answer'] += f"\n🟢 مستوى الثقة: جيد ({confidence}%)"
            elif confidence > 30:
                enhanced['answer'] += f"\n🟡 مستوى الثقة: متوسط ({confidence}%)"
            else:
                enhanced['answer'] += f"\n🔴 مستوى الثقة: منخفض ({confidence}%)"
        
        # Add timestamp and metadata
        enhanced['timestamp'] = datetime.now().isoformat()
        enhanced['question'] = original_question
        enhanced['system_mode'] = self.capabilities['mode']
        
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
        
        # Keep only last 8 messages per user (Railway optimization)
        if len(self.conversation_history[user_id]) > 8:
            self.conversation_history[user_id] = self.conversation_history[user_id][-8:]
    
    def get_conversation_context(self, user_id: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Get recent conversation context for a user (reduced for Railway)."""
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
            "كيف هو الوضع في دارفور؟",
            "ما التطورات في العلاقات الخارجية؟"
        ]
        
        # Return 3 random suggestions
        import random
        return random.sample(suggestions, min(3, len(suggestions)))
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the analyst system."""
        vector_db_test = self.vector_db.test_connection()
        db_stats = self.vector_db.get_collection_stats()
        deployment_info = self.feature_detector.get_deployment_info()
        
        return {
            'available': self.is_available(),
            'vector_db_status': vector_db_test,
            'knowledge_base_stats': db_stats,
            'active_conversations': len(self.conversation_history),
            'total_messages': sum(len(conv) for conv in self.conversation_history.values()),
            'deployment_info': deployment_info,
            'capabilities': self.capabilities,
            'initialized_at': datetime.now().isoformat()
        }
    
    def format_telegram_response(self, response: Dict[str, Any]) -> str:
        """Format response for Telegram delivery."""
        answer = response['answer']
        
        # Add sources if available
        sources = response.get('sources', [])
        if sources and len(sources) > 0:
            answer += "\n\n📚 المصادر:\n"
            for i, source in enumerate(sources[:2], 1):  # Show max 2 sources for Railway
                answer += f"{i}. {source['title']} - {source['source']}\n"
        
        # Add footer with mode info
        mode = response.get('system_mode', 'standard')
        answer += f"\n🤖 الخبير الإخباري ({mode}) - وكالة الزيت للأنباء"
        
        return answer
