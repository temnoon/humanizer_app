"""
Attribute Management System
===========================

Manages saved narrative attributes with algorithm transparency and introspection.
Provides storage, retrieval, and algorithm tracking for QNT analyses.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import aiofiles

@dataclass
class AttributeStorage:
    """File-based storage for saved attributes"""
    
    def __init__(self, storage_dir: str = "./data/saved_attributes"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_cache_file = self.storage_dir / "analysis_cache.json"
        self.attributes_file = self.storage_dir / "attributes.json"
        
    async def save_analysis(self, analysis_id: str, analysis_data: Dict[str, Any]):
        """Save complete analysis data for later reference"""
        cache = await self._load_analysis_cache()
        cache[analysis_id] = {
            "data": analysis_data,
            "saved_at": datetime.now().isoformat()
        }
        
        async with aiofiles.open(self.analysis_cache_file, 'w') as f:
            await f.write(json.dumps(cache, indent=2))
    
    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis data"""
        cache = await self._load_analysis_cache()
        entry = cache.get(analysis_id)
        return entry["data"] if entry else None
    
    async def save_attribute(self, attribute_data: Dict[str, Any]) -> str:
        """Save a specific attribute with algorithm details"""
        attributes = await self._load_attributes()
        
        attribute_id = str(uuid.uuid4())
        attribute_data["attribute_id"] = attribute_id
        attribute_data["created_at"] = datetime.now().isoformat()
        
        attributes[attribute_id] = attribute_data
        
        async with aiofiles.open(self.attributes_file, 'w') as f:
            await f.write(json.dumps(attributes, indent=2))
        
        return attribute_id
    
    async def get_attribute(self, attribute_id: str) -> Optional[Dict[str, Any]]:
        """Get specific attribute by ID"""
        attributes = await self._load_attributes()
        return attributes.get(attribute_id)
    
    async def get_attribute_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get attribute by user-assigned name"""
        attributes = await self._load_attributes()
        for attr in attributes.values():
            if attr.get("name") == name:
                return attr
        return None
    
    async def list_attributes(self, attribute_type: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List all attributes with optional filtering"""
        attributes = await self._load_attributes()
        results = []
        
        for attr in attributes.values():
            # Filter by type
            if attribute_type and attr.get("attribute_type") != attribute_type:
                continue
            
            # Filter by tags
            if tags:
                attr_tags = attr.get("tags", [])
                if not any(tag in attr_tags for tag in tags):
                    continue
            
            results.append(attr)
        
        # Sort by creation date, newest first
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results
    
    async def delete_attribute(self, attribute_id: str) -> bool:
        """Delete an attribute"""
        attributes = await self._load_attributes()
        if attribute_id in attributes:
            del attributes[attribute_id]
            async with aiofiles.open(self.attributes_file, 'w') as f:
                await f.write(json.dumps(attributes, indent=2))
            return True
        return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about saved attributes"""
        attributes = await self._load_attributes()
        
        by_type = {}
        by_algorithm = {}
        by_confidence = {"high": 0, "medium": 0, "low": 0}
        
        for attr in attributes.values():
            # Count by type
            attr_type = attr.get("attribute_type", "unknown")
            by_type[attr_type] = by_type.get(attr_type, 0) + 1
            
            # Count by algorithm
            algorithm = attr.get("algorithm_used", {}).get("name", "unknown")
            by_algorithm[algorithm] = by_algorithm.get(algorithm, 0) + 1
            
            # Count by confidence level
            confidence = attr.get("confidence_score", 0)
            if confidence >= 0.8:
                by_confidence["high"] += 1
            elif confidence >= 0.6:
                by_confidence["medium"] += 1
            else:
                by_confidence["low"] += 1
        
        return {
            "total_attributes": len(attributes),
            "by_type": by_type,
            "by_algorithm": by_algorithm,
            "by_confidence": by_confidence,
            "storage_path": str(self.storage_dir)
        }
    
    async def _load_analysis_cache(self) -> Dict[str, Any]:
        """Load analysis cache from file"""
        if not self.analysis_cache_file.exists():
            return {}
        
        try:
            async with aiofiles.open(self.analysis_cache_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception:
            return {}
    
    async def _load_attributes(self) -> Dict[str, Any]:
        """Load attributes from file"""
        if not self.attributes_file.exists():
            return {}
        
        try:
            async with aiofiles.open(self.attributes_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception:
            return {}

class AttributeAlgorithmTracker:
    """Tracks algorithm details for transparency and reproducibility"""
    
    @staticmethod
    def create_algorithm_record(
        name: str,
        version: str,
        llm_provider: str,
        prompt_template: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a complete algorithm record"""
        return {
            "name": name,
            "version": version,
            "parameters": parameters,
            "confidence_threshold": parameters.get("confidence_threshold", 0.5),
            "llm_provider": llm_provider,
            "prompt_template": prompt_template,
            "processing_steps": [
                "1. Text preprocessing and normalization",
                "2. LLM prompt construction with template",
                "3. LLM inference with specified parameters",
                "4. Response parsing and validation",
                "5. Confidence scoring and thresholding",
                "6. Fallback handling if confidence too low"
            ]
        }
    
    @staticmethod
    def get_persona_algorithm_details(llm_provider: str) -> Dict[str, Any]:
        """Get algorithm details for persona extraction"""
        return AttributeAlgorithmTracker.create_algorithm_record(
            name="QNT_Persona_Extractor",
            version="2.0.0",
            llm_provider=llm_provider,
            prompt_template="""Analyze this narrative text and identify the persona (voice/perspective):

Text: "{narrative}"

Extract:
1. The primary persona archetype (e.g., "wise elder", "curious child", "skeptical scientist", "romantic dreamer")
2. Key characteristics of this voice
3. Specific textual indicators that reveal this persona

Respond with JSON:
{{
    "name": "persona archetype",
    "confidence": 0.85,
    "characteristics": ["trait1", "trait2", "trait3"],
    "voice_indicators": ["specific phrases", "word choices", "perspective markers"]
}}""",
            parameters={
                "max_tokens": 300,
                "temperature": 0.3,
                "confidence_threshold": 0.6
            }
        )
    
    @staticmethod
    def get_namespace_algorithm_details(llm_provider: str) -> Dict[str, Any]:
        """Get algorithm details for namespace extraction"""
        return AttributeAlgorithmTracker.create_algorithm_record(
            name="QNT_Namespace_Extractor",
            version="2.0.0",
            llm_provider=llm_provider,
            prompt_template="""Analyze this narrative text and identify the namespace (universe/context):

Text: "{narrative}"

Extract:
1. The narrative universe or domain (e.g., "maritime/nautical", "modern urban", "fantasy realm", "domestic life")
2. Cultural and temporal context
3. Domain-specific elements and markers
4. Level of abstraction (literal, metaphorical, mythic, etc.)

Respond with JSON:
{{
    "name": "narrative universe",
    "confidence": 0.85,
    "domain_markers": ["specific elements", "vocabulary", "references"],
    "cultural_context": "time period and culture",
    "reality_layer": "literal/metaphorical/mythic"
}}""",
            parameters={
                "max_tokens": 300,
                "temperature": 0.3,
                "confidence_threshold": 0.6
            }
        )
    
    @staticmethod
    def get_style_algorithm_details(llm_provider: str) -> Dict[str, Any]:
        """Get algorithm details for style extraction"""
        return AttributeAlgorithmTracker.create_algorithm_record(
            name="QNT_Style_Extractor",
            version="2.0.0",
            llm_provider=llm_provider,
            prompt_template="""Analyze this narrative text and identify the style (linguistic/rhetorical approach):

Text: "{narrative}"

Extract:
1. The stylistic approach (e.g., "lyrical", "conversational", "formal", "poetic", "minimalist")
2. Key linguistic features and patterns
3. Rhetorical and literary devices used
4. Tone and mood characteristics

Respond with JSON:
{{
    "name": "stylistic approach",
    "confidence": 0.85,
    "linguistic_features": ["sentence structure", "vocabulary level", "rhythm"],
    "rhetorical_devices": ["metaphor", "repetition", "imagery"],
    "tone_characteristics": ["melancholic", "hopeful", "urgent"]
}}""",
            parameters={
                "max_tokens": 300,
                "temperature": 0.3,
                "confidence_threshold": 0.6
            }
        )
    
    @staticmethod
    def get_essence_algorithm_details(llm_provider: str) -> Dict[str, Any]:
        """Get algorithm details for essence extraction"""
        return AttributeAlgorithmTracker.create_algorithm_record(
            name="QNT_Essence_Extractor",
            version="2.0.0",
            llm_provider=llm_provider,
            prompt_template="""Analyze this narrative text and extract the essential meaning (essence):

Text: "{narrative}"

Extract the core invariant meaning that would be preserved across different transformations:
1. The distilled essential message
2. Elements that are fundamental to the meaning
3. Semantic density/concentration
4. Internal coherence

Respond with JSON:
{{
    "core_meaning": "essential meaning in one sentence",
    "meaning_density": 0.75,
    "invariant_elements": ["core concepts", "key relationships", "essential emotions"],
    "coherence_score": 0.85,
    "entropy_measure": 0.65
}}""",
            parameters={
                "max_tokens": 300,
                "temperature": 0.2,
                "confidence_threshold": 0.7
            }
        )

# Global storage instance
attribute_storage = AttributeStorage()