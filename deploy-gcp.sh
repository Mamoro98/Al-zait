#!/bin/bash
# Google Cloud Platform Deployment Script for Al Zait

set -e  # Exit on any error

echo "🚀 Deploying Al Zait to Google Cloud Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"  # Change to your preferred region
SERVICE_NAME="al-zait-news-agent"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI not found!"
    echo "📦 Please install gcloud CLI first: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker not found!"
    echo "📦 Please install Docker first"
    exit 1
fi

# Get project ID if not set
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        print_error "No Google Cloud project found!"
        echo "Please set your project: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
fi

print_status "Using project: $PROJECT_ID"
print_status "Using region: $REGION"

# Check if .env exists (for local testing)
if [ ! -f ".env.gcp" ]; then
    print_warning ".env.gcp file not found!"
    echo "📝 Please create .env.gcp with your API keys for local testing"
    echo "For production, we'll use Google Cloud Secret Manager"
fi

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

print_success "APIs enabled"

# Build and push Docker image
print_status "Building Docker image..."
docker build -f Dockerfile.gcp -t gcr.io/$PROJECT_ID/al-zait:latest .

print_status "Pushing image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/al-zait:latest

print_success "Image pushed successfully"

# Create secrets (if they don't exist)
print_status "Setting up secrets in Secret Manager..."

# Function to create secret if it doesn't exist
create_secret_if_not_exists() {
    SECRET_NAME=$1
    if ! gcloud secrets describe $SECRET_NAME &>/dev/null; then
        print_status "Creating secret: $SECRET_NAME"
        echo "Please enter your $SECRET_NAME:"
        read -s SECRET_VALUE
        echo -n "$SECRET_VALUE" | gcloud secrets create $SECRET_NAME --data-file=-
        print_success "Secret $SECRET_NAME created"
    else
        print_status "Secret $SECRET_NAME already exists"
    fi
}

# Create secret manager secrets
create_secret_if_not_exists "telegram-bot-token"
create_secret_if_not_exists "telegram-chat-id"
create_secret_if_not_exists "groq-api-key"
create_secret_if_not_exists "gemini-api-key"
create_secret_if_not_exists "newsapi-key"

# Update cloud-run.yaml with correct project ID
print_status "Updating Cloud Run configuration..."
sed "s/PROJECT_ID/$PROJECT_ID/g" cloud-run.yaml > cloud-run-deploy.yaml

# Deploy to Cloud Run
print_status "Deploying to Cloud Run..."
gcloud run services replace cloud-run-deploy.yaml --region=$REGION

# Make service publicly accessible (for health checks and webhook)
print_status "Configuring public access..."
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --region=$REGION \
    --member="allUsers" \
    --role="roles/run.invoker"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

print_success "Deployment completed!"
print_success "Service URL: $SERVICE_URL"
print_success "Health check: $SERVICE_URL/health"

# Test deployment
print_status "Testing deployment..."
sleep 30  # Wait for service to start

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/health)

if [ "$HEALTH_STATUS" = "200" ]; then
    print_success "Health check passed!"
    echo "🌐 Your Al Zait service is running at: $SERVICE_URL"
    echo "📱 Test your Telegram bot now!"
    echo "🎯 To update your Telegram bot webhook (if using webhooks):"
    echo "   Set webhook URL to: $SERVICE_URL/webhook"
else
    print_warning "Health check returned HTTP $HEALTH_STATUS"
    print_status "Checking logs..."
    gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=20 --region=$REGION
fi

# Cleanup temporary file
rm -f cloud-run-deploy.yaml

print_success "Deployment script completed!"

echo ""
echo "🔧 Next steps:"
echo "1. Test your service: curl $SERVICE_URL/health"
echo "2. Check logs: gcloud logs read \"resource.type=cloud_run_revision\" --limit=50 --region=$REGION"
echo "3. Monitor usage: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
echo "4. Update secrets: gcloud secrets versions add SECRET_NAME --data-file=-"
