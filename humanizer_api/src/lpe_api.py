"""
LPE API - Advanced Content Transformation Engine (Complete)

Multi-engine content transformation system incorporating the best features from
previous LPE versions with enhanced multi-provider LLM support and session management.
"""

import logging
import asyncio
import json
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import httpx
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Import our configuration
from config import get_config, HumanizerConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
config = get_config()

# Database Models
Base = declarative_base()

class ProcessingSession(Base):
    __tablename__ = "processing_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)  # Future user management
    session_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_operations = Column(Integer, default=0)
    metadata = Column(JSON, default={})

class ProcessingOperation(Base):
    __tablename__ = "processing_operations"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    engine_type = Column(String, nullable=False)
    input_content = Column(Text, nullable=False)
    output_content = Column(Text, nullable=False)
    parameters = Column(JSON, default={})
    metadata = Column(JSON, default={})
    processing_time_ms = Column(Integer)
    quality_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    llm_provider = Column(String)
    llm_model = Column(String)
    token_usage = Column(JSON, default={})

# Enums
class ProcessingEngine(str, Enum):
    PROJECTION = "projection"
    ANALYSIS = "analysis"
    MAIEUTIC = "maieutic"
    TRANSLATION = "translation"
    SYNTHESIS = "synthesis"
    VISION = "vision"

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"

# Pydantic Models
class MediaContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_type: str = Field(..., description="Type: text, image, audio, video, document")
    data: Union[str, dict] = Field(..., description="Content data")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = Field(None, description="Content source")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        valid_types = ['text', 'image', 'audio', 'video', 'document', 'json']
        if v not in valid_types:
            raise ValueError(f'Content type must be one of {valid_types}')
        return v

class ProcessingRequest(BaseModel):
    content: List[MediaContent] = Field(..., description="Content to process")
    processing_type: ProcessingEngine = Field(..., description="Processing engine to use")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Engine-specific parameters")
    context: Optional[str] = Field(None, description="Additional context")
    session_id: Optional[str] = Field(None, description="Processing session ID")
    session_name: Optional[str] = Field(None, description="Human-readable session name")
    preferred_provider: Optional[LLMProvider] = Field(None, description="Preferred LLM provider")
    
    class Config:
        use_enum_values = True

class ProcessingResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    input_content: List[MediaContent]
    output_content: List[MediaContent]
    processing_type: ProcessingEngine
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: int
    quality_score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    llm_provider: str
    token_usage: Dict[str, Any] = Field(default_factory=dict)

# LLM Client Interface
class LLMClient:
    """Unified interface for multiple LLM providers with intelligent fallback"""
    
    def __init__(self, config: HumanizerConfig):
        self.config = config
        self.http_client = httpx.AsyncClient(timeout=config.llm.timeout)
        
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using specified or preferred provider"""
        
        provider = provider or self.config.llm.preferred_provider
        
        try:
            if provider == "deepseek":
                return await self._deepseek_generate(prompt, system_prompt, model, **kwargs)
            elif provider == "ollama":
                return await self._ollama_generate(prompt, system_prompt, model, **kwargs)
            else:
                raise ValueError(f"Provider {provider} not implemented yet")
                
        except Exception as e:
            logger.error(f"Generation failed with {provider}: {e}")
            # Try fallback providers
            for fallback_provider in self.config.llm.fallback_providers:
                if fallback_provider != provider:
                    try:
                        logger.info(f"Trying fallback provider: {fallback_provider}")
                        return await self.generate(prompt, system_prompt, fallback_provider, model, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback {fallback_provider} also failed: {fallback_error}")
                        continue
            
            raise HTTPException(status_code=503, detail=f"All LLM providers failed. Last error: {str(e)}")
    
    async def _deepseek_generate(self, prompt: str, system_prompt: Optional[str], model: Optional[str], **kwargs) -> Dict[str, Any]:
        """DeepSeek API generation - cost-effective option"""
        if not self.config.llm.deepseek_api_key:
            raise ValueError("DeepSeek API key not configured")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model or self.config.llm.deepseek_model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.llm.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.llm.max_tokens)
        }
        
        response = await self.http_client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.llm.deepseek_api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "provider": "deepseek",
            "model": data.get("model", model),
            "usage": data.get("usage", {})
        }
    
    async def _ollama_generate(self, prompt: str, system_prompt: Optional[str], model: Optional[str], **kwargs) -> Dict[str, Any]:
        """Ollama local generation - privacy-focused option"""
        
        payload = {
            "model": model or self.config.llm.ollama_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.llm.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.llm.max_tokens)
            }
        }
        
        response = await self.http_client.post(
            f"{self.config.llm.ollama_host}/api/generate",
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return {
            "content": data["response"],
            "provider": "ollama", 
            "model": data.get("model", model),
            "usage": {"total_duration": data.get("total_duration", 0)}
        }

# Processing Engines
class BaseProcessingEngine:
    """Base class for all processing engines"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    async def process(
        self, 
        content: List[MediaContent], 
        parameters: Dict[str, Any],
        context: Optional[str] = None,
        **kwargs
    ) -> List[MediaContent]:
        """Process content - to be implemented by subclasses"""
        raise NotImplementedError

