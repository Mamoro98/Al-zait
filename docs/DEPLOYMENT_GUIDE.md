# 🚀 Al Zait Deployment Guide - Production Setup

## Overview

This guide covers deploying Al Zait's advanced AI system to production, including all intelligent features: RAG Q&A, audio generation, and interactive Telegram bot.

---

## 🏗️ **Architecture Overview**

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   News Sources  │────│   Collector      │────│   Vector DB     │
│   RSS/NewsAPI   │    │   Agent          │    │   ChromaDB      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │────│   Editor Agent   │────│   Audio TTS     │
│   Bot/Channel   │    │   + RAG System   │    │   gTTS          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                       ┌──────────────────┐
                       │ Interactive Bot  │
                       │ Q&A System       │
                       └──────────────────┘
```

### Service Types
- **Daily/Hourly Agent**: Automated news collection and digest creation
- **Interactive Bot**: Real-time Q&A with users
- **Background Services**: Vector database, audio generation, cleanup

---

## 🛠️ **Prerequisites**

### Required Accounts (All FREE)
1. **Railway Account**: [railway.app](https://railway.app) - Free tier hosting
2. **Telegram Bot**: BotFather bot token - Free
3. **NewsAPI Key**: [newsapi.org](https://newsapi.org) - Free tier
4. **Gemini API**: [ai.google.dev](https://ai.google.dev) - Free tier
5. **GitHub Account**: For code repository - Free

### Local Development Setup
```bash
# Python 3.11+ required
python --version

# Clone repository
git clone <your-repo-url>
cd al-zait

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🔑 **Configuration Setup**

### Environment Variables
Create `.env` file in project root:

```bash
# Required - Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_channel_or_chat_id

# Required - News Sources  
NEWSAPI_KEY=your_newsapi_key

# Required - AI Processing
GEMINI_API_KEY=your_gemini_api_key

# Optional - Advanced Configuration
MAX_CONTENT_LENGTH=800
SCHEDULE_MINUTE=0
LOG_LEVEL=INFO

# Production Settings
RAILWAY=true
PORT=8000
```

### Getting API Keys

**1. Telegram Bot Token:**
```
1. Message @BotFather on Telegram
2. Send: /newbot
3. Choose bot name: "Al Zait News Bot"  
4. Choose username: "AlZaitNewsBot" (must be unique)
5. Copy the token provided
```

**2. Telegram Chat ID:**
```bash
# For channel: Create channel, add bot as admin, get channel ID
# For group: Add bot to group, send message, get chat ID
# Use this API call to find your chat ID:
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

**3. NewsAPI Key:**
```
1. Go to https://newsapi.org/register
2. Create free account
3. Copy API key from dashboard
4. Free tier: 1000 requests/day
```

**4. Gemini API Key:**
```
1. Go to https://ai.google.dev
2. Create project and enable Gemini API
3. Generate API key
4. Free tier: 60 requests/minute
```

---

## 🚂 **Railway Deployment**

### Step 1: Prepare Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for Railway deployment"
git push origin main

# Verify files are present:
# - Dockerfile
# - railway.toml  
# - start.py
# - requirements.txt
```

### Step 2: Create Railway Project
1. **Go to Railway**: [railway.app](https://railway.app)
2. **Login**: Use GitHub account
3. **New Project**: "Deploy from GitHub repo"
4. **Select Repository**: Choose your Al Zait repo
5. **Branch**: Select `main` or `advanced-intelligence`

### Step 3: Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

```
TELEGRAM_BOT_TOKEN = your_telegram_bot_token
TELEGRAM_CHAT_ID = your_channel_id  
NEWSAPI_KEY = your_newsapi_key
GEMINI_API_KEY = your_gemini_key
RAILWAY = true
PORT = 8000
```

### Step 4: Deploy and Monitor
```bash
# Railway will automatically:
1. Build Docker image
2. Install dependencies  
3. Start the application
4. Provide public URL

# Monitor deployment in Railway dashboard
# Check logs for any errors
```

---

## 🐳 **Docker Configuration**

### Dockerfile Structure
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "start.py"]
```

### Railway Configuration (railway.toml)
```toml
[build]
builder = "dockerfile"

[deploy]
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 3
```

---

## 🎛️ **Service Management**

### Running Different Services

**1. Daily/Hourly News Agent:**
```bash
python main.py
```

**2. Interactive Q&A Bot:**
```bash
python run_interactive_bot.py
```

**3. One-time News Collection:**
```bash
python run_once.py
```

**4. Testing Suite:**
```bash
python test_advanced_intelligence.py
```

### Production Start Script (start.py)
The production script runs:
1. Health check web server (for Railway)
2. Main news agent with scheduled operations
3. Background cleanup tasks
4. Comprehensive error handling

---

## 📊 **Monitoring & Maintenance**

### Health Checks
Railway automatically monitors:
- **HTTP Health**: `/health` endpoint responds with 200
- **Process Health**: Main process stays running
- **Memory Usage**: Automatic restarts if memory leaks
- **Error Rates**: Logs errors for debugging

### Log Monitoring
```bash
# View Railway logs in dashboard
# Or use Railway CLI:
railway logs --follow

