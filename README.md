# Al Zait (الزيت) - Autonomous Sudan News Agent

> **An intelligent AI agent that autonomously monitors, analyzes, and delivers daily Sudan news briefs in Arabic via Telegram.**

🤖 **Fully Autonomous** • 🌍 **Multilingual** • 💬 **Arabic Output** • 📱 **Telegram Integration** • 🔄 **Daily Automation**

---

## 📖 Overview

Al Zait is an advanced autonomous AI agent that runs daily at 8:00 AM, scanning 20+ Arabic and English news sources to find the most important news about Sudan. It intelligently groups duplicate stories, writes neutral 3-sentence summaries in Modern Standard Arabic, and delivers a clean daily brief to a Telegram channel.

**Key Problem Solved:** Information overload and bias for the Sudanese diaspora who need accurate, neutral, and consolidated news about their homeland.

---

## ✨ Features

### 🤖 **Autonomous Intelligence**
- Runs automatically every day at 8:00 AM
- No human intervention required
- Smart error recovery and fallback mechanisms
- Persistent memory to avoid duplicate processing

### 🌐 **Multi-Source News Gathering**
- NewsAPI integration (1000+ sources)
- RSS feed monitoring (Al Jazeera, BBC Arabic, Sudan Tribune)
- Cross-language duplicate detection
- Real-time article fetching and parsing

### 🧠 **Advanced AI Processing**
- **Event Clustering:** Groups related articles using LLM analysis
- **Bias Mitigation:** Identifies conflicting viewpoints and presents them neutrally
- **Arabic Summarization:** Generates factual 3-sentence summaries in MSA
- **Cross-Language Understanding:** Processes both Arabic and English sources

### 📱 **Seamless Delivery**
- Telegram bot integration with proper Arabic text rendering
- Formatted daily briefs with timestamps
- Long message handling (auto-splits if needed)
- Delivery status tracking and error notifications

### 💾 **Persistent Memory**
- SQLite database for URL deduplication
- Execution history and statistics tracking
- Brief archive with delivery status
- Automatic cleanup of old data

---

## 🏗️ Architecture

Al Zait uses **LangGraph** for stateful workflow management with the following nodes:

```
📥 fetch_news
    ↓
🔍 filter_articles
    ↓  
🎯 cluster_events
    ↓
📝 summarize_events
    ↓
📋 compile_brief
    ↓
📤 deliver_brief
    ↓
💾 update_memory
    ↓
✅ END
```

### **Technology Stack (100% Free)**

- **Agent Framework:** LangGraph for state management
- **News Sources:** NewsAPI (free tier) + RSS feeds
- **LLM Provider:** Ollama (local) + Groq (backup, free tier)
- **Delivery:** Telegram Bot API (completely free)
- **Database:** SQLite (local) or Railway PostgreSQL (free tier)
- **Hosting:** Railway free tier or GitHub Actions
- **Scheduling:** APScheduler

---

## 🚀 Quick Start

### 1. **Clone Repository**
```bash
git clone https://github.com/your-username/al-zait.git
cd al-zait
```

### 2. **Install Dependencies**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. **Setup Configuration**
```bash
# Copy environment template
cp config/env.template .env

# Edit .env with your API keys (see Configuration section below)
```

### 4. **Setup APIs**

