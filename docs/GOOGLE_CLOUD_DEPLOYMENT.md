# 🚀 Al Zait - Google Cloud Platform Deployment

Deploy the **FULL Al Zait News Agent** on Google Cloud Platform with Cloud Run!

## 🎯 Why Google Cloud Platform?

| Feature | Railway Free | Google Cloud | Winner |
|---------|-------------|-------------|---------|
| **Memory** | 4GB | **Up to 8GB** | 🥇 Google Cloud |
| **Storage** | Limited | **Persistent + Cloud Storage** | 🥇 Google Cloud |
| **Compute** | Limited | **Auto-scaling + 4 vCPUs** | 🥇 Google Cloud |
| **Free Credits** | Limited | **$300 + Always Free** | 🥇 Google Cloud |
| **ML/AI Support** | Basic | **Native AI/ML Integration** | 🥇 Google Cloud |
| **Scalability** | Fixed | **Serverless Auto-scaling** | 🥇 Google Cloud |

## 📋 Prerequisites

- Google Cloud account with billing enabled
- Google Cloud CLI (`gcloud`) installed
- Docker installed locally
- Your Al Zait API keys:
  - Telegram Bot Token
  - Groq API Key
  - Gemini API Key
  - NewsAPI Key

## 🔧 Step 1: Google Cloud Setup

### 1.1 Create Google Cloud Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign up and get **$300 free credits**
3. Create a new project or select existing one
4. Enable billing (required for Cloud Run)

### 1.2 Install Google Cloud CLI
```bash
# Windows (PowerShell)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe

# macOS
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 1.3 Initialize gcloud
```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## 🛠️ Step 2: Configure Your Project

### 2.1 Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/Al-zait.git
cd Al-zait
```

### 2.2 Create Environment Configuration
```bash
# Copy the template
cp env.gcp.template .env

# Edit with your API keys
nano .env
```

Fill in your API keys:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
NEWSAPI_KEY=your_newsapi_key
```

### 2.3 Make Deployment Script Executable
```bash
chmod +x deploy-gcp.sh
```

## 🚀 Step 3: Deploy to Google Cloud

### 3.1 Run Automated Deployment
```bash
./deploy-gcp.sh
```

This script will:
- ✅ Enable required Google Cloud APIs
- 🏗️ Build and push Docker image to Container Registry
- 🔐 Create secrets in Secret Manager
- 🚀 Deploy to Cloud Run
- 🌐 Configure public access
- 🏥 Test health endpoint

### 3.2 Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
# Set your project ID
PROJECT_ID="your-project-id"
REGION="us-central1"

# Build and push image
docker build -f Dockerfile.gcp -t gcr.io/$PROJECT_ID/al-zait:latest .
docker push gcr.io/$PROJECT_ID/al-zait:latest

# Create secrets
echo -n "YOUR_TELEGRAM_BOT_TOKEN" | gcloud secrets create telegram-bot-token --data-file=-
echo -n "YOUR_TELEGRAM_CHAT_ID" | gcloud secrets create telegram-chat-id --data-file=-
echo -n "YOUR_GROQ_API_KEY" | gcloud secrets create groq-api-key --data-file=-
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
echo -n "YOUR_NEWSAPI_KEY" | gcloud secrets create newsapi-key --data-file=-

# Update cloud-run.yaml with your project ID
sed "s/PROJECT_ID/$PROJECT_ID/g" cloud-run.yaml > cloud-run-deploy.yaml

# Deploy to Cloud Run
gcloud run services replace cloud-run-deploy.yaml --region=$REGION

# Make service publicly accessible
gcloud run services add-iam-policy-binding al-zait-news-agent \
    --region=$REGION \
    --member="allUsers" \
    --role="roles/run.invoker"
```

## 🔍 Step 4: Verify Deployment

### 4.1 Get Service URL
```bash
gcloud run services describe al-zait-news-agent --region=us-central1 --format='value(status.url)'
```

### 4.2 Test Health Endpoint
```bash
curl https://YOUR-SERVICE-URL/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX...",
  "platform": "Google Cloud Platform",
  "service": "Cloud Run",
  "deployment_mode": "Full",
  "ai_capabilities": "Advanced",
  "features": {
    "vector_database": true,
    "advanced_rag": true,
    "intelligent_agents": true,
    "multimedia_brief": true,
    "interactive_analyst": true,
    "cloud_run_optimized": true
  }
}
```

### 4.3 Test Telegram Bot
1. Open Telegram
2. Find your bot by username
3. Send: `/start`
4. Send: `ما هو الوضع الاقتصادي في السودان؟`
5. You should get intelligent Arabic responses!

## 📊 Step 5: Monitoring and Management

### 5.1 View Logs
```bash
# Recent logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50 --region=us-central1

# Follow logs in real-time
gcloud logs tail "resource.type=cloud_run_revision" --region=us-central1
```

### 5.2 Monitor Performance
Visit [Cloud Run Console](https://console.cloud.google.com/run) to monitor:
- 📊 Request volume and latency
- 🔧 CPU and memory usage
- 🚨 Error rates and alerts
- 💰 Cost breakdown

### 5.3 Update Deployment
```bash
# Pull latest changes
git pull

