# 🚀 Al Zait News Agent - Online Deployment Guide

Deploy your autonomous Sudan news agent to Railway for 24/7 operation (100% free).

## 📋 Prerequisites

1. **GitHub Account** (free)
2. **Railway Account** (free - sign up at [railway.app](https://railway.app))
3. **API Keys Ready**:
   - NewsAPI key from [newsapi.org](https://newsapi.org)
   - Groq API key from [console.groq.com](https://console.groq.com)
   - Telegram bot token from @BotFather
   - Your Telegram chat ID

## 🏗️ Step 1: Prepare for Deployment

### 1.1 Create GitHub Repository
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial Al Zait deployment"

# Create repository on GitHub and push
git remote add origin https://github.com/yourusername/al-zait.git
git branch -M main
git push -u origin main
```

## 🚂 Step 2: Deploy to Railway

### 2.1 Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `al-zait` repository
6. Click **"Deploy Now"**

### 2.2 Configure Environment Variables
In Railway dashboard, go to **Variables** tab and add:

```bash
# News API
NEWSAPI_KEY=your_actual_newsapi_key_here

# Groq API  
GROQ_API_KEY=your_actual_groq_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_ID=your_actual_chat_id_here

# Optional: Customize schedule
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0

# Optional: Custom search queries
SEARCH_QUERIES_AR=أخبار السودان اليوم,السياسة السودانية,الاقتصاد السوداني
SEARCH_QUERIES_EN=Sudan news today,Sudan political news,Sudan economy news

# Production settings
LOG_LEVEL=INFO
DATABASE_PATH=/app/data/news.db
```

### 2.3 Configure Service Settings
1. In Railway dashboard, go to **Settings**
2. Set **Service Name**: `al-zait-news-agent`
3. Under **Networking**, note your service URL
4. Under **Deploy**, ensure **Auto-Deploy** is enabled

## ✅ Step 3: Verify Deployment

### 3.1 Check Deployment Status
1. Monitor the **Deploy** logs in Railway dashboard
2. Look for these success messages:
   ```
   ✅ Health check server started
   ✅ Al Zait scheduler initialized  
   ✅ Configuration test passed
   🚀 Al Zait News Agent is now running...
   ```

### 3.2 Test the Health Endpoint
Visit your Railway service URL - you should see:
```
Al Zait News Agent is running
```

### 3.3 Monitor Logs
In Railway dashboard **Logs** tab, you should see:
```
📅 Daily briefing scheduled for 08:00
✅ All tests passed! Al Zait is ready to run.
🚀 Al Zait News Agent is now running...
```

## 📱 Step 4: Verify Telegram Delivery

Your agent will automatically run at 8:00 AM daily and send briefs to your Telegram.

To test immediately:
1. Check Railway logs for any errors
2. Your first brief will arrive at the next scheduled time
3. Check your Telegram for the formatted Arabic brief

## 🎯 Production Features

### ✅ What's Included:
- **24/7 Uptime**: Runs continuously on Railway
- **Auto-Restart**: Railway automatically restarts if needed  
- **Health Monitoring**: Built-in health check endpoint
- **Persistent Data**: Database stored in container
- **Error Recovery**: Robust error handling and logging
- **Zero Cost**: Completely free deployment

### 📊 Monitoring Your Agent:
- **Railway Logs**: Real-time application logs
- **Health Check**: Monitor via service URL
- **Telegram Delivery**: Daily briefs as proof of operation
- **Error Alerts**: Check Railway logs for any issues

## 🔧 Maintenance & Updates

### Update Your Agent:
1. Make changes to your local code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update Al Zait configuration"
   git push
   ```
3. Railway automatically redeploys!

### View Logs:
```bash
# Or check Railway dashboard Logs tab for real-time monitoring
```

### Scale Resources (if needed):
Railway free tier includes:
- **500 hours/month** (more than enough for daily scheduling)
- **1GB RAM**
- **1GB storage**

## 🎉 Success!

Your Al Zait News Agent is now running 24/7 online! Every morning at 8:00 AM (or your custom time), it will:

1. 🔍 Scan multiple Arabic & English news sources
2. 🤖 Process articles using AI clustering and summarization  
3. 📝 Generate neutral Arabic summaries
4. 📱 Deliver formatted briefs to your Telegram

**Your autonomous Sudan news service is now live globally! 🌍📰**

## 🆘 Troubleshooting

### Common Issues:

**❌ Build Failed**
- Check Railway logs for specific error
- Verify all files are committed to GitHub
- Ensure requirements.txt is complete

**❌ Configuration Errors**  
- Double-check all environment variables in Railway
- Verify API keys are valid and active
- Test Telegram bot token manually

**❌ No Telegram Messages**
- Verify TELEGRAM_CHAT_ID is correct (include negative sign if needed)
- Check Railway logs for delivery errors
- Ensure bot has permission to message you

**❌ Health Check Failed**
- Railway service URL should return "Al Zait News Agent is running"
- Check if service is properly starting in logs

### Get Help:
- Check Railway logs first
- Verify environment variables
- Test API keys individually
- Monitor Telegram for delivery confirmation

---

**🎊 Congratulations! Your Al Zait agent is now deployed and serving the Sudanese diaspora worldwide!**