# Local log files:
data/al_zait.log         # Main application
data/interactive_bot.log  # Interactive bot
data/test_*.log          # Test results
```

### Automated Cleanup
The system automatically:
- **Cleans old articles**: 30 days retention in vector DB
- **Removes old audio**: 7 days retention for audio files  
- **Rotates logs**: 5MB rotation, 7 days retention
- **Optimizes database**: Weekly SQLite optimization

### Manual Maintenance
```bash
# Check system status
python -c "from main import AlZaitScheduler; AlZaitScheduler().test_configuration()"

# Clean up manually
python -c "from src.tools.vector_db_client import VectorDBClient; VectorDBClient().cleanup_old_articles()"

# Test all components
python test_advanced_intelligence.py
```

---

## 🔧 **Troubleshooting**

### Common Deployment Issues

**1. Build Failures**
```bash
# Check requirements.txt compatibility
pip install -r requirements.txt --dry-run

# Verify Python version
python --version  # Should be 3.11+

# Check Docker build locally
docker build -t al-zait-test .
```

**2. Environment Variable Issues**
```bash
# Test configuration locally
python -c "from src.utils.config import Config; print(Config.validate_config())"

# Check Railway variables
railway variables

# Verify API keys work
python -c "from src.tools.llm_client import LLMClient; print(LLMClient().test_connection())"
```

**3. Database/Storage Issues**
```bash
# Verify ChromaDB initialization
python -c "from src.tools.vector_db_client import VectorDBClient; print(VectorDBClient().test_connection())"

# Check SQLite database
python -c "from src.tools.database import NewsDatabase; print(NewsDatabase().get_statistics())"

# Clear corrupted data
rm -rf data/vector_db data/audio/*.mp3
```

**4. Telegram Bot Issues**
```bash
# Test bot token
curl https://api.telegram.org/bot<TOKEN>/getMe

# Verify chat permissions
python -c "from src.tools.telegram_client import TelegramClient; print(TelegramClient().test_connection_sync())"

# Check bot commands
python -c "from src.bots.telegram_interactive_bot import TelegramInteractiveBot; print(TelegramInteractiveBot().is_available())"
```

### Performance Optimization

**Memory Usage:**
- Monitor Railway metrics dashboard
- Reduce `MAX_CONTENT_LENGTH` if memory issues
- Implement more aggressive cleanup schedules

**API Rate Limits:**
- Gemini: 60 requests/minute (free tier)
- NewsAPI: 1000 requests/day (free tier)
- Telegram: 30 messages/second (rarely hit)

**Storage Optimization:**
- Vector DB grows ~1MB per 100 articles
- Audio files ~50KB per minute of speech
- SQLite database ~100KB per 1000 articles

---

## 🔄 **Scaling & Upgrades**

### Horizontal Scaling
For higher load, deploy multiple instances:
1. **News Collection**: Single instance (avoid duplicates)
2. **Interactive Bot**: Multiple instances (load balanced)
3. **Database**: Shared storage volume
4. **Audio Generation**: Distributed processing

### Vertical Scaling  
Railway free tier limits:
- **RAM**: 512MB (usually sufficient)
- **CPU**: Shared cores (adequate for AI processing)
- **Storage**: 1GB (monitor vector database growth)

### Future Enhancements
- **Multi-language**: Additional language models
- **Voice Input**: Speech-to-text capabilities
- **Image Processing**: Visual news analysis
- **API Endpoints**: REST API for third-party integration
- **Analytics Dashboard**: Web-based monitoring interface

---

## 📈 **Success Metrics**

### Key Performance Indicators
- **Uptime**: >99% availability
- **Response Time**: <3 seconds for Q&A
- **User Engagement**: Daily active users
- **Content Quality**: High confidence responses (>70%)
- **Audio Generation**: <10 seconds per digest

### Monitoring Tools
```bash
# Check system health
curl https://your-railway-url.railway.app/health

# Monitor bot interactions
grep "Question from" data/interactive_bot.log | wc -l

# Track success rates  
python -c "from src.bots.telegram_interactive_bot import TelegramInteractiveBot; print(TelegramInteractiveBot().get_bot_stats())"
```

---

## 🆘 **Support Resources**

### Documentation
- **Advanced Features**: `docs/ADVANCED_FEATURES.md`
- **User Guide**: `docs/USER_GUIDE.md`  
- **API Reference**: Code comments and docstrings

### Testing & Validation
- **Component Tests**: `test_advanced_intelligence.py`
- **Audio Tests**: `test_audio_features.py`
- **Integration Tests**: `test_intelligent_agents.py`

### Community & Updates
- **GitHub Issues**: Report bugs and feature requests
- **Documentation Updates**: Keep deployment guide current
- **Version Control**: Tag releases for stable deployments

---

*This deployment guide ensures successful production setup of Al Zait's advanced AI features. Follow the steps carefully and monitor the system after deployment. 🚀*
