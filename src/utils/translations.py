"""Translations for Al Zait News Agent."""

TRANSLATIONS = {
    'ar': {
        # Welcome & Help
        'welcome_title': '🗞️ <b>مرحباً بك في وكالة الزيت للأنباء!</b>',
        'welcome_message': '''أنا روبوت إخباري ذكي أتابع أخبار السودان من مصادر متعددة وأقدم لك ملخصات يومية.

<b>📌 الأوامر المتاحة:</b>
/news - احصل على آخر الأخبار الآن
/status - حالة الروبوت وإحصائيات
/language - تغيير اللغة
/help - عرض المساعدة
/about - عن وكالة الزيت

<b>⏰ الموجز اليومي:</b>
يتم إرسال موجز الأخبار تلقائياً كل يوم الساعة 7 صباحاً.

<i>للحصول على الأخبار الآن، أرسل /news</i>''',
        
        'help_title': '📚 <b>دليل استخدام وكالة الزيت</b>',
        'help_message': '''<b>الأوامر:</b>

🗞️ /news - <i>احصل على موجز إخباري فوري</i>
📊 /status - <i>عرض حالة الروبوت</i>
🌐 /language - <i>تغيير اللغة (عربي/إنجليزي)</i>
ℹ️ /about - <i>معلومات عن المشروع</i>

<b>ملاحظات:</b>
• الموجز اليومي يُرسل الساعة 7 صباحاً
• يمكنك طلب الأخبار في أي وقت بـ /news''',
        
        # News
        'processing': '⏳ <i>جاري جمع وتحليل الأخبار...</i>\n\nقد يستغرق هذا بضع ثوانٍ.',
        'news_title': '🗞️ <b>موجز الزيت الإخباري</b>',
        'no_news': '📭 <b>لا توجد أخبار جديدة حالياً</b>\n\nلم يتم العثور على أخبار جديدة عن السودان. حاول مرة أخرى لاحقاً.',
        'news_error': '❌ <b>عذراً، لم أتمكن من جمع الأخبار</b>\n\nقد تكون المصادر غير متاحة حالياً. حاول مرة أخرى لاحقاً.',
        'articles_analyzed': '📈 <i>تم تحليل {count} مقال من {events} حدث</i>',
        
        # Status
        'status_title': '📊 <b>حالة وكالة الزيت</b>',
        'stats': '<b>إحصائيات:</b>',
        'total_articles': '• إجمالي المقالات: {count}',
        'articles_this_week': '• مقالات هذا الأسبوع: {count}',
        'success_rate': '• نسبة النجاح: {rate:.1f}%',
        'last_brief': '<b>آخر موجز:</b>',
        'no_brief_yet': 'لم يتم إرسال أي موجز بعد',
        'next_brief': '<b>الموجز القادم:</b>\nالساعة 7:00 صباحاً',
        'system_status': '<b>حالة النظام:</b> 🟢 يعمل',
        
        # Language
        'language_title': '🌐 <b>إعدادات اللغة</b>',
        'language_current': 'اللغة الحالية: <b>{lang}</b>',
        'language_options': '\nاختر اللغة:\n/language_ar - العربية 🇸🇩\n/language_en - English 🇬🇧',
        'language_changed': '✅ تم تغيير اللغة إلى: <b>{lang}</b>',
        'language_ar_name': 'العربية',
        'language_en_name': 'الإنجليزية',
        
        # About
        'about_title': '🗞️ <b>وكالة الزيت للأنباء (Al Zait)</b>',
        'about_message': '''<b>الوصف:</b>
روبوت ذكي مستقل يتابع أخبار السودان يومياً من مصادر متعددة عربية وإنجليزية، ويقدم ملخصات محايدة.

<b>المصادر:</b>
• قناة الجزيرة • BBC عربي • سودان تريبيون
• راديو دبنقا • رويترز • وكالات أخرى

<b>المميزات:</b>
✅ تجميع الأخبار المتشابهة
✅ ملخصات بالعربية والإنجليزية
✅ تحديث يومي تلقائي

<i>صُنع بـ ❤️ للمجتمع السوداني</i>

🔗 GitHub: github.com/Mamoro98/Al-zait''',
        
        # Misc
        'admin_only': '❌ هذا الأمر للمشرفين فقط',
        'db_refreshed': '✅ <b>تم تحديث قاعدة البيانات</b>\n\nسيتم جمع جميع الأخبار من جديد.',
        'error': '❌ حدث خطأ',
    },
    
    'en': {
        # Welcome & Help
        'welcome_title': '🗞️ <b>Welcome to Al Zait News Agency!</b>',
        'welcome_message': '''I am an intelligent news bot that monitors Sudan news from multiple sources and provides daily summaries.

<b>📌 Available Commands:</b>
/news - Get latest news now
/status - Bot status and statistics
/language - Change language
/help - Show help
/about - About Al Zait

<b>⏰ Daily Brief:</b>
News brief is sent automatically every day at 7 AM.

<i>To get news now, send /news</i>''',
        
        'help_title': '📚 <b>Al Zait User Guide</b>',
        'help_message': '''<b>Commands:</b>

🗞️ /news - <i>Get instant news brief</i>
📊 /status - <i>View bot status</i>
🌐 /language - <i>Change language (Arabic/English)</i>
ℹ️ /about - <i>About the project</i>

<b>Notes:</b>
• Daily brief is sent at 7 AM
• You can request news anytime with /news''',
        
        # News
        'processing': '⏳ <i>Gathering and analyzing news...</i>\n\nThis may take a few seconds.',
        'news_title': '🗞️ <b>Al Zait News Brief</b>',
        'no_news': '📭 <b>No new news currently</b>\n\nNo new news about Sudan found. Try again later.',
        'news_error': '❌ <b>Sorry, could not gather news</b>\n\nSources may be unavailable. Try again later.',
        'articles_analyzed': '📈 <i>Analyzed {count} articles from {events} events</i>',
        
        # Status
        'status_title': '📊 <b>Al Zait Status</b>',
        'stats': '<b>Statistics:</b>',
        'total_articles': '• Total articles: {count}',
        'articles_this_week': '• Articles this week: {count}',
        'success_rate': '• Success rate: {rate:.1f}%',
        'last_brief': '<b>Last brief:</b>',
        'no_brief_yet': 'No brief sent yet',
        'next_brief': '<b>Next brief:</b>\n7:00 AM',
        'system_status': '<b>System status:</b> 🟢 Running',
        
        # Language
        'language_title': '🌐 <b>Language Settings</b>',
        'language_current': 'Current language: <b>{lang}</b>',
        'language_options': '\nChoose language:\n/language_ar - العربية 🇸🇩\n/language_en - English 🇬🇧',
        'language_changed': '✅ Language changed to: <b>{lang}</b>',
        'language_ar_name': 'Arabic',
        'language_en_name': 'English',
        
        # About
        'about_title': '🗞️ <b>Al Zait News Agency</b>',
        'about_message': '''<b>Description:</b>
An autonomous intelligent bot that monitors Sudan news daily from multiple Arabic and English sources, providing neutral summaries.

<b>Sources:</b>
• Al Jazeera • BBC Arabic • Sudan Tribune
• Radio Dabanga • Reuters • Other agencies

<b>Features:</b>
✅ Groups similar news stories
✅ Summaries in Arabic and English
✅ Automatic daily updates

<i>Made with ❤️ for the Sudanese community</i>

🔗 GitHub: github.com/Mamoro98/Al-zait''',
        
        # Misc
        'admin_only': '❌ This command is for admins only',
        'db_refreshed': '✅ <b>Database refreshed</b>\n\nAll news will be collected again.',
        'error': '❌ An error occurred',
    }
}


def get_text(key: str, lang: str = 'ar', **kwargs) -> str:
    """Get translated text by key and language."""
    lang = lang if lang in TRANSLATIONS else 'ar'
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['ar'].get(key, key))
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    
    return text
