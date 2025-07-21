#!/usr/bin/env python3
"""
Context-Aware Text Splitter for Large Projection Pipeline Inputs

This module handles intelligent text splitting for the LPE (Lamish Projection Engine)
to process large narratives that exceed context length limits. It preserves semantic
coherence while ensuring each chunk can be processed through the 5-stage projection
pipeline.

Key Features:
- Token count estimation for different LLM models
- Semantic boundary preservation (sentences, paragraphs, sections)
- Context overlap management to maintain narrative flow
- LPE pipeline stage-aware splitting (considers all 5 stages)
- Parallel processing support for multiple chunks
- Result recombination with coherence checking
"""

import re
import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """Represents a chunk of text for LPE processing"""
    id: str
    content: str
    chunk_index: int
    total_chunks: int
    word_count: int
    estimated_tokens: int
    start_position: int
    end_position: int
    overlap_before: str = ""
    overlap_after: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ContextAwareSplitter:
    """
    Intelligent text splitter that considers LLM context limits and semantic boundaries
    """
    
    def __init__(self, 
                 max_tokens_per_chunk: int = 3000,  # Conservative limit for most models
                 overlap_size: int = 100,           # Words of overlap between chunks
                 model_type: str = "general"):      # "gpt-4", "claude", "general"
        
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.overlap_size = overlap_size
        self.model_type = model_type
        
        # Token estimation ratios for different model families
        self.token_ratios = {
            "gpt-4": 0.75,      # ~4 chars per token
            "claude": 0.7,      # ~4.3 chars per token  
            "llama": 0.8,       # ~3.5 chars per token
            "general": 0.75     # Conservative estimate
        }
        
        # LPE pipeline stage token multipliers (accounts for prompt overhead)
        self.stage_multipliers = {
            "deconstruct": 1.5,    # Analysis adds context
            "map": 1.3,           # Mapping adds namespace context
            "reconstruct": 1.4,   # Reconstruction adds creative context
            "stylize": 1.2,       # Style adds formatting context
            "reflect": 1.3        # Reflection adds meta-context
        }
        
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for the given text"""
        char_count = len(text)
        return int(char_count * self.token_ratios.get(self.model_type, 0.75))
    
    def get_max_safe_tokens(self) -> int:
        """Get maximum safe token count considering LPE pipeline overhead"""
        # Take the most conservative stage multiplier
        max_multiplier = max(self.stage_multipliers.values())
        return int(self.max_tokens_per_chunk / max_multiplier)
    
    def should_split(self, text: str) -> bool:
        """Check if text needs to be split for LPE processing"""
        estimated_tokens = self.estimate_tokens(text)
        safe_limit = self.get_max_safe_tokens()
        
        logger.info(f"Text length: {len(text)} chars, ~{estimated_tokens} tokens, safe limit: {safe_limit}")
        
        return estimated_tokens > safe_limit
    
    def split_for_lpe(self, text: str, narrative_id: str = None) -> List[TextChunk]:
        """
        Split text into chunks suitable for LPE processing
        
        Returns chunks that can be safely processed through all 5 LPE stages
        """
        if not self.should_split(text):
            # Single chunk - no splitting needed
            return [TextChunk(
                id=f"{narrative_id or 'chunk'}_0",
                content=text,
                chunk_index=0,
                total_chunks=1,
                word_count=len(text.split()),
                estimated_tokens=self.estimate_tokens(text),
                start_position=0,
                end_position=len(text),
                metadata={"split_required": False}
            )]
        
        logger.info(f"Splitting large text ({len(text)} chars) for LPE processing")
        
        # Split into chunks with semantic awareness
        chunks = self._semantic_split(text, narrative_id)
        
        # Add overlap for context preservation
        chunks = self._add_overlap(chunks, text)
        
        return chunks
    
    def _semantic_split(self, text: str, narrative_id: str) -> List[TextChunk]:
        """Split text at semantic boundaries while respecting token limits"""
        safe_tokens = self.get_max_safe_tokens()
        chunks = []
        
        # First try to split by sections (double newlines)
        sections = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        current_position = 0
        chunk_index = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Test if adding this section would exceed token limit
            test_content = (current_chunk + "\n\n" + section) if current_chunk else section
            test_tokens = self.estimate_tokens(test_content)
            
            if test_tokens <= safe_tokens:
                # Safe to add this section
                current_chunk = test_content
            else:
                # Current chunk is at capacity
                if current_chunk:
                    # Save current chunk
                    chunk = self._create_chunk(
                        current_chunk, chunk_index, narrative_id, 
                        current_position, current_position + len(current_chunk)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_position += len(current_chunk)
                
                # Check if this section alone exceeds limit
                if self.estimate_tokens(section) > safe_tokens:
                    # Section is too large, need to split by paragraphs
                    para_chunks = self._split_by_paragraphs(section, chunk_index, narrative_id, current_position)
                    chunks.extend(para_chunks)
                    chunk_index += len(para_chunks)
                    current_position += len(section)
                    current_chunk = ""
                else:
                    # Start new chunk with this section
                    current_chunk = section
        
        # Don't forget the last chunk
        if current_chunk:
            chunk = self._create_chunk(
                current_chunk, chunk_index, narrative_id,
                current_position, current_position + len(current_chunk)
            )
            chunks.append(chunk)
        
        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks
    
    def _split_by_paragraphs(self, text: str, start_index: int, narrative_id: str, base_position: int) -> List[TextChunk]:
        """Split large section by paragraphs when section splitting isn't enough"""
        safe_tokens = self.get_max_safe_tokens()
        paragraphs = text.split('\n')
        chunks = []
        
        current_chunk = ""
        chunk_index = start_index
        current_position = base_position
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            test_content = (current_chunk + "\n" + paragraph) if current_chunk else paragraph
            test_tokens = self.estimate_tokens(test_content)
            
            if test_tokens <= safe_tokens:
                current_chunk = test_content
            else:
                # Save current chunk if it exists
                if current_chunk:
                    chunk = self._create_chunk(
                        current_chunk, chunk_index, narrative_id,
                        current_position, current_position + len(current_chunk)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_position += len(current_chunk)
                
                # If paragraph itself is too large, split by sentences
                if self.estimate_tokens(paragraph) > safe_tokens:
                    sentence_chunks = self._split_by_sentences(paragraph, chunk_index, narrative_id, current_position)
                    chunks.extend(sentence_chunks)
                    chunk_index += len(sentence_chunks)
                    current_position += len(paragraph)
                    current_chunk = ""
                else:
                    current_chunk = paragraph
        
        # Last chunk
        if current_chunk:
            chunk = self._create_chunk(
                current_chunk, chunk_index, narrative_id,
                current_position, current_position + len(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_by_sentences(self, text: str, start_index: int, narrative_id: str, base_position: int) -> List[TextChunk]:
        """Final fallback: split by sentences when paragraphs are too large"""
        safe_tokens = self.get_max_safe_tokens()
        sentences = re.split(r'[.!?]+\s+', text)
        chunks = []
        
        current_chunk = ""
        chunk_index = start_index
        current_position = base_position
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            test_content = (current_chunk + ". " + sentence) if current_chunk else sentence
            test_tokens = self.estimate_tokens(test_content)
            
            if test_tokens <= safe_tokens:
                current_chunk = test_content
            else:
                # Save current chunk
                if current_chunk:
                    chunk = self._create_chunk(
                        current_chunk, chunk_index, narrative_id,
                        current_position, current_position + len(current_chunk)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_position += len(current_chunk)
                
                # Start new chunk (even if sentence is too long, we have to include it)
                current_chunk = sentence
        
        # Last chunk
        if current_chunk:
            chunk = self._create_chunk(
                current_chunk, chunk_index, narrative_id,
                current_position, current_position + len(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, content: str, index: int, narrative_id: str, start_pos: int, end_pos: int) -> TextChunk:
        """Create a TextChunk object with proper metadata"""
        return TextChunk(
            id=f"{narrative_id or 'chunk'}_{index}",
            content=content,
            chunk_index=index,
            total_chunks=0,  # Will be updated later
            word_count=len(content.split()),
            estimated_tokens=self.estimate_tokens(content),
            start_position=start_pos,
            end_position=end_pos,
            metadata={
                "split_required": True,
                "split_method": "semantic",
                "safe_tokens": self.get_max_safe_tokens()
            }
        )
    
    def _add_overlap(self, chunks: List[TextChunk], original_text: str) -> List[TextChunk]:
        """Add overlap between chunks to preserve context"""
        if len(chunks) <= 1:
            return chunks
        
        for i, chunk in enumerate(chunks):
            # Add overlap before (from previous chunk)
            if i > 0:
                prev_chunk = chunks[i-1]
                prev_words = prev_chunk.content.split()
                if len(prev_words) > self.overlap_size:
                    overlap = " ".join(prev_words[-self.overlap_size:])
                    chunk.overlap_before = overlap
            
            # Add overlap after (from next chunk)
            if i < len(chunks) - 1:
                next_chunk = chunks[i+1]
                next_words = next_chunk.content.split()
                if len(next_words) > self.overlap_size:
                    overlap = " ".join(next_words[:self.overlap_size])
                    chunk.overlap_after = overlap
        
        return chunks

class LPEChunkProcessor:
    """
    Processes text chunks through the LPE pipeline with context awareness
    """
    
    def __init__(self, lpe_api_base: str = "http://localhost:8100"):
        self.lpe_api_base = lpe_api_base
        
    async def process_chunks_parallel(self, chunks: List[TextChunk], 
                                    persona: str, namespace: str, style: str,
                                    max_parallel: int = 3) -> List[Dict[str, Any]]:
        """
        Process multiple chunks through LPE pipeline in parallel
        
        Returns list of processed results that can be recombined
        """
        if len(chunks) == 1:
            # Single chunk - process directly
            result = await self._process_single_chunk(chunks[0], persona, namespace, style)
            return [result]
        
        logger.info(f"Processing {len(chunks)} chunks in parallel (max {max_parallel} concurrent)")
        
        # Process chunks in batches to avoid overwhelming the system
        results = []
        for i in range(0, len(chunks), max_parallel):
            batch = chunks[i:i + max_parallel]
            
            # Create tasks for this batch
            tasks = []
            for chunk in batch:
                task = self._process_single_chunk(chunk, persona, namespace, style)
                tasks.append(task)
            
            # Execute batch in parallel
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing chunk {batch[j].id}: {result}")
                    # Create error result
                    result = {
                        "chunk_id": batch[j].id,
                        "success": False,
                        "error": str(result),
                        "original_content": batch[j].content
                    }
                
                results.append(result)
            
            # Brief pause between batches
            if i + max_parallel < len(chunks):
                await asyncio.sleep(1)
        
        return results
    
    async def _process_single_chunk(self, chunk: TextChunk, persona: str, namespace: str, style: str) -> Dict[str, Any]:
        """Process a single chunk through the LPE pipeline"""
        try:
            import aiohttp
            
            # Prepare the content with context from overlaps
            content_with_context = chunk.content
            
            if chunk.overlap_before:
                content_with_context = f"[Previous context: {chunk.overlap_before}]\n\n{content_with_context}"
            
            if chunk.overlap_after:
                content_with_context = f"{content_with_context}\n\n[Following context: {chunk.overlap_after}]"
            
            # Add chunk metadata to help LPE understand this is part of a larger narrative
            if chunk.total_chunks > 1:
                content_with_context = f"[This is part {chunk.chunk_index + 1} of {chunk.total_chunks} of a larger narrative]\n\n{content_with_context}"
            
            # Make request to LPE API
            async with aiohttp.ClientSession() as session:
                payload = {
                    "content": content_with_context,
                    "persona": persona,
                    "namespace": namespace,
                    "style": style,
                    "chunk_metadata": {
                        "chunk_id": chunk.id,
                        "chunk_index": chunk.chunk_index,
                        "total_chunks": chunk.total_chunks,
                        "word_count": chunk.word_count,
                        "estimated_tokens": chunk.estimated_tokens
                    }
                }
                
                async with session.post(f"{self.lpe_api_base}/transform", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "chunk_id": chunk.id,
                            "chunk_index": chunk.chunk_index,
                            "success": True,
                            "result": result,
                            "original_content": chunk.content,
                            "processed_content": result.get("final_output", ""),
                            "processing_steps": result.get("steps", [])
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"LPE API error {response.status}: {error_text}")
        
        except Exception as e:
            logger.error(f"Failed to process chunk {chunk.id}: {e}")
            return {
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "success": False,
                "error": str(e),
                "original_content": chunk.content
            }

class ResultRecombiner:
    """
    Intelligently recombines processed chunk results into coherent narrative
    """
    
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
    
    async def recombine_results(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recombine processed chunks into final narrative
        
        Returns combined result with coherence analysis
        """
        if len(chunk_results) == 1:
            # Single chunk - return directly with metadata
            result = chunk_results[0]
            return {
                "final_narrative": result.get("processed_content", result.get("original_content", "")),
                "chunk_count": 1,
                "success_rate": 1.0 if result.get("success", False) else 0.0,
                "processing_metadata": result,
                "coherence_analysis": {"single_chunk": True, "coherence_score": 1.0}
            }
        
        # Sort by chunk index to ensure correct order
        sorted_results = sorted(chunk_results, key=lambda x: x.get("chunk_index", 0))
        
        # Extract successful processed content
        successful_chunks = [r for r in sorted_results if r.get("success", False)]
        success_rate = len(successful_chunks) / len(chunk_results)
        
        if success_rate == 0:
            # All chunks failed - return original content combined
            original_parts = [r.get("original_content", "") for r in sorted_results]
            return {
                "final_narrative": "\n\n".join(original_parts),
                "chunk_count": len(chunk_results),
                "success_rate": 0.0,
                "error": "All chunks failed processing",
                "processing_metadata": chunk_results
            }
        
        # Combine successful processed content
        processed_parts = []
        for result in sorted_results:
            if result.get("success", False):
                content = result.get("processed_content", result.get("original_content", ""))
                processed_parts.append(content)
            else:
                # Use original content for failed chunks
                content = result.get("original_content", "")
                processed_parts.append(f"[Original content - processing failed]: {content}")
        
        combined_narrative = await self._intelligent_combine(processed_parts)
        
        # Analyze coherence
        coherence_analysis = await self._analyze_coherence(processed_parts, combined_narrative)
        
        return {
            "final_narrative": combined_narrative,
            "chunk_count": len(chunk_results),
            "success_rate": success_rate,
            "processing_metadata": chunk_results,
            "coherence_analysis": coherence_analysis
        }
    
    async def _intelligent_combine(self, parts: List[str]) -> str:
        """Intelligently combine narrative parts with transition handling"""
        if not parts:
            return ""
        
        if len(parts) == 1:
            return parts[0]
        
        # Simple concatenation with smart spacing
        combined = ""
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            
            if i == 0:
                combined = part
            else:
                # Add appropriate spacing/transition
                if combined.endswith('.') or combined.endswith('!') or combined.endswith('?'):
                    combined += "\n\n" + part
                else:
                    combined += " " + part
        
        return combined
    
    async def _analyze_coherence(self, parts: List[str], combined: str) -> Dict[str, Any]:
        """Analyze narrative coherence after recombination"""
        analysis = {
            "parts_count": len(parts),
            "total_length": len(combined),
            "coherence_score": 0.8,  # Default good score
            "transition_quality": "good",
            "narrative_flow": "maintained"
        }
        
        # Simple heuristic analysis
        if len(parts) > 1:
            # Check for abrupt transitions
            transitions = []
            for i in range(len(parts) - 1):
                end_part = parts[i][-100:] if len(parts[i]) > 100 else parts[i]
                start_part = parts[i+1][:100] if len(parts[i+1]) > 100 else parts[i+1]
                
                # Simple transition quality check
                if any(word in end_part.lower() for word in ['however', 'meanwhile', 'therefore', 'thus']):
                    transitions.append("smooth")
                elif end_part.endswith('.') and start_part[0].isupper():
                    transitions.append("adequate")
                else:
                    transitions.append("abrupt")
            
            smooth_count = transitions.count("smooth")
            adequate_count = transitions.count("adequate") 
            abrupt_count = transitions.count("abrupt")
            
            if smooth_count > adequate_count + abrupt_count:
                analysis["transition_quality"] = "excellent"
                analysis["coherence_score"] = 0.95
            elif abrupt_count > smooth_count + adequate_count:
                analysis["transition_quality"] = "poor"
                analysis["coherence_score"] = 0.6
            
            analysis["transitions"] = transitions
        
        return analysis

# Main integration function
async def process_large_narrative(content: str, persona: str, namespace: str, style: str,
                                narrative_id: str = None, max_parallel: int = 3) -> Dict[str, Any]:
    """
    Complete pipeline for processing large narratives through LPE
    
    Handles splitting, parallel processing, and recombination
    """
    # Initialize components
    splitter = ContextAwareSplitter(max_tokens_per_chunk=3000)
    processor = LPEChunkProcessor()
    recombiner = ResultRecombiner()
    
    # Step 1: Split text if needed
    chunks = splitter.split_for_lpe(content, narrative_id)
    
    logger.info(f"Processing narrative: {len(chunks)} chunks, {len(content)} chars")
    
    # Step 2: Process chunks through LPE
    chunk_results = await processor.process_chunks_parallel(
        chunks, persona, namespace, style, max_parallel
    )
    
    # Step 3: Recombine results
    final_result = await recombiner.recombine_results(chunk_results)
    
    # Add splitting metadata
    final_result["splitting_metadata"] = {
        "original_length": len(content),
        "chunks_created": len(chunks),
        "split_required": len(chunks) > 1,
        "max_chunk_tokens": splitter.get_max_safe_tokens(),
        "model_type": splitter.model_type
    }
    
    return final_result

if __name__ == "__main__":
    # Test the context-aware splitter
    test_narrative = """
    This is a test narrative to demonstrate context-aware splitting for the LPE pipeline. 
    The story begins with a character who discovers something extraordinary in their everyday life.
    
    Chapter 1: The Discovery
    It was a Tuesday morning when Sarah first noticed the peculiar shimmer in her coffee cup. 
    At first, she thought it was just the light playing tricks on her eyes, but as she watched more carefully, 
    she realized that the liquid was actually moving in patterns that defied physics.
    
    The coffee swirled in perfect spirals, forming intricate mandalas that seemed to tell a story. 
    Each pattern was more complex than the last, and Sarah found herself mesmerized by the display. 
    She had always been a rational person, grounded in science and logic, but this phenomenon challenged everything she thought she knew.
    
    Chapter 2: The Investigation
    Sarah decided to approach this mystery methodically. She began documenting the patterns, 
    taking photographs and making detailed notes about the timing and conditions of each occurrence. 
    The patterns seemed to appear only when she was experiencing strong emotions - excitement, fear, wonder.
    
    Over the following weeks, Sarah discovered that the phenomenon wasn't limited to her coffee cup. 
    She began to notice similar patterns in puddles, in flowing water, even in the way dust motes moved through sunbeams in her apartment. 
    It was as if the universe was trying to communicate with her through the medium of fluid dynamics.
    
    Chapter 3: The Revelation
    The breakthrough came when Sarah realized that the patterns weren't random at all. 
    They were actually a form of writing, a language that existed at the intersection of consciousness and matter. 
    The more she studied them, the more she began to understand their meaning.
    
    The patterns told the story of a hidden dimension that existed parallel to our own, 
    a realm where thought and reality were intimately connected. Sarah realized that her heightened emotional states 
    were somehow creating bridges between the dimensions, allowing the hidden realm to communicate through the patterns.
    
    As she delved deeper into this discovery, Sarah understood that she had been chosen to serve as a translator 
    between worlds. The responsibility was overwhelming, but she also felt a deep sense of purpose and excitement 
    about the possibilities that lay ahead.
    """ * 3  # Make it long enough to require splitting
    
    async def test_splitting():
        result = await process_large_narrative(
            test_narrative, 
            "scientist", 
            "fantasy_realism", 
            "literary_prose",
            "test_narrative_1"
        )
        
        print(f"Processing completed:")
        print(f"- Original length: {result['splitting_metadata']['original_length']} chars")
        print(f"- Chunks created: {result['splitting_metadata']['chunks_created']}")
        print(f"- Success rate: {result['success_rate']:.1%}")
        print(f"- Coherence score: {result['coherence_analysis']['coherence_score']:.2f}")
        print(f"- Final length: {len(result['final_narrative'])} chars")
    
    # Run test
    asyncio.run(test_splitting())