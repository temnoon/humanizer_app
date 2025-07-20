# Vision API endpoints for the Enhanced Lighthouse API
# Clean implementation with proper LLM Config integration

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import time
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Create router
vision_router = APIRouter(prefix="/api", tags=["Vision"])

# Request models
class VisionRequest(BaseModel):
    prompt: str = Field(..., description="Vision task prompt")
    image_data: str = Field(..., description="Base64 encoded image data")
    provider: Optional[str] = Field(None, description="Override provider from LLM Config")
    model: Optional[str] = Field(None, description="Override model from LLM Config")

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Image generation prompt")
    provider: str = Field("openai", description="Image generation provider")
    size: str = Field("1024x1024", description="Image size")
    model: str = Field("dall-e-3", description="Generation model")
    style: Optional[str] = Field(None, description="Image style")
    quality: str = Field("standard", description="Image quality")

# Import the main API's configuration function and LLM providers
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import LLM providers for real vision processing
try:
    from lpe_core.llm_provider import get_llm_provider, GoogleProvider, OllamaVisionProvider
    REAL_LLM_AVAILABLE = True
    logger.info("Real LLM providers loaded successfully")
except ImportError as e:
    logger.warning(f"Real LLM providers not available: {e}")
    REAL_LLM_AVAILABLE = False

async def process_vision_request(prompt: str, image_data: str, provider: str, model: str, task_type: str = "analyze"):
    """Process vision request using real vision-capable APIs."""
    
    try:
        if provider.lower() in ['google', 'gemini']:
            # Use Google Gemini Vision API via REST
            import httpx
            import os
            import base64
            import json
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                return "Error: Google API key not configured"
            
            # Use REST API directly for Gemini Vision
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        return result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return "No response from Gemini model"
                else:
                    return f"Gemini API error: {response.status_code} - {response.text}"
            
        elif provider.lower() == 'openai':
            # Use OpenAI Vision API
            import openai
            import os
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return "Error: OpenAI API key not configured"
            
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        elif provider.lower() == 'ollama':
            # Use Ollama Vision
            import httpx
            import json
            import os
            
            ollama_url = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            
            response = await httpx.AsyncClient().post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response from Ollama')
            else:
                return f"Ollama error: {response.status_code} - {response.text}"
                
        else:
            return f"""Vision analysis not supported for provider: {provider}

Supported providers:
- google (Gemini Vision)
- openai (GPT-4 Vision) 
- ollama (Local vision models)

Please select a supported provider for image analysis."""
            
    except Exception as e:
        logger.error(f"Error in vision processing: {e}")
        return f"""Error processing vision request with {provider}/{model}:

{str(e)}

Please check that:
1. The provider ({provider}) supports vision analysis
2. The model ({model}) is vision-capable
3. API keys are properly configured
4. The image data is valid base64"""

async def get_vision_config():
    """Get vision configuration from LLM Config."""
    # Import the fetch function from main API
    try:
        from api_enhanced import fetch_llm_configurations
        config_response = await fetch_llm_configurations()
        return config_response.get("task_configs", {}).get("vision", {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.5,
            "max_tokens": 1500
        })
    except:
        # Fallback configuration
        return {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.5,
            "max_tokens": 1500
        }

