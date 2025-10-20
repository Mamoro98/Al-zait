#!/usr/bin/env python3
"""
Installation and setup script for Al Zait News Agent.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print Al Zait banner."""
    print("=" * 60)
    print("🗞️ Al Zait (الزيت) - Autonomous Sudan News Agent")
    print("=" * 60)
    print("Setting up your autonomous news agent...")
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python version check passed: {sys.version.split()[0]}")

def create_virtual_environment():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return
    
    print("🔧 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        sys.exit(1)

def get_venv_python():
    """Get the path to Python executable in virtual environment."""
    if os.name == 'nt':  # Windows
        return Path("venv") / "Scripts" / "python.exe"
    else:  # Unix-like systems
        return Path("venv") / "bin" / "python"

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    
    python_path = get_venv_python()
    
    try:
        subprocess.run([
            str(python_path), "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            str(python_path), "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_environment_file():
    """Setup environment configuration file."""
    env_template = Path("config") / "env.template"
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ Environment file already exists")
        return
    
    if env_template.exists():
        print("🔧 Creating environment configuration file...")
        shutil.copy(env_template, env_file)
        print("✅ Environment file created from template")
        print("⚠️  Please edit .env file with your API keys before running")
    else:
        print("⚠️  Environment template not found")

def create_data_directory():
    """Create data directory for database and logs."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")

def check_optional_dependencies():
    """Check for optional dependencies."""
    print("\n🔍 Checking optional dependencies...")
    
    # Check for Ollama
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama is installed")
        else:
            print("⚠️  Ollama not found - install for local LLM support")
            print("   Install: curl -fsSL https://ollama.ai/install.sh | sh")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Ollama not found - install for local LLM support")
    
    # Check for Docker
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker is available")
        else:
            print("ℹ️  Docker not found - optional for deployment")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("ℹ️  Docker not found - optional for deployment")

def run_basic_test():
    """Run basic configuration test."""
    print("\n🧪 Running basic test...")
    
    python_path = get_venv_python()
    
    try:
        # Test imports
        result = subprocess.run([
            str(python_path), "-c", 
            "import sys; sys.path.append('src'); from src.utils.config import Config; print('✅ Basic imports successful')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"⚠️  Basic test failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️  Basic test timed out")
    except Exception as e:
        print(f"⚠️  Basic test error: {e}")

def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 Installation completed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. 📝 Edit .env file with your API keys:")
    print("   - NewsAPI key (free at newsapi.org)")
    print("   - Groq API key (free at console.groq.com)")
    print("   - Telegram bot token (create with @BotFather)")
    print()
    print("2. 🧪 Test your configuration:")
    if os.name == 'nt':
        print("   venv\\Scripts\\python main.py --test")
    else:
        print("   source venv/bin/activate")
        print("   python main.py --test")
    print()
    print("3. 🚀 Run your first brief:")
    if os.name == 'nt':
        print("   venv\\Scripts\\python run_once.py --run-full")
    else:
        print("   python run_once.py --run-full")
    print()
    print("4. 📅 Start automated scheduling:")
    if os.name == 'nt':
        print("   venv\\Scripts\\python main.py --schedule")
    else:
        print("   python main.py --schedule")
    print()
    print("📚 For detailed instructions, see README.md")
    print("🆘 For help, visit: https://github.com/your-username/al-zait/issues")
    print()

def main():
    """Main installation function."""
    print_banner()
    
    try:
        check_python_version()
        create_virtual_environment()
        install_dependencies()
        setup_environment_file()
        create_data_directory()
        check_optional_dependencies()
        run_basic_test()
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