# Redeploy (builds new image automatically)
./deploy-gcp.sh
```

## 🔐 Step 6: Security and Secrets Management

### 6.1 Update Secrets
```bash
# Update a secret
echo -n "NEW_SECRET_VALUE" | gcloud secrets versions add SECRET_NAME --data-file=-

# View secret versions
gcloud secrets versions list SECRET_NAME
```

### 6.2 Configure IAM (Optional)
```bash
# Create service account for the application
gcloud iam service-accounts create al-zait-service-account

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:al-zait-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 🎛️ Step 7: Advanced Configuration

### 7.1 Custom Domain (Optional)
1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click your service → **Manage Custom Domains**
3. Add your domain and verify ownership
4. Update DNS records as instructed

### 7.2 Auto-scaling Configuration
Edit `cloud-run.yaml` to adjust:
```yaml
annotations:
  # Minimum instances (0 for cost savings)
  autoscaling.knative.dev/minScale: "0"
  # Maximum instances
  autoscaling.knative.dev/maxScale: "100"
  # Memory allocation
  run.googleapis.com/memory: "4Gi"
  # CPU allocation  
  run.googleapis.com/cpu: "2"
```

### 7.3 Environment-specific Deployment
```bash
# Production deployment
GCP_MODE=both ./deploy-gcp.sh

# Bot-only deployment
GCP_MODE=bot ./deploy-gcp.sh

# Agents-only deployment  
GCP_MODE=agents ./deploy-gcp.sh
```

## 💡 Features Enabled on Google Cloud

✅ **Full Vector Database**: ChromaDB with sentence-transformers  
✅ **Advanced RAG**: Intelligent article retrieval and synthesis  
✅ **Multimedia Briefings**: Audio generation with intro/outro  
✅ **Smart Clustering**: ML-powered event grouping  
✅ **Crisis Detection**: Real-time urgency scoring  
✅ **Interactive Analysis**: Conversational Q&A with context  
✅ **Multi-language Support**: Arabic and English processing  
✅ **Intelligent Agents**: Collector and Editor working in harmony  
✅ **Auto-scaling**: Handles traffic spikes automatically  
✅ **Global CDN**: Fast response times worldwide  

## 🔧 Troubleshooting

### Common Issues

**Build failures:**
```bash
# Check build logs
gcloud builds log --region=global BUILD_ID

# Clear Docker cache
docker system prune -a
```

**Service not responding:**
```bash
# Check service status
gcloud run services describe al-zait-news-agent --region=us-central1

# Check recent logs
gcloud logs read "resource.type=cloud_run_revision" --limit=20
```

**Memory issues:**
- Increase memory in `cloud-run.yaml` (up to 8Gi)
- Optimize model loading in startup

**Cold starts:**
- Set `minScale: "1"` to keep one instance warm
- Implement warm-up endpoints

### Performance Optimization

**For high traffic:**
```yaml
# In cloud-run.yaml
annotations:
  run.googleapis.com/memory: "8Gi"
  run.googleapis.com/cpu: "4"
  autoscaling.knative.dev/minScale: "2"
  autoscaling.knative.dev/maxScale: "100"
```

**Cost optimization:**
```yaml
# In cloud-run.yaml
annotations:
  run.googleapis.com/memory: "2Gi"
  run.googleapis.com/cpu: "1"
  autoscaling.knative.dev/minScale: "0"
  autoscaling.knative.dev/maxScale: "10"
```

## 💰 Cost Management

### Free Tier Limits
- **Cloud Run**: 2 million requests/month FREE
- **Secret Manager**: 6 secrets FREE
- **Container Registry**: 0.5GB storage FREE
- **Cloud Logging**: 50GB logs/month FREE

### Cost Estimation
For typical usage:
- **Light usage** (< 1000 requests/day): $0-5/month
- **Medium usage** (< 10k requests/day): $5-20/month  
- **Heavy usage** (< 100k requests/day): $20-100/month

### Cost Optimization Tips
1. Set appropriate `minScale` (0 for cost, 1+ for performance)
2. Use efficient memory allocation
3. Implement caching to reduce compute time
4. Monitor usage in Cloud Console

## 🚀 Next Steps

1. **Custom Domain**: Set up your own domain
2. **CI/CD Pipeline**: Automate deployments with Cloud Build
3. **Monitoring**: Set up Cloud Monitoring alerts
4. **Backup Strategy**: Implement data backup to Cloud Storage
5. **Load Testing**: Test performance under load

## 🎯 Google Cloud Advantages

- **🔄 Auto-scaling**: Scales to zero when not in use
- **🌍 Global**: Deploy to regions worldwide
- **🔒 Security**: Built-in security and compliance
- **🤖 AI Integration**: Native ML/AI services
- **💰 Cost-effective**: Pay only for actual usage
- **📊 Monitoring**: Advanced logging and monitoring
- **🚀 Performance**: Fast cold starts and execution

---

🎯 **Your Al Zait News Agent is now running on Google Cloud Platform!**

The system will:
- 🕐 Collect news every hour
- 📰 Generate intelligent digest daily at 8 AM  
- 🤖 Respond to user questions instantly
- 🎙️ Create audio briefings
- 🧠 Use advanced AI for analysis
- 🔄 Scale automatically with demand

**Cost: $0-20/month for typical usage** 🎉

Visit your service URL to see it in action!
