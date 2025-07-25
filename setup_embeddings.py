#!/usr/bin/env python3
"""
Embedding Setup Script
======================

This script sets up everything needed for overnight embeddings processing:
1. Database schema with pgvector extension
2. Ollama with nomic-text-embed model
3. Configuration validation
4. Dependency checks

Run this before starting overnight_embeddings.py
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import asyncpg
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

class EmbeddingSetup:
    """Setup manager for embedding infrastructure."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
        
    async def check_database_connection(self, config: dict) -> bool:
        """Check if we can connect to PostgreSQL."""
        try:
            db_config = config.get('database', {})
            conn = await asyncpg.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                user=db_config.get('user', 'postgres'),
                password=db_config.get('password', ''),
                database=db_config.get('database', 'humanizer')
            )
            await conn.close()
            console.print("✅ Database connection successful")
            return True
        except Exception as e:
            console.print(f"❌ Database connection failed: {e}")
            return False
            
    async def setup_database_schema(self, config: dict) -> bool:
        """Set up the database schema for embeddings."""
        try:
            db_config = config.get('database', {})
            conn = await asyncpg.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                user=db_config.get('user', 'postgres'),
                password=db_config.get('password', ''),
                database=db_config.get('database', 'humanizer')
            )
            
            # Check if pgvector extension exists
            console.print("🔧 Checking pgvector extension...")
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                console.print("✅ pgvector extension enabled")
            except Exception as e:
                console.print(f"❌ Failed to enable pgvector: {e}")
                console.print("You may need to install pgvector: https://github.com/pgvector/pgvector")
                await conn.close()
                return False
                
            # Apply schema extensions
            schema_file = Path("humanizer_api/src/schema_chunks_extension.sql")
            if schema_file.exists():
                console.print("🔧 Applying schema extensions...")
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                await conn.execute(schema_sql)
                console.print("✅ Database schema updated")
            else:
                console.print(f"❌ Schema file not found: {schema_file}")
                await conn.close()
                return False
                
            await conn.close()
            return True
            
        except Exception as e:
            console.print(f"❌ Database setup failed: {e}")
            return False
            
    async def check_ollama_status(self, config: dict) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            ollama_host = config.get('embedding', {}).get('ollama_host', 'http://localhost:11434')
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{ollama_host}/api/version", timeout=5.0)
                if response.status_code == 200:
                    version_info = response.json()
                    console.print(f"✅ Ollama is running (version: {version_info.get('version', 'unknown')})")
                    return True
                else:
                    console.print(f"❌ Ollama responded with status {response.status_code}")
                    return False
                    
        except Exception as e:
            console.print(f"❌ Failed to connect to Ollama: {e}")
            console.print("Make sure Ollama is installed and running: https://ollama.ai/")
            return False
            
    async def check_embedding_model(self, config: dict) -> bool:
        """Check if the embedding model is available in Ollama."""
        try:
            ollama_host = config.get('embedding', {}).get('ollama_host', 'http://localhost:11434')
            model_name = config.get('embedding', {}).get('model_name', 'nomic-text-embed')
            
            async with httpx.AsyncClient() as client:
                # List available models
                response = await client.get(f"{ollama_host}/api/tags", timeout=10.0)
                if response.status_code == 200:
                    models_data = response.json()
                    available_models = [model['name'] for model in models_data.get('models', [])]
                    
                    if model_name in available_models:
                        console.print(f"✅ Embedding model '{model_name}' is available")
                        return True
                    else:
                        console.print(f"❌ Embedding model '{model_name}' not found")
                        console.print("Available models:", available_models)
                        
                        # Offer to download the model
                        if console.input(f"Download {model_name}? [y/N]: ").lower() == 'y':
                            return await self._download_model(ollama_host, model_name)
                        return False
                else:
                    console.print(f"❌ Failed to list Ollama models: {response.status_code}")
                    return False
                    
        except Exception as e:
            console.print(f"❌ Failed to check embedding model: {e}")
            return False
            
    async def _download_model(self, ollama_host: str, model_name: str) -> bool:
        """Download the embedding model to Ollama."""
        try:
            console.print(f"📥 Downloading {model_name}... (this may take a few minutes)")
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{ollama_host}/api/pull",
                    json={"name": model_name}
                )
                
                if response.status_code == 200:
                    console.print(f"✅ Successfully downloaded {model_name}")
                    return True
                else:
                    console.print(f"❌ Failed to download {model_name}: {response.status_code}")
                    return False
                    
        except Exception as e:
            console.print(f"❌ Model download failed: {e}")
            return False
            
    async def test_embedding_generation(self, config: dict) -> bool:
        """Test embedding generation with a sample text."""
        try:
            ollama_host = config.get('embedding', {}).get('ollama_host', 'http://localhost:11434')
            model_name = config.get('embedding', {}).get('model_name', 'nomic-text-embed')
            
            test_text = "This is a test sentence for embedding generation."
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{ollama_host}/api/embeddings",
                    json={
                        "model": model_name,
                        "prompt": test_text
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result.get('embedding', [])
                    if len(embedding) == 768:  # nomic-text-embed produces 768-dim vectors
                        console.print(f"✅ Embedding generation test successful (768 dimensions)")
                        return True
                    else:
                        console.print(f"❌ Unexpected embedding dimension: {len(embedding)}")
                        return False
                else:
                    console.print(f"❌ Embedding generation failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            console.print(f"❌ Embedding test failed: {e}")
            return False
            
    def check_python_dependencies(self) -> bool:
        """Check if required Python packages are installed."""
        required_packages = [
            'asyncpg',
            'httpx', 
            'rich',
            'sentence-transformers'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                console.print(f"✅ {package}")
            except ImportError:
                console.print(f"❌ {package}")
                missing_packages.append(package)
                
        if missing_packages:
            console.print(f"\nInstall missing packages with:")
            console.print(f"pip install {' '.join(missing_packages)}")
            return False
            
        return True
        
    async def get_database_stats(self, config: dict) -> dict:
        """Get current database statistics."""
        try:
            db_config = config.get('database', {})
            conn = await asyncpg.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                user=db_config.get('user', 'postgres'),
                password=db_config.get('password', ''),
                database=db_config.get('database', 'humanizer')
            )
            
            # Get content statistics
            stats = {}
            
            # Total content items
            result = await conn.fetchval("SELECT COUNT(*) FROM archived_content WHERE content IS NOT NULL")
            stats['total_content'] = result or 0
            
            # Content with existing chunks
            try:
                result = await conn.fetchval("""
                    SELECT COUNT(DISTINCT content_id) FROM content_chunks
                """)
                stats['content_with_chunks'] = result or 0
            except:
                stats['content_with_chunks'] = 0
                
            # Total chunks
            try:
                result = await conn.fetchval("SELECT COUNT(*) FROM content_chunks")
                stats['total_chunks'] = result or 0
            except:
                stats['total_chunks'] = 0
                
            # Chunks with embeddings
            try:
                result = await conn.fetchval("SELECT COUNT(*) FROM content_chunks WHERE embedding IS NOT NULL")
                stats['embedded_chunks'] = result or 0
            except:
                stats['embedded_chunks'] = 0
                
            await conn.close()
            return stats
            
        except Exception as e:
            console.print(f"❌ Failed to get database stats: {e}")
            return {}
            
    def create_sample_config(self) -> dict:
        """Create a sample configuration file."""
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "user": "postgres", 
                "password": "",
                "database": "humanizer"
            },
            "embedding": {
                "ollama_host": "http://localhost:11434",
                "model_name": "nomic-text-embed",
                "chunk_size": 240,
                "chunk_overlap": 50
            },
            "processor": {
                "batch_size": 10,
                "max_concurrent": 3,
                "retry_attempts": 2,
                "delay_seconds": 0.5
            },
            "batch_limit": 1000
        }
        
        config_file = Path("embedding_config.json")
        with open(config_file, 'w') as f:
            json.dump(config, indent=2, fp=f)
            
        console.print(f"📝 Created sample config: {config_file}")
        console.print("Edit this file with your database credentials and preferences")
        
        return config
        
    async def run_setup(self):
        """Run the complete setup process."""
        console.print(Panel.fit(
            "[bold blue]Embedding Setup[/bold blue]\n"
            "Setting up infrastructure for overnight embeddings processing",
            border_style="blue"
        ))
        
        # Create sample config if it doesn't exist
        config_file = Path("embedding_config.json")
        if not config_file.exists():
            config = self.create_sample_config()
        else:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
        # Check Python dependencies
        console.print("\n[bold]Checking Python dependencies...[/bold]")
        if not self.check_python_dependencies():
            console.print("❌ Please install missing dependencies before continuing")
            return False
            
        # Check database connection
        console.print("\n[bold]Checking database connection...[/bold]")
        if not await self.check_database_connection(config):
            console.print("❌ Fix database connection before continuing")
            return False
            
        # Set up database schema
        console.print("\n[bold]Setting up database schema...[/bold]")
        if not await self.setup_database_schema(config):
            console.print("❌ Database schema setup failed")
            return False
            
        # Check Ollama
        console.print("\n[bold]Checking Ollama...[/bold]")
        if not await self.check_ollama_status(config):
            console.print("❌ Start Ollama before continuing")
            return False
            
        # Check embedding model
        console.print("\n[bold]Checking embedding model...[/bold]")
        if not await self.check_embedding_model(config):
            console.print("❌ Embedding model not available")
            return False
            
        # Test embedding generation
        console.print("\n[bold]Testing embedding generation...[/bold]")
        if not await self.test_embedding_generation(config):
            console.print("❌ Embedding generation test failed")
            return False
            
        # Get database statistics
        console.print("\n[bold]Database statistics...[/bold]")
        stats = await self.get_database_stats(config)
        
        if stats:
            table = Table(title="Current Database Status")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="magenta")
            
            table.add_row("Total Content Items", str(stats.get('total_content', 0)))
            table.add_row("Content with Chunks", str(stats.get('content_with_chunks', 0)))
            table.add_row("Total Chunks", str(stats.get('total_chunks', 0)))
            table.add_row("Embedded Chunks", str(stats.get('embedded_chunks', 0)))
            
            console.print(table)
            
            # Calculate what needs processing
            total_content = stats.get('total_content', 0)
            content_with_chunks = stats.get('content_with_chunks', 0)
            needs_processing = total_content - content_with_chunks
            
            if needs_processing > 0:
                console.print(f"\n📊 Approximately {needs_processing} content items need processing")
            else:
                console.print("\n✅ All content appears to have been processed")
                
        console.print(Panel.fit(
            "[bold green]✅ Setup Complete![/bold green]\n"
            f"Ready to run: python overnight_embeddings.py --config {config_file}",
            border_style="green"
        ))
        
        return True


async def main():
    """Main entry point."""
    setup = EmbeddingSetup()
    success = await setup.run_setup()
    
    if success:
        console.print("\n[bold green]🚀 You can now run overnight embeddings![/bold green]")
        console.print("Commands:")
        console.print("  python overnight_embeddings.py --dry-run  # See what would be processed")
        console.print("  python overnight_embeddings.py             # Start processing")
    else:
        console.print("\n[bold red]❌ Setup incomplete. Fix the issues above before proceeding.[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())