"""
LLM Router
Direct LLM provider access and management
"""
from fastapi import APIRouter, Depends

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from models import LLMRequest, LLMResponse
from core.dependencies import get_llm_service, LLMService

router = APIRouter()

@router.post("/complete", response_model=LLMResponse)
async def complete_text(
    request: LLMRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """Complete text using configured LLM provider"""
    # Placeholder implementation
    return LLMResponse(
        text=f"Completion for: {request.prompt[:50]}...",
        model="placeholder-model",
        provider="placeholder-provider", 
        token_usage={"prompt_tokens": 10, "completion_tokens": 20},
        response_time_ms=500.0
    )

@router.post("/embed")
async def generate_embeddings(
    text: str,
    llm_service: LLMService = Depends(get_llm_service)
):
    """Generate embeddings for text"""
    embedding = await llm_service.embed(text)
    return {"embedding": embedding, "dimension": len(embedding)}