"""
Search Service
Advanced semantic and full-text search with relevance ranking
"""
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, and_, or_
import chromadb

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config
from models import SearchQuery, SearchResult, SearchResponse, Content, ContentType
from .llm_service import LLMService

logger = logging.getLogger(__name__)


class SearchService:
    """Advanced search service with semantic and full-text capabilities"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        
    async def semantic_search(
        self,
        query: SearchQuery,
        db: AsyncSession,
        vectordb: chromadb.PersistentClient
    ) -> SearchResponse:
        """Perform semantic search using vector embeddings"""
        
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_embedding = await self.llm_service.embed(query.query)
            
            # Search vector database
            collection = vectordb.get_collection(config.vectordb.collection_name)
            
            # Build where clause for filtering
            where_clause = self._build_vector_where_clause(query)
            
            # Perform vector search
            vector_results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(query.limit * 2, config.vectordb.max_results),  # Get extra for filtering
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert to Content objects and apply additional filtering
            search_results = await self._process_vector_results(
                vector_results, query, db
            )
            
            # Calculate query time
            query_time_ms = (time.time() - start_time) * 1000
            
            return SearchResponse(
                results=search_results[:query.limit],
                total_results=len(search_results),
                query_time_ms=query_time_ms,
                query=query
            )
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}", exc_info=True)
            # Fallback to full-text search
            logger.info("Falling back to full-text search")
            return await self.fulltext_search(query, db)
    
    async def fulltext_search(
        self,
        query: SearchQuery,
        db: AsyncSession
    ) -> SearchResponse:
        """Perform full-text search using database indexes"""
        
        start_time = time.time()
        
        # Build PostgreSQL full-text search query
        sql_query = self._build_fulltext_query(query)
        
        # Execute search
        result = await db.execute(sql_query)
        content_rows = result.fetchall()
        
        # Convert to SearchResult objects
        search_results = []
        for rank, row in enumerate(content_rows, 1):
            content = Content(
                id=row.id,
                content_type=row.content_type,
                data=row.data,
                metadata=row.metadata,
                embedding=row.embedding,
                processing_status=row.processing_status,
                quality_score=row.quality_score,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            
            # Calculate similarity score based on rank
            similarity_score = max(0.1, 1.0 - (rank - 1) * 0.1)
            
            # Generate highlight snippets
            snippets = self._generate_snippets(content.data, query.query)
            
            search_results.append(SearchResult(
                content=content,
                similarity_score=similarity_score,
                rank=rank,
                highlight_snippets=snippets
            ))
        
        query_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=search_results,
            total_results=len(search_results),
            query_time_ms=query_time_ms,
            query=query
        )
    
    async def hybrid_search(
        self,
        query: SearchQuery,
        db: AsyncSession,
        vectordb: chromadb.PersistentClient,
        semantic_weight: float = 0.7
    ) -> SearchResponse:
        """Combine semantic and full-text search with weighted scoring"""
        
        start_time = time.time()
        
        # Perform both searches concurrently
        semantic_task = asyncio.create_task(
            self.semantic_search(query, db, vectordb)
        )
        fulltext_task = asyncio.create_task(
            self.fulltext_search(query, db)
        )
        
        semantic_response, fulltext_response = await asyncio.gather(
            semantic_task, fulltext_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(semantic_response, Exception):
            logger.warning(f"Semantic search failed: {semantic_response}")
            return fulltext_response if not isinstance(fulltext_response, Exception) else SearchResponse(
                results=[], total_results=0, query_time_ms=0, query=query
            )
        
        if isinstance(fulltext_response, Exception):
            logger.warning(f"Full-text search failed: {fulltext_response}")
            return semantic_response
        
        # Combine and re-rank results
        combined_results = self._combine_search_results(
            semantic_response.results,
            fulltext_response.results,
            semantic_weight
        )
        
        query_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=combined_results[:query.limit],
            total_results=len(combined_results),
            query_time_ms=query_time_ms,
            query=query
        )
    
    def _build_vector_where_clause(self, query: SearchQuery) -> Optional[Dict[str, Any]]:
        """Build where clause for vector database filtering"""
        
        where_conditions = {}
        
        # Filter by content types
        if query.content_types:
            where_conditions["content_type"] = {
                "$in": [ct.value for ct in query.content_types]
            }
        
        # Filter by tags
        if query.tags:
            # Note: This would need to be adapted based on how tags are stored in metadata
            where_conditions["tags"] = {
                "$in": query.tags
            }
        
        return where_conditions if where_conditions else None
    
    async def _process_vector_results(
        self,
        vector_results: Dict[str, Any],
        query: SearchQuery,
        db: AsyncSession
    ) -> List[SearchResult]:
        """Process vector search results into SearchResult objects"""
        
        search_results = []
        
        if not vector_results["ids"] or not vector_results["ids"][0]:
            return search_results
        
        # Get content IDs and distances
        content_ids = vector_results["ids"][0]
        distances = vector_results["distances"][0]
        metadatas = vector_results["metadatas"][0]
        
        # Convert distances to similarity scores (assuming cosine distance)
        similarity_scores = [1.0 - distance for distance in distances]
        
        # Filter by similarity threshold
        filtered_results = [
            (content_id, score, metadata)
            for content_id, score, metadata in zip(content_ids, similarity_scores, metadatas)
            if score >= query.similarity_threshold
        ]
        
        if not filtered_results:
            return search_results
        
        # Get full content records from database
        content_ids_to_fetch = [result[0] for result in filtered_results]
        
        sql_query = select(Content).where(
            Content.id.in_(content_ids_to_fetch)
        )
        
        result = await db.execute(sql_query)
        contents_by_id = {str(content.id): content for content in result.scalars()}
        
        # Build SearchResult objects
        for rank, (content_id, similarity_score, metadata) in enumerate(filtered_results, 1):
            if content_id in contents_by_id:
                content = contents_by_id[content_id]
                
                # Generate highlight snippets
                snippets = self._generate_snippets(content.data, query.query)
                
                search_results.append(SearchResult(
                    content=content,
                    similarity_score=similarity_score,
                    rank=rank,
                    highlight_snippets=snippets
                ))
        
        return search_results
    
    def _build_fulltext_query(self, query: SearchQuery):
        """Build PostgreSQL full-text search query"""
        
        # Base full-text search
        search_vector = func.to_tsvector('english', Content.data)
        search_query = func.plainto_tsquery('english', query.query)
        
        base_query = select(Content).where(
            search_vector.match(search_query)
        )
        
        # Add content type filtering
        if query.content_types:
            base_query = base_query.where(
                Content.content_type.in_(query.content_types)
            )
        
        # Add tag filtering (assuming tags are stored in metadata JSONB)
        if query.tags:
            tag_conditions = []
            for tag in query.tags:
                tag_conditions.append(
                    Content.metadata['tags'].astext.contains(tag)
                )
            if tag_conditions:
                base_query = base_query.where(or_(*tag_conditions))
        
        # Order by relevance and apply pagination
        base_query = base_query.order_by(
            func.ts_rank(search_vector, search_query).desc()
        ).offset(query.offset).limit(query.limit)
        
        return base_query
    
    def _generate_snippets(self, content: str, search_query: str) -> List[str]:
        """Generate highlighted snippets around search terms"""
        
        snippets = []
        search_terms = search_query.lower().split()
        content_lower = content.lower()
        
        # Find sentences containing search terms
        sentences = content.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains any search terms
            if any(term in sentence_lower for term in search_terms):
                # Trim sentence if too long
                snippet = sentence.strip()
                if len(snippet) > 200:
                    # Find the search term and center the snippet around it
                    for term in search_terms:
                        term_pos = sentence_lower.find(term)
                        if term_pos != -1:
                            start = max(0, term_pos - 100)
                            end = min(len(sentence), term_pos + 100)
                            snippet = "..." + sentence[start:end] + "..."
                            break
                
                snippets.append(snippet)
                
                # Limit number of snippets
                if len(snippets) >= 3:
                    break
        
        return snippets
    
    def _combine_search_results(
        self,
        semantic_results: List[SearchResult],
        fulltext_results: List[SearchResult],
        semantic_weight: float
    ) -> List[SearchResult]:
        """Combine and re-rank results from semantic and full-text search"""
        
        # Create lookup for semantic scores
        semantic_scores = {
            str(result.content.id): result.similarity_score
            for result in semantic_results
        }
        
        # Create lookup for full-text scores
        fulltext_scores = {
            str(result.content.id): result.similarity_score
            for result in fulltext_results
        }
        
        # Get all unique content IDs
        all_content_ids = set(semantic_scores.keys()) | set(fulltext_scores.keys())
        
        # Create combined results
        combined_results = []
        content_lookup = {}
        
        # Build content lookup
        for result in semantic_results + fulltext_results:
            content_lookup[str(result.content.id)] = result.content
        
        # Calculate combined scores
        for content_id in all_content_ids:
            semantic_score = semantic_scores.get(content_id, 0.0)
            fulltext_score = fulltext_scores.get(content_id, 0.0)
            
            # Weighted combination
            combined_score = (
                semantic_score * semantic_weight +
                fulltext_score * (1.0 - semantic_weight)
            )
            
            if content_id in content_lookup:
                # Use snippets from the higher-scoring search
                if semantic_score > fulltext_score:
                    snippets = next(
                        (r.highlight_snippets for r in semantic_results if str(r.content.id) == content_id),
                        []
                    )
                else:
                    snippets = next(
                        (r.highlight_snippets for r in fulltext_results if str(r.content.id) == content_id),
                        []
                    )
                
                combined_results.append(SearchResult(
                    content=content_lookup[content_id],
                    similarity_score=combined_score,
                    rank=0,  # Will be set after sorting
                    highlight_snippets=snippets
                ))
        
        # Sort by combined score and set ranks
        combined_results.sort(key=lambda x: x.similarity_score, reverse=True)
        for rank, result in enumerate(combined_results, 1):
            result.rank = rank
        
        return combined_results
    
    async def search_suggestions(
        self,
        partial_query: str,
        db: AsyncSession,
        limit: int = 5
    ) -> List[str]:
        """Generate search suggestions based on partial query"""
        
        # Simple implementation - could be enhanced with ML models
        suggestions = []
        
        if len(partial_query) >= 2:
            # Search for content titles and sources that match
            sql_query = select(Content.metadata['title'].astext).where(
                and_(
                    Content.metadata['title'].astext.ilike(f"%{partial_query}%"),
                    Content.metadata['title'].astext.is_not(None)
                )
            ).limit(limit)
            
            result = await db.execute(sql_query)
            titles = result.scalars().all()
            
            suggestions.extend([title for title in titles if title])
        
        return suggestions[:limit]
    
    async def get_search_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get search analytics and popular queries"""
        
        # This would typically query an analytics table
        # For now, return mock data
        return {
            "total_searches_today": 150,
            "avg_response_time_ms": 250,
            "popular_queries": [
                "machine learning",
                "data science",
                "artificial intelligence",
                "python programming",
                "web development"
            ],
            "search_success_rate": 0.92
        }