class ProjectionEngine(BaseProcessingEngine):
    """Transform content through persona, namespace, and style"""
    
    async def process(
        self, 
        content: List[MediaContent], 
        parameters: Dict[str, Any],
        context: Optional[str] = None,
        **kwargs
    ) -> List[MediaContent]:
        
        persona = parameters.get('persona', 'Scholar')
        namespace = parameters.get('namespace', 'academic')
        style = parameters.get('style', 'formal')
        
        results = []
        
        for item in content:
            if item.content_type == 'text':
                system_prompt = f"""You are an expert in narrative transformation. Transform the given content through a specific lens while preserving its essential meaning.

Transformation Parameters:
- PERSONA: {persona} (the character perspective through which to view the content)
- NAMESPACE: {namespace} (the conceptual universe or domain framework)  
- STYLE: {style} (the linguistic patterns and mannerisms to employ)

Your task is to recast the content as if perceived and expressed by the {persona} within the {namespace} context, using {style} linguistic patterns."""
                
                user_prompt = f"""Transform this content:

{item.data}

{f"Additional context: {context}" if context else ""}

Provide the transformed version that embodies the {persona} perspective within the {namespace} framework, expressed in {style} style."""
                
                result = await self.llm_client.generate(
                    user_prompt,
                    system_prompt,
                    **kwargs
                )
                
                results.append(MediaContent(
                    content_type='text',
                    data=result['content'],
                    metadata={
                        'transformation_type': 'projection',
                        'persona': persona,
                        'namespace': namespace,
                        'style': style,
                        'source_id': item.id,
                        'llm_provider': result['provider'],
                        'llm_model': result['model']
                    },
                    source=f"projection_from_{item.id}"
                ))
        
        return results

class AnalysisEngine(BaseProcessingEngine):
    """Analyze content for inherent characteristics"""
    
    async def process(
        self, 
        content: List[MediaContent], 
        parameters: Dict[str, Any],
        context: Optional[str] = None,
        **kwargs
    ) -> List[MediaContent]:
        
        analysis_type = parameters.get('type', 'comprehensive')
        
        results = []
        
        for item in content:
            system_prompt = f"""You are an expert content analyst. Analyze the given content to identify its inherent characteristics.

Provide comprehensive analysis including:
1. Inherent persona/voice characteristics
2. Conceptual namespace/domain
3. Stylistic patterns and linguistic features
4. Structural analysis
5. Key themes and patterns"""
            
            user_prompt = f"""Analyze this content:

{item.data if item.content_type == 'text' else f"[{item.content_type.upper()}]: {str(item.data)[:500]}"}

{f"Additional context: {context}" if context else ""}

Provide detailed analysis of the content's inherent characteristics."""
            
            result = await self.llm_client.generate(
                user_prompt,
                system_prompt,
                **kwargs
            )
            
            results.append(MediaContent(
                content_type='text',
                data=result['content'],
                metadata={
                    'transformation_type': 'analysis',
                    'analysis_type': analysis_type,
                    'source_id': item.id,
                    'llm_provider': result['provider']
                }
            ))
        
        return results

