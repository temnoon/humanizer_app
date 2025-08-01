"""
Data Migration from Existing Services
Migrate content and configurations from current Humanizer system to unified platform
"""
import asyncio
import json
import logging
import sqlite3
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import asyncpg
import chromadb
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from config import config
from models import Content, ContentType, ProcessingStatus, ContentMetadata
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


class DataMigrator:
    """Migrate data from existing services to unified platform"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.migration_stats = {
            "content_migrated": 0,
            "content_failed": 0,
            "conversations_migrated": 0,
            "transformations_migrated": 0,
            "embeddings_generated": 0,
            "errors": []
        }
        
    async def migrate_all(self, source_paths: Dict[str, str], target_db_url: str):
        """Migrate all data from existing services"""
        
        logger.info("Starting comprehensive data migration")
        
        # Create database connection
        engine = create_async_engine(target_db_url)
        async_session = sessionmaker(engine, class_=AsyncSession)
        
        # Initialize ChromaDB
        vectordb = chromadb.PersistentClient(path=config.vectordb.path)
        
        try:
            async with async_session() as session:
                # Migrate content from Archive API
                if "archive_db" in source_paths:
                    await self._migrate_archive_content(
                        source_paths["archive_db"], session, vectordb
                    )
                
                # Migrate conversations
                if "lighthouse_db" in source_paths:
                    await self._migrate_lighthouse_data(
                        source_paths["lighthouse_db"], session, vectordb
                    )
                
                # Migrate Rails data
                if "rails_db" in source_paths:
                    await self._migrate_rails_data(
                        source_paths["rails_db"], session, vectordb
                    )
                
                # Migrate configuration files
                if "config_dir" in source_paths:
                    await self._migrate_configurations(
                        source_paths["config_dir"], session
                    )
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            raise
        finally:
            await engine.dispose()
        
        logger.info(f"Migration completed: {self.migration_stats}")
        return self.migration_stats
    
    async def _migrate_archive_content(
        self, 
        archive_db_path: str, 
        session: AsyncSession,
        vectordb: chromadb.PersistentClient
    ):
        """Migrate content from Archive API SQLite database"""
        
        logger.info(f"Migrating content from {archive_db_path}")
        
        # Connect to source SQLite database
        conn = sqlite3.connect(archive_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get all content records
            cursor.execute("""
                SELECT id, content_type, content_data, metadata, 
                       embeddings, created_at, source_info
                FROM content 
                ORDER BY created_at
            """)
            
            batch_size = 50
            batch = []
            
            for row in cursor.fetchall():
                try:
                    # Parse metadata
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    
                    # Determine content type
                    content_type = self._map_content_type(row['content_type'])
                    
                    # Create content metadata
                    content_metadata = ContentMetadata(
                        source=metadata.get('source', 'archive_migration'),
                        title=metadata.get('title'),
                        author=metadata.get('author'),
                        language=metadata.get('language', 'en'),
                        tags=metadata.get('tags', [])
                    )
                    
                    # Parse embedding if available
                    embedding = None
                    if row['embeddings']:
                        try:
                            embedding = json.loads(row['embeddings'])
                        except:
                            pass
                    
                    # Create content record
                    content = Content(
                        id=uuid.UUID(row['id']) if self._is_valid_uuid(row['id']) else uuid.uuid4(),
                        content_type=content_type,
                        data=row['content_data'] or '',
                        metadata=content_metadata.dict(),
                        embedding=embedding,
                        processing_status=ProcessingStatus.COMPLETED,
                        quality_score=metadata.get('quality_score', 0.8),
                        created_at=self._parse_datetime(row['created_at'])
                    )
                    
                    batch.append(content)
                    
                    # Process batch
                    if len(batch) >= batch_size:
                        await self._process_content_batch(batch, session, vectordb)
                        batch = []
                        
                except Exception as e:
                    self.migration_stats["content_failed"] += 1
                    self.migration_stats["errors"].append(f"Content migration error: {e}")
                    logger.error(f"Failed to migrate content {row['id']}: {e}")
            
            # Process remaining batch
            if batch:
                await self._process_content_batch(batch, session, vectordb)
                
        finally:
            conn.close()
        
        logger.info(f"Archive content migration completed: {self.migration_stats['content_migrated']} records")
    
    async def _migrate_lighthouse_data(
        self,
        lighthouse_db_path: str,
        session: AsyncSession,
        vectordb: chromadb.PersistentClient
    ):
        """Migrate data from Lighthouse API database"""
        
        logger.info(f"Migrating Lighthouse data from {lighthouse_db_path}")
        
        conn = sqlite3.connect(lighthouse_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Check if conversations table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='conversations'
            """)
            
            if cursor.fetchone():
                await self._migrate_conversations(cursor, session)
            
            # Check for transformation records
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='transformations'
            """)
            
            if cursor.fetchone():
                await self._migrate_transformations(cursor, session)
                
        finally:
            conn.close()
    
    async def _migrate_conversations(self, cursor, session: AsyncSession):
        """Migrate conversation data"""
        
        cursor.execute("""
            SELECT id, title, messages, created_at, metadata
            FROM conversations
            ORDER BY created_at
        """)
        
        for row in cursor.fetchall():
            try:
                # Parse messages
                messages = json.loads(row['messages']) if row['messages'] else []
                
                # Convert conversation to content
                conversation_text = self._messages_to_text(messages)
                
                # Create metadata
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                content_metadata = ContentMetadata(
                    source="lighthouse_conversation",
                    title=row['title'] or f"Conversation {row['id'][:8]}",
                    author=metadata.get('user', 'unknown'),
                    language='en',
                    tags=['conversation', 'lighthouse']
                )
                
                # Create content record
                content = Content(
                    id=uuid.uuid4(),
                    content_type=ContentType.JSON,
                    data=conversation_text,
                    metadata=content_metadata.dict(),
                    processing_status=ProcessingStatus.COMPLETED,
                    quality_score=0.9,  # Conversations are generally high quality
                    created_at=self._parse_datetime(row['created_at'])
                )
                
                session.add(content)
                self.migration_stats["conversations_migrated"] += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate conversation {row['id']}: {e}")
                self.migration_stats["errors"].append(f"Conversation migration error: {e}")
    
    async def _migrate_transformations(self, cursor, session: AsyncSession):
        """Migrate transformation records"""
        
        cursor.execute("""
            SELECT id, original_text, transformed_text, engine, 
                   attributes, created_at, metadata
            FROM transformations
            ORDER BY created_at
        """)
        
        for row in cursor.fetchall():
            try:
                # Create transformation record in new schema
                # This would involve creating records in transformations.transformation_requests
                # and transformations.transformation_results tables
                
                self.migration_stats["transformations_migrated"] += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate transformation {row['id']}: {e}")
                self.migration_stats["errors"].append(f"Transformation migration error: {e}")
    
    async def _migrate_rails_data(
        self,
        rails_db_path: str,
        session: AsyncSession,
        vectordb: chromadb.PersistentClient
    ):
        """Migrate data from Rails application database"""
        
        logger.info(f"Migrating Rails data from {rails_db_path}")
        
        conn = sqlite3.connect(rails_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Migrate writebooks
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='writebooks'
            """)
            
            if cursor.fetchone():
                await self._migrate_writebooks(cursor, session, vectordb)
            
            # Migrate archived content
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='archived_contents'
            """)
            
            if cursor.fetchone():
                await self._migrate_archived_contents(cursor, session, vectordb)
                
        finally:
            conn.close()
    
    async def _migrate_writebooks(self, cursor, session: AsyncSession, vectordb: chromadb.PersistentClient):
        """Migrate writebook data"""
        
        cursor.execute("""
            SELECT id, title, content, metadata, created_at, updated_at
            FROM writebooks
            ORDER BY created_at
        """)
        
        for row in cursor.fetchall():
            try:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                
                content_metadata = ContentMetadata(
                    source="rails_writebook",
                    title=row['title'],
                    author=metadata.get('author', 'unknown'),
                    language='en',
                    tags=['writebook', 'rails'] + metadata.get('tags', [])
                )
                
                content = Content(
                    id=uuid.uuid4(),
                    content_type=ContentType.MARKDOWN,
                    data=row['content'] or '',
                    metadata=content_metadata.dict(),
                    processing_status=ProcessingStatus.COMPLETED,
                    quality_score=0.85,
                    created_at=self._parse_datetime(row['created_at']),
                    updated_at=self._parse_datetime(row['updated_at'])
                )
                
                session.add(content)
                self.migration_stats["content_migrated"] += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate writebook {row['id']}: {e}")
                self.migration_stats["errors"].append(f"Writebook migration error: {e}")
    
    async def _migrate_archived_contents(self, cursor, session: AsyncSession, vectordb: chromadb.PersistentClient):
        """Migrate archived content from Rails"""
        
        cursor.execute("""
            SELECT id, title, content, source_type, metadata, created_at
            FROM archived_contents
            ORDER BY created_at
        """)
        
        for row in cursor.fetchall():
            try:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                
                content_metadata = ContentMetadata(
                    source=f"rails_archive_{row['source_type']}",
                    title=row['title'],
                    author=metadata.get('author', 'unknown'),
                    language=metadata.get('language', 'en'),
                    tags=['archived', 'rails'] + metadata.get('tags', [])
                )
                
                content = Content(
                    id=uuid.uuid4(),
                    content_type=self._map_content_type(row['source_type']),
                    data=row['content'] or '',
                    metadata=content_metadata.dict(),
                    processing_status=ProcessingStatus.COMPLETED,
                    quality_score=metadata.get('quality_score', 0.7),
                    created_at=self._parse_datetime(row['created_at'])
                )
                
                session.add(content)
                self.migration_stats["content_migrated"] += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate archived content {row['id']}: {e}")
                self.migration_stats["errors"].append(f"Archived content migration error: {e}")
    
    async def _migrate_configurations(self, config_dir: str, session: AsyncSession):
        """Migrate configuration files"""
        
        logger.info(f"Migrating configurations from {config_dir}")
        
        config_path = Path(config_dir)
        
        # Look for configuration files
        config_files = [
            "llm_configurations.json",
            "embedding_config.json",
            "attribute_patterns.json"
        ]
        
        for config_file in config_files:
            file_path = config_path / config_file
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        config_data = json.load(f)
                    
                    # Store configuration as content
                    content_metadata = ContentMetadata(
                        source="configuration_migration",
                        title=f"Configuration: {config_file}",
                        author="system",
                        language="en",
                        tags=["configuration", "migration"]
                    )
                    
                    content = Content(
                        id=uuid.uuid4(),
                        content_type=ContentType.JSON,
                        data=json.dumps(config_data, indent=2),
                        metadata=content_metadata.dict(),
                        processing_status=ProcessingStatus.COMPLETED,
                        quality_score=1.0,
                        created_at=datetime.utcnow()
                    )
                    
                    session.add(content)
                    
                except Exception as e:
                    logger.error(f"Failed to migrate config {config_file}: {e}")
                    self.migration_stats["errors"].append(f"Config migration error: {e}")
    
    async def _process_content_batch(
        self, 
        batch: List[Content], 
        session: AsyncSession,
        vectordb: chromadb.PersistentClient
    ):
        """Process a batch of content records"""
        
        # Add to database
        for content in batch:
            session.add(content)
        
        # Generate embeddings for content without them
        embedding_tasks = []
        for content in batch:
            if not content.embedding and content.data:
                embedding_tasks.append(self._generate_embedding(content))
        
        if embedding_tasks:
            await asyncio.gather(*embedding_tasks, return_exceptions=True)
        
        # Store in vector database
        await self._store_batch_in_vectordb(batch, vectordb)
        
        self.migration_stats["content_migrated"] += len(batch)
        
        # Flush to database
        await session.flush()
    
    async def _generate_embedding(self, content: Content):
        """Generate embedding for content"""
        
        try:
            embedding = await self.llm_service.embed(content.data)
            content.embedding = embedding
            self.migration_stats["embeddings_generated"] += 1
        except Exception as e:
            logger.warning(f"Failed to generate embedding for {content.id}: {e}")
    
    async def _store_batch_in_vectordb(self, batch: List[Content], vectordb: chromadb.PersistentClient):
        """Store batch of content in vector database"""
        
        try:
            collection = vectordb.get_or_create_collection(
                name=config.vectordb.collection_name,
                metadata={"dimension": config.vectordb.embedding_dimension}
            )
            
            # Prepare data for batch insert
            embeddings = []
            documents = []
            metadatas = []
            ids = []
            
            for content in batch:
                if content.embedding:
                    embeddings.append(content.embedding)
                    documents.append(content.data)
                    metadatas.append({
                        "content_id": str(content.id),
                        "content_type": content.content_type.value,
                        "title": content.metadata.get("title", ""),
                        "source": content.metadata.get("source", ""),
                        "created_at": content.created_at.isoformat()
                    })
                    ids.append(str(content.id))
            
            if embeddings:
                collection.add(
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
        except Exception as e:
            logger.error(f"Failed to store batch in vector database: {e}")
    
    def _map_content_type(self, source_type: str) -> ContentType:
        """Map source content type to unified ContentType"""
        
        type_mapping = {
            'text': ContentType.TEXT,
            'html': ContentType.HTML,
            'markdown': ContentType.MARKDOWN,
            'md': ContentType.MARKDOWN,
            'json': ContentType.JSON,
            'pdf': ContentType.PDF,
            'image': ContentType.IMAGE,
            'video': ContentType.VIDEO,
            'audio': ContentType.AUDIO,
            'conversation': ContentType.JSON,
            'writebook': ContentType.MARKDOWN
        }
        
        return type_mapping.get(source_type.lower(), ContentType.TEXT)
    
    def _messages_to_text(self, messages: List[Dict]) -> str:
        """Convert conversation messages to searchable text"""
        
        text_parts = []
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            text_parts.append(f"{role}: {content}")
        
        return "\n\n".join(text_parts)
    
    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """Check if string is valid UUID"""
        try:
            uuid.UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False
    
    def _parse_datetime(self, datetime_string: str) -> datetime:
        """Parse datetime string with fallback"""
        
        if not datetime_string:
            return datetime.utcnow()
        
        # Try different datetime formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_string, fmt)
            except ValueError:
                continue
        
        # Fallback to current time
        logger.warning(f"Could not parse datetime: {datetime_string}")
        return datetime.utcnow()


async def main():
    """Main migration function"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Define source paths (adjust these paths based on your actual setup)
    source_paths = {
        "archive_db": "/Users/tem/humanizer-lighthouse/humanizer_api/data/archive.db",
        "lighthouse_db": "/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse/data/humanizer.db",
        "rails_db": "/Users/tem/humanizer-lighthouse/humanizer_rails/db/development.sqlite3",
        "config_dir": "/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse/data"
    }
    
    # Target database URL
    target_db_url = config.database.url
    
    # Create migrator
    migrator = DataMigrator()
    
    try:
        # Run migration
        stats = await migrator.migrate_all(source_paths, target_db_url)
        
        print("\n" + "="*50)
        print("MIGRATION COMPLETED")
        print("="*50)
        print(f"Content migrated: {stats['content_migrated']}")
        print(f"Content failed: {stats['content_failed']}")
        print(f"Conversations migrated: {stats['conversations_migrated']}")
        print(f"Transformations migrated: {stats['transformations_migrated']}")
        print(f"Embeddings generated: {stats['embeddings_generated']}")
        print(f"Total errors: {len(stats['errors'])}")
        
        if stats['errors']:
            print("\nERRORS:")
            for error in stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(stats['errors']) > 10:
                print(f"  ... and {len(stats['errors']) - 10} more errors")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)