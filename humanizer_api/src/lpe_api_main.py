"""
LPE API - Advanced Content Transformation Engine (continued)

This is the continuation of the LPE API implementation.
"""

# Continue from the existing lpe_api.py file
# Adding the main LPE API class and routing

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
            ProcessingEngine.TRANSLATION: TranslationEngine(self.llm_client),
            ProcessingEngine.SYNTHESIS: SynthesisEngine(self.llm_client),
            ProcessingEngine.VISION: VisionEngine(self.llm_client)
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
            start_time = datetime.utcnow()
            
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
                processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
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
        
        @self.app.get("/sessions")
        async def list_sessions(
            limit: int = 50,
            offset: int = 0,
            db: Session = Depends(self.get_db)
        ):
            """List processing sessions"""
            sessions = db.query(ProcessingSession).order_by(
                ProcessingSession.updated_at.desc()
            ).limit(limit).offset(offset).all()
            
            return {
                "sessions": [
                    {
                        "id": session.id,
                        "session_name": session.session_name,
                        "created_at": session.created_at.isoformat(),
                        "updated_at": session.updated_at.isoformat(),
                        "total_operations": session.total_operations
                    }
                    for session in sessions
                ],
                "total_sessions": db.query(ProcessingSession).count()
            }
        
        @self.app.post("/batch")
        async def batch_process(
            session_id: str,
            engine_type: ProcessingEngine,
            contents: List[MediaContent],
            parameters: Dict[str, Any] = {},
            context: Optional[str] = None,
            background_tasks: BackgroundTasks = BackgroundTasks(),
            db: Session = Depends(self.get_db)
        ):
            """Process multiple content items in batch"""
            
            results = []
            total_processing_time = 0
            
            for content_item in contents:
                request = ProcessingRequest(
                    content=[content_item],
                    processing_type=engine_type,
                    parameters=parameters,
                    context=context,
                    session_id=session_id
                )
                
                result = await process_content(request, background_tasks, db)
                results.append(result)
                total_processing_time += result.processing_time_ms
            
            return {
                "batch_id": str(uuid.uuid4()),
                "session_id": session_id,
                "processed_items": len(contents),
                "total_processing_time_ms": total_processing_time,
                "results": results
            }
        
        @self.app.get("/operation/{operation_id}")
        async def get_operation(operation_id: str, db: Session = Depends(self.get_db)):
            """Get specific operation details"""
            operation = db.query(ProcessingOperation).filter(
                ProcessingOperation.id == operation_id
            ).first()
            
            if not operation:
                raise HTTPException(status_code=404, detail="Operation not found")
            
            return {
                "id": operation.id,
                "session_id": operation.session_id,
                "engine_type": operation.engine_type,
                "input_content": json.loads(operation.input_content),
                "output_content": json.loads(operation.output_content),
                "parameters": operation.parameters,
                "metadata": operation.metadata,
                "processing_time_ms": operation.processing_time_ms,
                "quality_score": operation.quality_score,
                "created_at": operation.created_at.isoformat(),
                "llm_provider": operation.llm_provider,
                "token_usage": operation.token_usage
            }
        
        @self.app.get("/stats")
        async def get_lpe_stats(db: Session = Depends(self.get_db)):
            """Get LPE processing statistics"""
            
            # Basic counts
            total_sessions = db.query(ProcessingSession).count()
            total_operations = db.query(ProcessingOperation).count()
            
            # Engine usage
            engine_usage = {}
            engine_results = db.execute(
                "SELECT engine_type, COUNT(*) FROM processing_operations GROUP BY engine_type"
            ).fetchall()
            for engine, count in engine_results:
                engine_usage[engine] = count
            
            # Provider usage
            provider_usage = {}
            provider_results = db.execute(
                "SELECT llm_provider, COUNT(*) FROM processing_operations GROUP BY llm_provider"
            ).fetchall()
            for provider, count in provider_results:
                provider_usage[provider] = count
            
            # Average processing times
            avg_times = {}
            time_results = db.execute(
                "SELECT engine_type, AVG(processing_time_ms) FROM processing_operations GROUP BY engine_type"
            ).fetchall()
            for engine, avg_time in time_results:
                avg_times[engine] = int(avg_time) if avg_time else 0
            
            return {
                "total_sessions": total_sessions,
                "total_operations": total_operations,
                "engine_usage": engine_usage,
                "provider_usage": provider_usage,
                "average_processing_times_ms": avg_times,
                "available_engines": len(ProcessingEngine),
                "available_providers": len(LLMProvider)
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
