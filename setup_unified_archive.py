#!/usr/bin/env python3
"""
Unified Archive Setup Script
Coordinates the setup and population of the PostgreSQL unified archive system
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import json

# Add the source directory to Python path
sys.path.append(str(Path(__file__).parent / "humanizer_api" / "src"))

from archive_unified_schema import UnifiedArchiveDB, CREATE_TABLE_SQL
from node_archive_importer import NodeArchiveImporter
from config import get_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class UnifiedArchiveSetup:
    """Coordinates the complete setup of the unified archive system"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.archive_db = None
        self.setup_complete = False
        
    async def setup_database(self):
        """Create database schema and indexes"""
        logger.info("Setting up PostgreSQL unified archive database...")
        
        try:
            self.archive_db = UnifiedArchiveDB(self.database_url)
            await self.archive_db.create_tables()
            logger.info("✅ Database schema created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False
    
    def setup_rails_database(self):
        """Run Rails migrations for the unified archive"""
        logger.info("Setting up Rails database integration...")
        
        rails_dir = Path(__file__).parent / "humanizer_rails"
        if not rails_dir.exists():
            logger.warning("Rails directory not found, skipping Rails setup")
            return True
        
        try:
            # Change to Rails directory and run migrations
            os.chdir(rails_dir)
            
            # Run the unified archive migration
            result = subprocess.run(
                ["bundle", "exec", "rails", "db:migrate"],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✅ Rails migrations completed successfully")
            logger.debug(f"Migration output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Rails migration failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Rails setup failed: {e}")
            return False
        finally:
            # Change back to original directory
            os.chdir(Path(__file__).parent)
    
    async def import_node_archive(self, node_archive_path: str, max_conversations: Optional[int] = None):
        """Import Node Archive Browser conversations"""
        if not self.archive_db:
            raise RuntimeError("Database not initialized")
        
        logger.info(f"Starting Node Archive import from: {node_archive_path}")
        
        node_path = Path(node_archive_path)
        if not node_path.exists():
            raise FileNotFoundError(f"Node archive path not found: {node_archive_path}")
        
        try:
            importer = NodeArchiveImporter(self.archive_db, node_archive_path)
            stats = importer.import_all_conversations(max_conversations=max_conversations)
            
            logger.info("✅ Node Archive import completed")
            logger.info(f"📊 Import Statistics:")
            logger.info(f"   - Conversations imported: {stats['conversations_imported']}")
            logger.info(f"   - Messages imported: {stats['messages_imported']}")
            logger.info(f"   - Conversations skipped: {stats['conversations_skipped']}")
            
            if stats['errors']:
                logger.warning(f"⚠️  {len(stats['errors'])} errors encountered during import")
                for error in stats['errors'][:5]:  # Show first 5 errors
                    logger.warning(f"   - {error}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Node Archive import failed: {e}")
            raise
    
    def start_archive_api(self):
        """Start the enhanced Archive API"""
        logger.info("Starting Enhanced Archive API...")
        
        api_script = Path(__file__).parent / "humanizer_api" / "src" / "archive_api_enhanced.py"
        if not api_script.exists():
            logger.error(f"Archive API script not found: {api_script}")
            return False
        
        try:
            # Start the API in the background
            process = subprocess.Popen(
                [sys.executable, str(api_script)],
                cwd=api_script.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"✅ Enhanced Archive API started (PID: {process.pid})")
            logger.info("🌐 API available at: http://localhost:7200")
            logger.info("📖 API documentation: http://localhost:7200/docs")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Archive API: {e}")
            return False
    
    def start_rails_server(self):
        """Start the Rails server"""
        logger.info("Starting Rails server...")
        
        rails_dir = Path(__file__).parent / "humanizer_rails"
        if not rails_dir.exists():
            logger.warning("Rails directory not found, skipping Rails server")
            return True
        
        try:
            os.chdir(rails_dir)
            
            # Start Rails server in the background
            process = subprocess.Popen(
                ["bundle", "exec", "rails", "server", "-p", "3000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"✅ Rails server started (PID: {process.pid})")
            logger.info("🌐 Rails API available at: http://localhost:3000")
            logger.info("📖 Unified Archive API: http://localhost:3000/api/v1/unified_archive")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Rails server: {e}")
            return False
        finally:
            os.chdir(Path(__file__).parent)
    
    def verify_setup(self):
        """Verify that all components are working"""
        logger.info("Verifying unified archive setup...")
        
        try:
            # Check database connection
            stats = self.archive_db.get_statistics()
            logger.info(f"✅ Database connected - Total content: {stats.get('total_content', 0)}")
            
            # Check API endpoints
            import httpx
            
            # Test Archive API
            try:
                response = httpx.get("http://localhost:7200/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Archive API responding")
                else:
                    logger.warning(f"⚠️  Archive API health check failed: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️  Archive API not responding: {e}")
            
            # Test Rails API
            try:
                response = httpx.get("http://localhost:3000/api/v1/unified_archive/statistics", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Rails API responding")
                else:
                    logger.warning(f"⚠️  Rails API failed: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️  Rails API not responding: {e}")
            
            self.setup_complete = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup verification failed: {e}")
            return False
    
    def print_summary(self):
        """Print setup summary and next steps"""
        logger.info("\n" + "="*60)
        logger.info("🎯 UNIFIED ARCHIVE SETUP COMPLETE")
        logger.info("="*60)
        
        if self.setup_complete:
            logger.info("✅ PostgreSQL unified archive database configured")
            logger.info("✅ Rails ActiveRecord models ready")
            logger.info("✅ Enhanced Archive API running on port 7200")
            logger.info("✅ Rails API running on port 3000")
            
            logger.info("\n📍 Key Endpoints:")
            logger.info("   • Archive API: http://localhost:7200/docs")
            logger.info("   • Rails API: http://localhost:3000/api/v1/unified_archive")
            logger.info("   • Search: http://localhost:3000/api/v1/unified_archive/search")
            logger.info("   • Statistics: http://localhost:3000/api/v1/unified_archive/statistics")
            
            logger.info("\n🚀 Next Steps:")
            logger.info("   1. Import more archive sources using the import endpoints")
            logger.info("   2. Set up LPE processing for content enhancement")
            logger.info("   3. Configure WriteBook integration for publishing")
            logger.info("   4. Set up Discourse integration for community features")
            
        else:
            logger.error("❌ Setup incomplete - check errors above")

async def main():
    parser = argparse.ArgumentParser(description="Set up unified PostgreSQL archive system")
    parser.add_argument("--database-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--node-archive-path", help="Path to Node Archive Browser data")
    parser.add_argument("--max-conversations", type=int, help="Maximum conversations to import")
    parser.add_argument("--skip-rails", action="store_true", help="Skip Rails setup")
    parser.add_argument("--skip-import", action="store_true", help="Skip data import")
    parser.add_argument("--skip-services", action="store_true", help="Skip starting services")
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = UnifiedArchiveSetup(args.database_url)
    
    try:
        # 1. Setup database schema
        success = await setup.setup_database()
        if not success:
            return 1
        
        # 2. Setup Rails integration
        if not args.skip_rails:
            success = setup.setup_rails_database()
            if not success:
                return 1
        
        # 3. Import Node Archive data
        if not args.skip_import and args.node_archive_path:
            await setup.import_node_archive(args.node_archive_path, args.max_conversations)
        
        # 4. Start services
        if not args.skip_services:
            setup.start_archive_api()
            if not args.skip_rails:
                setup.start_rails_server()
        
        # 5. Verify setup
        setup.verify_setup()
        
        # 6. Print summary
        setup.print_summary()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)