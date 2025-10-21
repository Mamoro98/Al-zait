#!/bin/bash

# Al Zait News Agent - Quick Deployment Script
# Usage: ./deploy.sh [environment]
# Environments: dev, staging, prod (default: prod)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="omer-project-437509"
REGION="us-central1"
ENVIRONMENT=${1:-prod}

# Environment-specific settings
case $ENVIRONMENT in
  "dev")
    SERVICE_NAME="al-zait-dev"
    MEMORY="2Gi"
    CPU="1"
    MIN_INSTANCES="0"
    MAX_INSTANCES="3"
    ML_ENABLED="false"
    ;;
  "staging")
    SERVICE_NAME="al-zait-staging"
    MEMORY="4Gi"
    CPU="2"
    MIN_INSTANCES="0"
    MAX_INSTANCES="5"
    ML_ENABLED="true"
    ;;
  "prod")
    SERVICE_NAME="al-zait-news-agent"
    MEMORY="4Gi"
    CPU="2"
    MIN_INSTANCES="0"
    MAX_INSTANCES="10"
    ML_ENABLED="true"
    ;;
  *)
    echo -e "${RED}Invalid environment: $ENVIRONMENT${NC}"
    echo "Usage: $0 [dev|staging|prod]"
    exit 1
    ;;
esac

echo -e "${BLUE}🚀 Deploying Al Zait to $ENVIRONMENT environment${NC}"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not authenticated with gcloud${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop"
    exit 1
fi

# Build image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
IMAGE_TAG="gcr.io/$PROJECT_ID/al-zait:$(git rev-parse --short HEAD)"
LATEST_TAG="gcr.io/$PROJECT_ID/al-zait:latest"

docker build -f Dockerfile.gcp -t "$IMAGE_TAG" -t "$LATEST_TAG" .

# Push image
echo -e "${YELLOW}📤 Pushing image to Container Registry...${NC}"
gcloud auth configure-docker
docker push "$IMAGE_TAG"
docker push "$LATEST_TAG"

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run ($ENVIRONMENT)...${NC}"

if [ "$ENVIRONMENT" = "dev" ]; then
    # Simple deployment for development
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE_TAG" \
        --region "$REGION" \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory "$MEMORY" \
        --cpu "$CPU" \
        --timeout 3600 \
        --min-instances "$MIN_INSTANCES" \
        --max-instances "$MAX_INSTANCES" \
        --set-env-vars "GOOGLE_CLOUD=true,GCP_CLOUD_RUN=true,ML_ENABLED=$ML_ENABLED,LOG_LEVEL=DEBUG"
else
    # Full deployment with secrets for staging/production
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE_TAG" \
        --region "$REGION" \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory "$MEMORY" \
        --cpu "$CPU" \
        --timeout 3600 \
        --concurrency 160 \
        --min-instances "$MIN_INSTANCES" \
        --max-instances "$MAX_INSTANCES" \
        --set-env-vars "GOOGLE_CLOUD=true,GCP_CLOUD_RUN=true,ML_ENABLED=$ML_ENABLED,VECTOR_DB_ENABLED=true,ADVANCED_AUDIO_ENABLED=true,LOG_LEVEL=INFO,SCHEDULE_MINUTE=0,GCP_MODE=both,PYTHONUNBUFFERED=1,PYTHONPATH=/app/src,OMP_NUM_THREADS=2,TOKENIZERS_PARALLELISM=false" \
        --update-secrets "TELEGRAM_BOT_TOKEN=telegram-bot-token:latest,TELEGRAM_CHAT_ID=telegram-chat-id:latest,GROQ_API_KEY=groq-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest,NEWSAPI_KEY=newsapi-key:latest"
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(status.url)')

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"

# Test health endpoint
echo -e "${YELLOW}🏥 Testing health endpoint...${NC}"
sleep 10

if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed, but service may still be starting...${NC}"
fi

echo ""
echo -e "${BLUE}📋 Useful commands:${NC}"
echo "View logs: gcloud logs read \"resource.type=cloud_run_revision\" --limit=50 --project=$PROJECT_ID"
echo "Service info: gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "Update service: gcloud run services update $SERVICE_NAME --region=$REGION"

echo ""
echo -e "${GREEN}🎉 Al Zait deployment complete!${NC}"