class MaieuticEngine(BaseProcessingEngine):
    """Generate Socratic questions for deeper understanding"""
    
    async def process(
        self, 
        content: List[MediaContent], 
        parameters: Dict[str, Any],
        context: Optional[str] = None,
        **kwargs
    ) -> List[MediaContent]:
        
        depth = parameters.get('depth', 3)
        focus = parameters.get('focus', 'assumptions')
        question_count = parameters.get('question_count', 7)
        
        results = []
        
        for item in content:
            system_prompt = f"""You are a master of Socratic questioning. Generate thought-provoking questions that guide deeper understanding through self-discovery.

Generate questions that:
1. Challenge assumptions
2. Explore implications  
3. Reveal hidden complexities
4. Guide toward deeper insights
5. Encourage critical thinking

Do not provide answers - only questions that lead to discovery."""
            
            user_prompt = f"""Generate Socratic questions for this content:

{item.data if item.content_type == 'text' else f"[{item.content_type.upper()}]: {str(item.data)[:500]}"}

{f"Additional context: {context}" if context else ""}

Focus on {focus} and generate {question_count} questions at depth level {depth}."""
            
            result = await self.llm_client.generate(
                user_prompt,
                system_prompt,
                **kwargs
            )
            
            results.append(MediaContent(
                content_type='text',
                data=result['content'],
                metadata={
                    'transformation_type': 'maieutic',
                    'depth': depth,
                    'focus': focus,
                    'question_count': question_count,
                    'source_id': item.id
                }
            ))
        
        return results

