# 🚂 Al Zait Railway Deployment Guide

## ✅ READY FOR DEPLOYMENT!

Your Al Zait system is now optimized for Railway's free tier (<4GB limit).

---

## 🚀 STEP-BY-STEP DEPLOYMENT

### **Step 1: Push to GitHub**
```bash
# Push the railway-optimized branch to your GitHub
git push origin railway-optimized

# If you get permission errors, make sure you're authenticated:
git remote -v  # Check your repository URL
```

### **Step 2: Railway Setup**
1. **Go to**: [railway.app](https://railway.app)
2. **Login**: Use your GitHub account
3. **New Project**: Click "Deploy from GitHub repo"
4. **Select Repository**: Choose your Al Zait repository
5. **Select Branch**: Choose `railway-optimized` (IMPORTANT!)

### **Step 3: Configure Railway Build**
In Railway dashboard, go to **Settings > Build**:
- **Dockerfile Path**: `Dockerfile.railway`
- **Build Command**: (leave default)
- **Start Command**: `python start-railway.py`

### **Step 4: Set Environment Variables**
In Railway dashboard, go to **Variables** tab and add these:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_telegram_channel_id
NEWSAPI_KEY=your_newsapi_key_from_newsapi.org
GEMINI_API_KEY=your_gemini_api_key_from_ai.google.dev
RAILWAY=true
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=600
SCHEDULE_MINUTE=0
```

### **Step 5: Deploy!**
1. **Click Deploy**: Railway will automatically build and deploy
2. **Monitor Logs**: Watch the deployment progress
3. **Check Health**: Your app will be available at the Railway URL

---

## 🔑 GET YOUR API KEYS

### **Telegram Bot Token:**
```
1. Message @BotFather on Telegram
2. Send: /newbot
3. Name: "Al Zait News Bot"
4. Username: "YourAlZaitBot" (must be unique)
5. Copy the token provided
```

### **Telegram Chat ID:**
```bash
# Method 1: For a channel
1. Create Telegram channel
2. Add your bot as admin
3. Get channel ID (starts with @)

# Method 2: Use this API call
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

### **NewsAPI Key:**
```
1. Go to: https://newsapi.org/register
2. Create free account (1000 requests/day)
3. Copy API key from dashboard
```

### **Gemini API Key:**
```
1. Go to: https://ai.google.dev
2. Create Google Cloud project
3. Enable Gemini API
4. Generate API key
5. Free tier: 60 requests/minute
```

---

## 📊 WHAT YOU'LL GET

### **🌟 Railway-Optimized Features:**
✅ **News Collection**: Hourly collection from multiple sources  
✅ **Crisis Detection**: AI-powered urgency scoring  
✅ **Daily Digest**: Intelligent morning summary  
✅ **Interactive Q&A**: Users can chat with the bot  
✅ **Audio Briefings**: Text-to-speech in Arabic  
✅ **Smart Search**: Lightweight text similarity search  
✅ **Multi-language**: Arabic and English support  
✅ **Source Attribution**: Confidence scores and citations  

### **📦 Technical Specs:**
- **Docker Image**: ~2GB (fits Railway free tier)
- **Memory Usage**: ~200MB (well under 512MB limit)  
- **Monthly Cost**: $0.00 (completely free)
- **Uptime**: 24/7 automatic operation
- **Scaling**: Auto-restart on failures

---

## 🔧 TROUBLESHOOTING

### **Build Fails:**
```bash
# Check these in Railway dashboard:
1. Dockerfile path: "Dockerfile.railway" 
2. Branch: "railway-optimized"
3. Build logs for specific errors
```

### **Environment Variables:**
```bash
# Make sure all required variables are set:
echo $TELEGRAM_BOT_TOKEN  # Should not be empty
echo $GEMINI_API_KEY      # Should not be empty
```

### **Bot Not Responding:**
```bash
# Test your bot token:
curl https://api.telegram.org/bot<TOKEN>/getMe

# Check Railway logs for errors
```

---

## 🎯 SUCCESS METRICS

Once deployed successfully, you should see:

### **Railway Logs:**
```
✅ Configuration validated successfully
🚂 Railway deployment mode detected  
⚡ Lightweight mode: Railway-optimized features
🏥 Health check server started on port 8000
🚀 Starting Al Zait news agent...
📅 Hourly briefing scheduled for every hour at minute 00
```

### **Telegram Bot:**
- Bot responds to `/start` command
- Users can ask questions and get intelligent answers
- Daily digest posted at scheduled time
- Audio briefings available on request

### **Health Check:**
- Visit your Railway app URL + `/health`
- Should return JSON with status: "healthy"

---

## 🎉 CONGRATULATIONS!

Once deployed, you'll have a **world-class AI news intelligence platform** running 24/7 for **absolutely free**!

Your users can:
- Chat with the bot directly for Q&A
- Get daily intelligent news digests  
- Request audio versions of news
- Access multi-language support
- Enjoy professional source attribution

**This is a truly impressive portfolio project!** 🌟