#### **NewsAPI (Optional but Recommended)**
1. Go to [NewsAPI.org](https://newsapi.org/)
2. Sign up for free account (1000 requests/day)
3. Add API key to `.env` file

#### **Groq API (Backup LLM)**
1. Go to [Groq Console](https://console.groq.com/)
2. Create free account (6000 requests/day)
3. Generate API key and add to `.env`

#### **Telegram Bot**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create new bot: `/newbot`
3. Follow instructions to get bot token
4. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
5. Add both to `.env` file

#### **Ollama (Local LLM - Optional)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Arabic-capable model
ollama pull qwen2.5:14b
# or smaller model: ollama pull qwen2.5:7b
```

### 5. **Test Configuration**
```bash
# Test all components
python main.py --test

# Run quick workflow test
python run_once.py --quick-test
```

### 6. **Run Agent**
```bash
# Run once manually (for testing)
python run_once.py --run-full

# Start automated scheduler
python main.py --schedule
```

---

## ⚙️ Configuration

Create a `.env` file based on `config/env.template`:

```bash
# News API (Free tier: 1000 requests/day)
NEWSAPI_KEY=your_newsapi_key_here

# Groq API (Free tier: 6000 requests/day) - Backup LLM
GROQ_API_KEY=your_groq_api_key_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Local LLM Settings (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b

# Agent Configuration
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
MAX_ARTICLES_PER_QUERY=10
SUMMARY_LENGTH_SENTENCES=3

# Search Queries (Arabic and English)
SEARCH_QUERIES_AR=أخبار السودان اليوم,السياسة السودانية,الاقتصاد السوداني
SEARCH_QUERIES_EN=Sudan news today,Sudan political news,Sudan economy news

# RSS Feeds (backup sources)
RSS_FEEDS=https://www.aljazeera.com/xml/rss/all.xml,https://feeds.bbci.co.uk/arabic/rss.xml,http://www.sudantribune.com/spip.php?page=backend
```

---

## 🎯 Usage

### **Automated Mode (Production)**
```bash
# Start the scheduler (runs daily at 8:00 AM)
python main.py --schedule
```

### **Manual Testing**
```bash
# Test individual components
python run_once.py --test-components

# Test workflow with limited articles
python run_once.py --test-workflow

# Run full workflow once
python run_once.py --run-full

# Quick validation test
python run_once.py --quick-test
```

### **Configuration Testing**
```bash
# Test all configurations and connections
python main.py --test
```

---

## 📊 Sample Output

### **Daily Brief Format**
```
🗞️ موجز الزيت الإخباري
📅 ٢٠ أكتوبر ٢٠٢٤

أهم الأخبار السودانية اليوم:

1. أعلنت الحكومة السودانية عن توقيع اتفاقية جديدة مع البنك الدولي لدعم الاقتصاد. الاتفاقية تشمل قروضاً ميسرة بقيمة ٥٠٠ مليون دولار لتمويل مشاريع البنية التحتية. من المتوقع أن تبدأ تنفيذ المشاريع خلال الربع الأول من العام المقبل.

2. شهدت مدينة الخرطوم هطول أمطار غزيرة أدت إلى فيضانات في عدة أحياء. أفادت وزارة الداخلية بإخلاء أكثر من ١٠٠ أسرة من المناطق المتضررة. تعمل فرق الإنقاذ على تقديم المساعدات الإنسانية للمتضررين.

3. أكدت وزارة الصحة تسجيل انخفاض في معدلات الملاريا بنسبة ٣٠٪ مقارنة بالعام الماضي. أرجعت الوزارة هذا التحسن إلى حملات التطعيم الموسعة ومكافحة البعوض. تخطط الوزارة لإطلاق حملة جديدة في المناطق الريفية الشهر المقبل.

📡 وكالة الزيت للأنباء
🤖 تقرير آلي مدعوم بالذكاء الاصطناعي
```

### **Console Logs**
```
11:30:45 | INFO     | Starting Al Zait daily news brief generation
11:30:46 | INFO     | Fetching news for 6 queries: ['أخبار السودان اليوم', ...]
11:30:52 | INFO     | Successfully fetched 47 articles
11:30:52 | INFO     | Filtered to 23 new articles (24 already processed)
11:30:58 | INFO     | Identified 8 distinct events using LLM clustering
11:31:15 | INFO     | Generated 8 Arabic summaries
11:31:18 | INFO     | Successfully compiled final brief (1,247 characters)
11:31:19 | INFO     | Brief delivered successfully via Telegram
11:31:20 | INFO     | ✅ Daily brief generation completed successfully
```

---

## 🧪 Testing

### **Run Tests**
```bash
# Run all unit tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_nodes.py -v

# Run with coverage
pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=html
```

### **Test Individual Components**
```bash
# Test database
python -c "from src.tools.database import NewsDatabase; db = NewsDatabase(); print(db.get_statistics())"

# Test LLM connections
python -c "from src.tools.llm_client import LLMClient; llm = LLMClient(); print(llm.test_connection())"

# Test Telegram
python -c "from src.tools.telegram_client import TelegramClient; tg = TelegramClient(); print(tg.test_connection_sync())"
```

---

## 🐳 Docker Deployment (Optional)

### **Build Image**
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO

# Run the application
CMD ["python", "main.py", "--schedule"]
EOF

# Build image
docker build -t al-zait .
```

### **Run Container**
```bash
# Run with environment file
docker run -d \\
  --name al-zait-agent \\
  --env-file .env \\
  -v $(pwd)/data:/app/data \\
  --restart unless-stopped \\
  al-zait
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **"No LLM connections available"**
```bash
# Option 1: Install Ollama locally
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:7b

# Option 2: Get Groq API key (free)
# Visit https://console.groq.com/
```

#### **"Telegram connection failed"**
```bash
# Verify bot token and chat ID
python -c "
from src.tools.telegram_client import TelegramClient
client = TelegramClient()
print('Bot test:', client.test_connection_sync())
"
```

#### **"No articles fetched"**
```bash
# Check NewsAPI key or rely on RSS feeds
# Verify internet connection
# Check search queries in config
```

#### **Database errors**
```bash
# Reset database
rm data/news.db
python -c "from src.tools.database import NewsDatabase; NewsDatabase()"
```

### **Debug Mode**
```bash
# Run with detailed logging
export LOG_LEVEL=DEBUG
python run_once.py --run-full
```

---

## 📈 Monitoring & Analytics

### **Database Statistics**
```bash
python -c "
from src.tools.database import NewsDatabase
db = NewsDatabase()
stats = db.get_statistics()
print(f'Total articles processed: {stats[\"total_articles\"]}')
print(f'This week: {stats[\"articles_this_week\"]}')
print(f'Success rate: {stats[\"success_rate\"]}%')
"
```

### **View Recent Briefs**
```bash
python -c "
from src.tools.database import NewsDatabase
db = NewsDatabase()
briefs = db.get_recent_briefs(5)
for brief in briefs:
    print(f'{brief[\"created_at\"]}: {brief[\"delivery_status\"]}')
"
```

### **Log Analysis**
```bash
# View recent logs
tail -f data/al_zait.log

# Search for errors
grep "ERROR" data/al_zait.log

# View execution summaries
grep "EXECUTION SUMMARY" data/al_zait.log -A 10
```

---

## 🛠️ Development

### **Project Structure**
```
al-zait/
├── src/
│   ├── agents/           # LangGraph workflow
│   ├── nodes/            # Individual processing nodes
│   ├── tools/            # External service clients
│   └── utils/            # Configuration and prompts
├── tests/                # Unit tests
├── config/               # Configuration templates
├── data/                 # Database and logs
├── main.py               # Scheduler entry point
├── run_once.py           # Manual execution
└── README.md             # This file
```

### **Adding New Nodes**
1. Create node function in `src/nodes/`
2. Import and add to workflow in `src/agents/news_agent.py`
3. Add tests in `tests/`
4. Update state definition if needed

### **Custom News Sources**
Add RSS feeds to `config/env.template`:
```bash
RSS_FEEDS=https://example.com/feed.xml,https://another-source.com/rss
```

---

## 📋 Roadmap

- [ ] **Web Dashboard:** Real-time monitoring interface
- [ ] **Multi-Channel Support:** WhatsApp, Discord, Twitter
- [ ] **Sentiment Analysis:** Track news sentiment trends
- [ ] **Breaking News Alerts:** Immediate notifications for urgent news
- [ ] **Voice Summaries:** Arabic audio briefs
- [ ] **Image Generation:** Automated infographics
- [ ] **Multi-Language Output:** English, French summaries

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Commit changes:** `git commit -m 'Add amazing feature'`
4. **Push to branch:** `git push origin feature/amazing-feature`
5. **Open Pull Request**

### **Development Setup**
```bash
# Clone your fork
git clone https://github.com/your-username/al-zait.git

# Install development dependencies
pip install -e ".[dev]"

# Run pre-commit hooks
black src/ tests/
isort src/ tests/

# Run tests
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain/LangGraph** for the workflow framework
- **Groq** for free LLM API access
- **NewsAPI** for comprehensive news coverage
- **Telegram** for reliable messaging platform
- **Ollama** for local LLM capabilities

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-username/al-zait/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-username/al-zait/discussions)
- **Email:** support@alzait.news

---

**Built with ❤️ for the Sudanese community worldwide**

*Al Zait (الزيت) - Bringing you the essence of Sudan news, daily.*
