#!/usr/bin/env python3
"""
Al Zait News Agent - Deployment Helper Script
Helps prepare the project for Railway deployment.
"""

import os
import subprocess
import sys
from pathlib import Path

def print_banner():
    """Print deployment banner."""
    print("=" * 60)
    print("🚀 Al Zait News Agent - Deployment Helper")
    print("=" * 60)
    print()

def check_git():
    """Check if git is available and repository is initialized."""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("❌ Git is not installed. Please install Git first.")
            return False
        
        print(f"✅ Git available: {result.stdout.strip()}")
        
        # Check if git repo is initialized
        if not Path(".git").exists():
            print("📁 Initializing Git repository...")
            subprocess.run(["git", "init"], check=True)
            print("✅ Git repository initialized")
        
        return True
    
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is not available. Please install Git first.")
        return False

def check_required_files():
    """Check if all required deployment files exist."""
    required_files = [
        "Dockerfile",
        "railway.toml", 
        "start.py",
        "requirements.txt",
        "main.py",
        "src/agents/news_agent.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required deployment files present")
    return True

def create_gitignore():
    """Create .gitignore for the repository."""
    gitignore_content = """# Al Zait - Git ignore file

# Environment variables (security)
.env
.env.local
.env.production

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
ENV/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
Desktop.ini

# Local data files
data/*.db
data/*.log
*.log

# Test and development files
test_*.py
run_once.py

# Temporary files
*.tmp
.tmp/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")

def prepare_repository():
    """Prepare the repository for deployment."""
    try:
        # Create .gitignore if it doesn't exist
        if not Path(".gitignore").exists():
            create_gitignore()
        
        # Add all files
        print("📦 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        
        if result.stdout.strip():
            # Commit changes
            print("💾 Committing changes...")
            subprocess.run([
                "git", "commit", "-m", "Prepare Al Zait for Railway deployment"
            ], check=True)
            print("✅ Changes committed successfully")
        else:
            print("✅ Repository is up to date")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False

def show_deployment_instructions():
    """Show next steps for deployment."""
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS - Deploy to Railway")
    print("=" * 60)
    print()
    print("1. 📁 Push to GitHub:")
    print("   - Create a new repository on GitHub.com")
    print("   - Copy the git remote URL")
    print("   - Run these commands:")
    print()
    print("   git remote add origin https://github.com/yourusername/al-zait.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("2. 🚂 Deploy on Railway:")
    print("   - Go to https://railway.app")
    print("   - Sign in with GitHub")
    print("   - Click 'New Project' → 'Deploy from GitHub repo'")
    print("   - Select your al-zait repository")
    print("   - Click 'Deploy Now'")
    print()
    print("3. ⚙️ Set Environment Variables in Railway:")
    print("   - Go to your project → Variables tab")
    print("   - Add these variables:")
    print("     * NEWSAPI_KEY=your_newsapi_key")
    print("     * GROQ_API_KEY=your_groq_key") 
    print("     * TELEGRAM_BOT_TOKEN=your_bot_token")
    print("     * TELEGRAM_CHAT_ID=your_chat_id")
    print()
    print("4. ✅ Verify Deployment:")
    print("   - Check Railway logs for success messages")
    print("   - Visit your Railway service URL")
    print("   - Should show: 'Al Zait News Agent is running'")
    print()
    print("📚 For detailed instructions, see: DEPLOYMENT.md")
    print()
    print("🎉 Your Al Zait agent will then run 24/7 online!")

def main():
    """Main deployment preparation function."""
    print_banner()
    
    # Check prerequisites
    if not check_git():
        sys.exit(1)
    
    if not check_required_files():
        print("❌ Please ensure all required files are present before deploying.")
        sys.exit(1)
    
    # Prepare repository
    if not prepare_repository():
        print("❌ Failed to prepare repository for deployment.")
        sys.exit(1)
    
    # Show next steps
    show_deployment_instructions()
    
    print("🚀 Repository is ready for Railway deployment!")

if __name__ == "__main__":
    main()