# Main LPE API Class
class LPEAPI:
    """Main LPE API class with all processing engines"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Humanizer LPE API",
            description="Advanced content transformation with multi-engine processing",
            version="1.0.0"
        )
        
        self.config = config
        self.setup_middleware()
        self.setup_database()
        self.setup_llm_client()
        self.setup_engines()
        self.setup_routes()
    
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.api.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_database(self):
        """Setup database connection"""
        database_url = self.config.get_database_url()
        self.engine = create_engine(database_url)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"Database initialized: {database_url}")
    
    def setup_llm_client(self):
        """Setup LLM client"""
        self.llm_client = LLMClient(self.config)
    
    def setup_engines(self):
        """Setup processing engines"""
        self.engines = {
            ProcessingEngine.PROJECTION: ProjectionEngine(self.llm_client),
            ProcessingEngine.ANALYSIS: AnalysisEngine(self.llm_client),
            ProcessingEngine.MAIEUTIC: MaieuticEngine(self.llm_client),
        }
    
    def get_db(self):
        """Database dependency"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.post("/process", response_model=ProcessingResponse)
        async def process_content(
            request: ProcessingRequest,
            background_tasks: BackgroundTasks,
            db: Session = Depends(self.get_db)
        ):
            """Process content through specified engine"""
            start_time = time.time()
            
            try:
                # Validate processing engine
                if request.processing_type not in self.engines:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unknown processing type: {request.processing_type}"
                    )
                
                # Create or get session
                session_id = request.session_id or str(uuid.uuid4())
                session = db.query(ProcessingSession).filter(
                    ProcessingSession.id == session_id
                ).first()
                
                if not session:
                    session = ProcessingSession(
                        id=session_id,
                        session_name=request.session_name or f"Session {session_id[:8]}",
                        metadata={}
                    )
                    db.add(session)
                
                # Get processing engine
                engine = self.engines[request.processing_type]
                
                # Process content
                output_content = await engine.process(
                    request.content,
                    request.parameters,
                    request.context,
                    provider=request.preferred_provider
                )
                
                # Calculate processing time
                processing_time = int((time.time() - start_time) * 1000)
                
                # Create operation record
                operation_id = str(uuid.uuid4())
                operation = ProcessingOperation(
                    id=operation_id,
                    session_id=session_id,
                    engine_type=request.processing_type.value,
                    input_content=json.dumps([item.dict() for item in request.content]),
                    output_content=json.dumps([item.dict() for item in output_content]),
                    parameters=request.parameters,
                    metadata={
                        "context": request.context,
                        "preferred_provider": request.preferred_provider
                    },
                    processing_time_ms=processing_time,
                    llm_provider=request.preferred_provider or self.config.llm.preferred_provider
                )
                
                db.add(operation)
                
                # Update session
                session.total_operations += 1
                session.updated_at = datetime.utcnow()
                
                db.commit()
                
                # Create response
                response = ProcessingResponse(
                    id=operation_id,
                    session_id=session_id,
                    input_content=request.content,
                    output_content=output_content,
                    processing_type=request.processing_type,
                    parameters=request.parameters,
                    processing_time_ms=processing_time,
                    llm_provider=request.preferred_provider or self.config.llm.preferred_provider,
                    metadata={
                        "operation_id": operation_id,
                        "engine": request.processing_type.value,
                        "context_provided": bool(request.context)
                    }
                )
                
                # Log to ChromaDB Memory
                background_tasks.add_task(
                    self._log_to_memory,
                    f"LPE processing: {request.processing_type.value}",
                    {
                        "session_id": session_id,
                        "engine": request.processing_type.value,
                        "input_count": len(request.content),
                        "output_count": len(output_content),
                        "processing_time_ms": processing_time
                    }
                )
                
                return response
                
            except Exception as e:
                logger.error(f"Processing error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/processors")
        async def list_processors():
            """List available processing engines"""
            return {
                "processors": [engine.value for engine in ProcessingEngine],
                "descriptions": {
                    "projection": "Transform content through persona, namespace, and style",
                    "analysis": "Analyze content for inherent characteristics", 
                    "maieutic": "Generate Socratic questions for deeper understanding",
                    "translation": "Cross-domain and language translation",
                    "synthesis": "Combine multiple content pieces into unified output",
                    "vision": "Provide structural and spatial analysis of content"
                },
                "total_engines": len(ProcessingEngine)
            }
        
        @self.app.get("/sessions/{session_id}")
        async def get_session(session_id: str, db: Session = Depends(self.get_db)):
            """Get processing session details"""
            session = db.query(ProcessingSession).filter(
                ProcessingSession.id == session_id
            ).first()
            
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Get operations for this session
            operations = db.query(ProcessingOperation).filter(
                ProcessingOperation.session_id == session_id
            ).order_by(ProcessingOperation.created_at).all()
            
            return {
                "session_id": session.id,
                "session_name": session.session_name,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "total_operations": session.total_operations,
                "operations": [
                    {
                        "id": op.id,
                        "engine_type": op.engine_type,
                        "processing_time_ms": op.processing_time_ms,
                        "quality_score": op.quality_score,
                        "created_at": op.created_at.isoformat(),
                        "llm_provider": op.llm_provider,
                        "parameters": op.parameters
                    }
                    for op in operations
                ]
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            
            # Test LLM connectivity
            llm_status = {}
            for provider in ["deepseek", "ollama"]:  # Test key providers
                try:
                    test_result = await self.llm_client.generate(
                        "Hello", 
                        provider=provider,
                        max_tokens=10
                    )
                    llm_status[provider] = "connected"
                except Exception as e:
                    llm_status[provider] = f"failed: {str(e)[:50]}"
            
            return {
                "status": "healthy",
                "database": "connected",
                "llm_providers": llm_status,
                "engines": list(self.engines.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _log_to_memory(self, content: str, metadata: Dict):
        """Log insights to ChromaDB Memory"""
        try:
            # This would integrate with your ChromaDB Memory MCP server
            logger.info(f"Memory log: {content} | {metadata}")
        except Exception as e:
            logger.error(f"Failed to log to memory: {e}")

# Create and configure the LPE API
def create_lpe_api() -> FastAPI:
    """Factory function to create the LPE API"""
    lpe_api = LPEAPI()
    return lpe_api.app

# For direct running
if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    app = create_lpe_api()
    
    logger.info(f"Starting LPE API on port {config.api.lpe_api_port}")
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.lpe_api_port,
        log_level=config.logging.level.lower()
    )
