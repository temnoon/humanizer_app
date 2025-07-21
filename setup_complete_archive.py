#!/usr/bin/env python3
"""
Complete Archive Setup Script
Sets up PostgreSQL with pgvector, pulls Ollama models, and configures the entire system
"""

import asyncio
import subprocess
import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ArchiveSetupManager:
    """Comprehensive setup manager for the archive system"""
    
    def __init__(self):
        self.setup_status = {
            "postgresql_setup": False,
            "pgvector_installed": False,
            "ollama_running": False,
            "nomic_model_ready": False,
            "database_created": False,
            "python_deps_installed": False,
            "archive_api_tested": False,
            "lighthouse_ui_ready": False
        }
        self.status_file = Path("archive_setup_status.json")
        self.load_status()
    
    def load_status(self):
        """Load previous setup status"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    saved_status = json.load(f)
                self.setup_status.update(saved_status)
                logger.info("📥 Loaded previous setup status")
            except Exception as e:
                logger.warning(f"Could not load setup status: {e}")
    
    def save_status(self):
        """Save current setup status"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.setup_status, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save setup status: {e}")
    
    def run_command(self, command: str, description: str, check_success: bool = True) -> bool:
        """Run a shell command with logging"""
        logger.info(f"🔧 {description}...")
        logger.debug(f"Running: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {description} completed successfully")
                if result.stdout.strip():
                    logger.debug(f"Output: {result.stdout.strip()}")
                return True
            else:
                if check_success:
                    logger.error(f"❌ {description} failed")
                    logger.error(f"Error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {description} timed out")
            return False
        except Exception as e:
            logger.error(f"❌ {description} failed with exception: {e}")
            return False
    
    def check_postgresql(self) -> bool:
        """Check if PostgreSQL is installed and running"""
        logger.info("🔍 Checking PostgreSQL installation...")
        
        # Check if psql is available
        if not self.run_command("which psql", "Finding psql", check_success=False):
            logger.error("❌ PostgreSQL not found. Please install PostgreSQL first:")
            logger.error("   macOS: brew install postgresql")
            logger.error("   Ubuntu: sudo apt install postgresql postgresql-contrib")
            return False
        
        # Check if PostgreSQL is running
        if not self.run_command("pg_isready", "Checking PostgreSQL status", check_success=False):
            logger.warning("⚠️  PostgreSQL not running, attempting to start...")
            if self.run_command("brew services start postgresql", "Starting PostgreSQL", check_success=False):
                time.sleep(3)  # Wait for startup
                if self.run_command("pg_isready", "Rechecking PostgreSQL", check_success=False):
                    self.setup_status["postgresql_setup"] = True
                    return True
            logger.error("❌ Could not start PostgreSQL. Please start it manually:")
            logger.error("   macOS: brew services start postgresql")
            logger.error("   Linux: sudo systemctl start postgresql")
            return False
        
        self.setup_status["postgresql_setup"] = True
        return True
    
    def setup_pgvector(self) -> bool:
        """Install and configure pgvector extension"""
        if self.setup_status["pgvector_installed"]:
            logger.info("✅ pgvector already installed")
            return True
        
        logger.info("🔧 Setting up pgvector extension...")
        
        # Check if pgvector is available
        test_result = subprocess.run(
            'psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if "already exists" in test_result.stderr or test_result.returncode == 0:
            logger.info("✅ pgvector extension is available")
            self.setup_status["pgvector_installed"] = True
            return True
        
        logger.warning("⚠️  pgvector not found, attempting to install...")
        
        # Try to install pgvector
        install_commands = [
            "brew install pgvector",  # macOS
            "sudo apt install postgresql-15-pgvector",  # Ubuntu
        ]
        
        for cmd in install_commands:
            if self.run_command(cmd, f"Installing pgvector with: {cmd}", check_success=False):
                # Test again
                if self.run_command(
                    'psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"',
                    "Testing pgvector installation"
                ):
                    self.setup_status["pgvector_installed"] = True
                    return True
        
        logger.error("❌ Could not install pgvector. Please install manually:")
        logger.error("   See: https://github.com/pgvector/pgvector#installation")
        return False
    
    def setup_ollama(self) -> bool:
        """Setup Ollama and pull nomic-embed-text model"""
        logger.info("🔍 Checking Ollama setup...")
        
        # Check if Ollama is installed
        if not self.run_command("which ollama", "Finding Ollama", check_success=False):
            logger.error("❌ Ollama not found. Please install Ollama first:")
            logger.error("   Visit: https://ollama.ai/download")
            logger.error("   macOS: brew install ollama")
            return False
        
        # Check if Ollama is running
        if not self.run_command("ollama list", "Checking Ollama status", check_success=False):
            logger.warning("⚠️  Ollama not running, attempting to start...")
            # Start Ollama in background
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)  # Wait for startup
            
            if not self.run_command("ollama list", "Rechecking Ollama"):
                logger.error("❌ Could not start Ollama. Please start it manually:")
                logger.error("   Run: ollama serve")
                return False
        
        self.setup_status["ollama_running"] = True
        
        # Check if nomic-embed-text is available
        result = subprocess.run(
            "ollama list | grep nomic-embed-text",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ nomic-embed-text model already available")
            self.setup_status["nomic_model_ready"] = True
            return True
        
        # Pull the model
        logger.info("📥 Pulling nomic-embed-text model (this may take a few minutes)...")
        if self.run_command("ollama pull nomic-embed-text", "Pulling nomic-embed-text model"):
            self.setup_status["nomic_model_ready"] = True
            return True
        
        return False
    
    def setup_database(self, database_name: str = "humanizer_archive") -> bool:
        """Create and configure the archive database"""
        if self.setup_status["database_created"]:
            logger.info(f"✅ Database {database_name} already exists")
            return True
        
        logger.info(f"🔧 Setting up database: {database_name}")
        
        # Create database if it doesn't exist
        create_result = subprocess.run(
            f'psql -d postgres -c "CREATE DATABASE {database_name};" 2>&1',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if "already exists" in create_result.stderr or create_result.returncode == 0:
            logger.info(f"✅ Database {database_name} ready")
        else:
            logger.error(f"❌ Failed to create database: {create_result.stderr}")
            return False
        
        # Enable pgvector extension
        if not self.run_command(
            f'psql -d {database_name} -c "CREATE EXTENSION IF NOT EXISTS vector;"',
            f"Enabling pgvector in {database_name}"
        ):
            return False
        
        self.setup_status["database_created"] = True
        return True
    
    def install_python_dependencies(self) -> bool:
        """Install required Python packages"""
        if self.setup_status["python_deps_installed"]:
            logger.info("✅ Python dependencies already installed")
            return True
        
        logger.info("📦 Installing Python dependencies...")
        
        dependencies = [
            "pgvector",
            "asyncpg", 
            "httpx",
            "sentence-transformers",
            "numpy",
            "tiktoken",
            "fastapi",
            "uvicorn"
        ]
        
        for dep in dependencies:
            if not self.run_command(f"pip install {dep}", f"Installing {dep}"):
                logger.error(f"❌ Failed to install {dep}")
                return False
        
        self.setup_status["python_deps_installed"] = True
        return True
    
    def test_archive_api(self) -> bool:
        """Test that the archive API can start"""
        if self.setup_status["archive_api_tested"]:
            logger.info("✅ Archive API already tested")
            return True
        
        logger.info("🧪 Testing Archive API startup...")
        
        # Test import
        try:
            sys.path.append(str(Path(__file__).parent / "humanizer_api" / "src"))
            from archive_unified_schema import UnifiedArchiveDB
            from embedding_system import AdvancedEmbeddingSystem
            
            logger.info("✅ Archive modules import successfully")
            self.setup_status["archive_api_tested"] = True
            return True
            
        except ImportError as e:
            logger.error(f"❌ Archive API import failed: {e}")
            return False
    
    def setup_lighthouse_ui(self) -> bool:
        """Ensure Lighthouse UI is ready"""
        if self.setup_status["lighthouse_ui_ready"]:
            logger.info("✅ Lighthouse UI already ready")
            return True
        
        logger.info("🎨 Checking Lighthouse UI setup...")
        
        ui_path = Path(__file__).parent / "lighthouse-ui"
        if not ui_path.exists():
            logger.error("❌ Lighthouse UI directory not found")
            return False
        
        # Check if node_modules exists
        if not (ui_path / "node_modules").exists():
            logger.info("📦 Installing UI dependencies...")
            os.chdir(ui_path)
            if not self.run_command("npm install", "Installing UI dependencies"):
                return False
        
        self.setup_status["lighthouse_ui_ready"] = True
        return True
    
    def run_complete_setup(self) -> bool:
        """Run the complete setup process"""
        logger.info("🚀 Starting Complete Archive System Setup")
        logger.info("=" * 60)
        
        setup_steps = [
            ("PostgreSQL", self.check_postgresql),
            ("pgvector Extension", self.setup_pgvector),
            ("Ollama & Models", self.setup_ollama), 
            ("Database Creation", lambda: self.setup_database()),
            ("Python Dependencies", self.install_python_dependencies),
            ("Archive API Test", self.test_archive_api),
            ("Lighthouse UI", self.setup_lighthouse_ui)
        ]
        
        for step_name, step_func in setup_steps:
            logger.info(f"\n📍 Step: {step_name}")
            logger.info("-" * 40)
            
            if not step_func():
                logger.error(f"❌ Setup failed at step: {step_name}")
                self.save_status()
                return False
            
            self.save_status()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 COMPLETE ARCHIVE SYSTEM SETUP SUCCESSFUL!")
        logger.info("=" * 60)
        
        self.print_next_steps()
        return True
    
    def print_next_steps(self):
        """Print next steps for the user"""
        logger.info("\n📋 Next Steps:")
        logger.info("1. Start the Archive API:")
        logger.info("   cd humanizer_api/src")
        logger.info("   python archive_api_enhanced.py")
        logger.info("")
        logger.info("2. Start the Lighthouse UI:")
        logger.info("   cd lighthouse-ui") 
        logger.info("   npm run dev")
        logger.info("")
        logger.info("3. Access the Archive tab in the UI:")
        logger.info("   http://localhost:3100")
        logger.info("")
        logger.info("4. Start smart archive processing:")
        logger.info('   curl -X POST "http://localhost:7200/smart-processing/analyze"')
        logger.info('   curl -X POST "http://localhost:7200/smart-processing/process?max_conversations=10"')
        logger.info("")
        logger.info("🎯 Your archive system is ready!")

def main():
    """Main setup function"""
    print("🏗️  Humanizer Archive System Setup")
    print("=" * 50)
    
    setup_manager = ArchiveSetupManager()
    
    if setup_manager.run_complete_setup():
        print("\n✅ Setup completed successfully!")
        return 0
    else:
        print("\n❌ Setup failed. Check logs above.")
        print("💡 You can run this script again to retry failed steps.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)