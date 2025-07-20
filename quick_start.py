#!/usr/bin/env python3
"""
FortiGate Enterprise Platform - Quick Start Script
Helps initialize and start the unified application
"""

import os
import subprocess
import sys
from pathlib import Path
import json

def quick_start():
    """Quick start the FortiGate Enterprise Platform"""
    
    app_path = Path("C:/Users/south/FortiGate-Enterprise-Platform")
    
    if not app_path.exists():
        print("[ERROR] FortiGate Enterprise Platform not found!")
        print("Please run the consolidation script first.")
        return
    
    print("🚀 FortiGate Enterprise Platform - Quick Start")
    print("=" * 50)
    
    # Check prerequisites
    check_prerequisites()
    
    # Initialize project
    initialize_project(app_path)
    
    # Create environment files
    create_environment_files(app_path)
    
    # Install dependencies
    install_dependencies(app_path)
    
    # Start services
    start_services(app_path)

def check_prerequisites():
    """Check if required tools are installed"""
    print("\n📋 Checking prerequisites...")
    
    # Check Python
    try:
        python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
        print(f"✅ Python: {python_version}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print(f"✅ Node.js: {node_version}")
    except:
        print("❌ Node.js not found - install from https://nodejs.org")
    
    # Check Docker
    try:
        docker_version = subprocess.check_output(["docker", "--version"], text=True).strip()
        print(f"✅ Docker: {docker_version}")
    except:
        print("⚠️  Docker not found - Docker deployment will not be available")
    
    print("✅ Prerequisites check complete")

def initialize_project(app_path):
    """Initialize the project with Git and basic setup"""
    print("\n🔧 Initializing project...")
    
    os.chdir(app_path)
    
    # Initialize Git if not already done
    if not (app_path / ".git").exists():
        try:
            subprocess.run(["git", "init"], check=True, capture_output=True)
            print("✅ Git repository initialized")
        except:
            print("⚠️  Git initialization failed")
    
    # Create .gitignore if it doesn't exist
    gitignore_path = app_path / ".gitignore"
    if not gitignore_path.exists():
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
env/

# Environment files
.env
.env.local
.env.production

# Build outputs
/build
/dist
*.egg-info/

# IDE files
.vscode/
.idea/
*.swp

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.sqlite
*.db

# Secrets
secrets/
*.pem
*.key
"""
        gitignore_path.write_text(gitignore_content)
        print("✅ .gitignore created")

def create_environment_files(app_path):
    """Create environment configuration files"""
    print("\n⚙️ Creating environment files...")
    
    # Backend .env
    backend_env = app_path / "backend" / ".env"
    if not backend_env.exists():
        env_content = """# Database Configuration
DATABASE_URL=postgresql://admin:password@localhost:5432/fortigate_enterprise

# API Configuration
SECRET_KEY=your-secret-key-change-in-production
API_V1_STR=/api/v1

# Power Automate Configuration
POWER_AUTOMATE_ENABLED=true
POWER_AUTOMATE_WEBHOOK_URL=https://your-power-automate-webhook-url

# Security Configuration
SCAN_TIMEOUT=30
MAX_CONCURRENT_SCANS=100
DEFAULT_SCAN_RANGE=192.168.1.0/24

# External Services
VULNERABILITY_DATABASE_URL=https://nvd.nist.gov/feeds/json/cve/1.1/
OUI_DATABASE_URL=https://standards-oui.ieee.org/oui/oui.txt
"""
        backend_env.write_text(env_content)
        print("✅ Backend .env created")
    
    # Frontend .env
    frontend_env = app_path / "frontend" / ".env"
    if not frontend_env.exists():
        env_content = """# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Application Configuration
REACT_APP_NAME=FortiGate Enterprise Platform
REACT_APP_VERSION=1.0.0
"""
        frontend_env.write_text(env_content)
        print("✅ Frontend .env created")

def install_dependencies(app_path):
    """Install project dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Backend dependencies
    backend_path = app_path / "backend"
    if (backend_path / "requirements.txt").exists():
        try:
            os.chdir(backend_path)
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Backend dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Backend dependency installation failed: {e}")
    
    # Frontend dependencies
    frontend_path = app_path / "frontend"
    if (frontend_path / "package.json").exists():
        try:
            os.chdir(frontend_path)
            subprocess.run(["npm", "install"], check=True, capture_output=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Frontend dependency installation failed: {e}")
    
    os.chdir(app_path)

def start_services(app_path):
    """Start the application services"""
    print("\n🚀 Starting services...")
    
    # Check if Docker is available and docker-compose.yml exists
    if (app_path / "docker-compose.yml").exists():
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            print("\n🐳 Starting with Docker...")
            print("Run: docker-compose up -d")
            print("Services will be available at:")
            print("  - Frontend: http://localhost:3000")
            print("  - Backend API: http://localhost:8000")
            print("  - API Docs: http://localhost:8000/api/docs")
        except:
            print("\n📝 Manual startup instructions:")
            print("Backend:")
            print("  cd backend")
            print("  python main.py")
            print("\nFrontend (new terminal):")
            print("  cd frontend") 
            print("  npm start")
    else:
        print("\n📝 Manual startup instructions:")
        print("Backend:")
        print("  cd backend")
        print("  python main.py")
        print("\nFrontend (new terminal):")
        print("  cd frontend")
        print("  npm start")

def show_power_automate_setup():
    """Show Power Automate setup instructions"""
    print("\n🤖 Power Automate Setup")
    print("=" * 30)
    print("1. Create a new Power Automate flow")
    print("2. Add 'When an HTTP request is received' trigger")
    print("3. Copy the webhook URL")
    print("4. Update POWER_AUTOMATE_WEBHOOK_URL in backend/.env")
    print("5. Configure your automation workflows")
    print("\nExample workflows available in automation/power_automate/")

def main():
    """Main function"""
    try:
        quick_start()
        show_power_automate_setup()
        
        print("\n✅ Quick start complete!")
        print("\n🎯 Next Steps:")
        print("1. Start the services using the instructions above")
        print("2. Configure Power Automate webhooks")
        print("3. Access the application at http://localhost:3000")
        print("4. Check API documentation at http://localhost:8000/api/docs")
        print("\n📚 See CONSOLIDATION_SUMMARY.md for detailed information")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")

if __name__ == "__main__":
    main()