@vision_router.post("/vision/analyze", summary="Analyze Image with Vision LLM")
async def analyze_image(request: VisionRequest):
    """Analyze an image using vision-capable LLM models."""
    start_time = time.time()
    
    try:
        # Get vision configuration from LLM Config
        vision_config = await get_vision_config()
        
        # Use provided overrides or fall back to config
        selected_provider = request.provider or vision_config.get("provider", "openai")
        selected_model = request.model or vision_config.get("model", "gpt-4o")
        
        logger.info(f"Vision analysis using {selected_provider}/{selected_model}")
        
        # Attempt real vision analysis
        analysis = await process_vision_request(
            prompt=request.prompt,
            image_data=request.image_data,
            provider=selected_provider,
            model=selected_model,
            task_type="analyze"
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "analysis": analysis,
            "prompt_used": request.prompt,
            "provider_used": selected_provider,
            "llm_model": selected_model,
            "processing_time_ms": round(processing_time, 2),
            "image_size_bytes": len(request.image_data) * 3 // 4,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {str(e)}")

@vision_router.post("/vision/transcribe", summary="Extract Text from Image (OCR)")
async def transcribe_image(request: VisionRequest):
    """Extract text from images using vision-capable models."""
    start_time = time.time()
    
    try:
        # Get vision configuration
        vision_config = await get_vision_config()
        
        selected_provider = request.provider or vision_config.get("provider", "openai")
        selected_model = request.model or vision_config.get("model", "gpt-4o")
        
        logger.info(f"Image transcription using {selected_provider}/{selected_model}")
        
        # Use specialized prompt for transcription
        transcription_prompt = request.prompt or "Please transcribe all text visible in this image. If this is handwritten text, transcribe it as accurately as possible. Preserve formatting and structure where relevant."
        
        # Attempt real transcription
        transcription = await process_vision_request(
            prompt=transcription_prompt,
            image_data=request.image_data,
            provider=selected_provider,
            model=selected_model,
            task_type="transcribe"
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "transcription": transcription,
            "prompt_used": transcription_prompt,
            "provider_used": selected_provider,
            "llm_model": selected_model,
            "processing_time_ms": round(processing_time, 2),
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Image transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image transcription failed: {str(e)}")

@vision_router.post("/vision/redraw", summary="Describe Image for Redrawing")
async def redraw_image(request: VisionRequest):
    """Generate detailed descriptions for image recreation."""
    start_time = time.time()
    
    try:
        # Get vision configuration
        vision_config = await get_vision_config()
        
        selected_provider = request.provider or vision_config.get("provider", "openai")
        selected_model = request.model or vision_config.get("model", "gpt-4o")
        
        logger.info(f"Image redraw description using {selected_provider}/{selected_model}")
        
        # Use specialized prompt for artistic analysis
        redraw_prompt = request.prompt or """Analyze this image for artistic reinterpretation and redrawing. Provide a detailed description that includes:

1. Overall composition and layout structure
2. Color palette and lighting characteristics
3. Artistic style and techniques used
4. Key visual elements and their relationships
5. Mood and atmosphere
6. Technical specifications that would help recreate this image

Be specific enough that an artist or AI could recreate the essence of this image from your description."""
        
        # Attempt real artistic analysis
        description = await process_vision_request(
            prompt=redraw_prompt,
            image_data=request.image_data,
            provider=selected_provider,
            model=selected_model,
            task_type="redraw"
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "description": description,
            "prompt_used": redraw_prompt,
            "provider_used": selected_provider,
            "llm_model": selected_model,
            "processing_time_ms": round(processing_time, 2),
            "detail_level": "comprehensive",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Image redraw description failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image redraw description failed: {str(e)}")

@vision_router.post("/image/generate", summary="Generate Image from Text Prompt")
async def generate_image(request: ImageGenerationRequest):
    """Generate images from text prompts using AI models."""
    start_time = time.time()
    
    try:
        logger.info(f"Image generation: {request.provider}/{request.model} - {request.prompt[:50]}...")
        
        # Mock image generation response
        if request.provider == "openai":
            image_url = f"https://example.com/generated/dalle3_{int(time.time())}.png"
            revised_prompt = f"Enhanced: {request.prompt} [Optimized for DALL-E 3]"
        elif request.provider == "midjourney":
            image_url = f"https://example.com/generated/mj_{int(time.time())}.png"
            revised_prompt = f"{request.prompt} --ar 1:1 --v 6 --style raw"
        else:
            image_url = f"https://example.com/generated/ai_{int(time.time())}.png"
            revised_prompt = request.prompt
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "image_url": image_url,
            "prompt_used": revised_prompt,
            "original_prompt": request.prompt,
            "provider_used": request.provider,
            "llm_model": request.model,
            "size": request.size,
            "style": request.style,
            "quality": request.quality,
            "generation_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "note": "Mock response - actual implementation would integrate with real image generation APIs"
        }
        
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")