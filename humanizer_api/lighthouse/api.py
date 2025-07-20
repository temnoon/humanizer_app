import os
from dotenv import load_dotenv
import spacy
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import litellm

# --- Application Setup ---

# Load environment variables from .env file (for API keys)
# LiteLLM will automatically use keys like OPENAI_API_KEY, ANTHROPIC_API_key, etc.
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="Humanizer Lighthouse API",
    description="Provides services for narrative deconstruction and projection (The Lamish Projection Engine).",
    version="0.1.0",
)

# --- CORS Configuration ---
# Allow requests from the UI development server

origins = [
    "http://localhost:3100",  # Vite/React frontend
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NLP Model Loading ---

# Load the spaCy model at startup to be used across requests
# Using a global variable to hold the loaded model
nlp = None

@app.on_event("startup")
def load_nlp_model():
    """Load the spaCy model into memory when the API starts."""
    global nlp
    try:
        print("Loading spaCy NLP model (en_core_web_trf)...")
        nlp = spacy.load("en_core_web_trf")
        print("NLP model loaded successfully.")
    except OSError:
        print("Error: spaCy model 'en_core_web_trf' not found.")
        print("Please run 'python -m spacy download en_core_web_trf' in your venv.")
        # In a real production scenario, you might want to exit here
        # For now, we'll allow it to run but NLP features will fail.
        nlp = None

# --- In-Memory Data Store ---
# This simulates a database for personas, namespaces, and styles
# to get the frontend working quickly.

db = {
    "personas": {
        "cynical_journalist": {
            "id": "cynical_journalist",
            "name": "Cynical Journalist",
            "description": "Assumes authority is self-serving and technology creates more problems than it solves.",
            "prompt_fragment": "Adopt a cynical, critical, and world-weary tone. Question all motives and expose the hidden flaws. Use investigative language."
        },
        "reverent_poet": {
            "id": "reverent_poet",
            "name": "Reverent Poet",
            "description": "Finds beauty in the mundane and expresses ideas with lyrical, metaphorical language.",
            "prompt_fragment": "Adopt a reverent, lyrical, and metaphorical tone. See the deeper beauty and interconnectedness of all things. Use poetic language and rich imagery."
        },
        "corporate_strategist": {
            "id": "corporate_strategist",
            "name": "Corporate Strategist",
            "description": "Views everything through a lens of efficiency, KPIs, and market dynamics.",
            "prompt_fragment": "Adopt a formal, strategic, and data-driven tone. Frame the narrative in terms of stakeholders, assets, and strategic imperatives. Use business jargon."
        }
    },
    "namespaces": {
        "lamish_galaxy": {
            "id": "lamish_galaxy",
            "name": "Lamish Galaxy",
            "description": "A far-future sci-fi setting with unique FTL concepts and galactic politics.",
            "mappings": {"car": "skimmer", "gun": "pulse caster", "ceo": "sector regent"}
        },
        "forgotten_kingdoms": {
            "id": "forgotten_kingdoms",
            "name": "Forgotten Kingdoms",
            "description": "A high-fantasy world of magic, castles, and ancient evils.",
            "mappings": {"computer": "scrying pool", "gun": "spell-etched wand", "ceo": "archmage"}
        },
        "earth_2024_news": {
            "id": "earth_2024_news",
            "name": "Earth (2024 News Cycle)",
            "description": "The familiar world of contemporary news and events.",
            "mappings": {}
        }
    },
    "styles": {
        "hemingway": {
            "id": "hemingway",
            "name": "Hemingway",
            "description": "Sparse, direct, and declarative sentences. Minimal adjectives.",
            "prompt_fragment": "Rewrite in a style similar to Ernest Hemingway. Use short, declarative sentences. Show, don't tell. Avoid adverbs and adjectives where possible."
        },
        "lovecraft": {
            "id": "lovecraft",
            "name": "Lovecraft",
            "description": "Ornate, complex sentences with a sense of cosmic dread and esoteric vocabulary.",
            "prompt_fragment": "Rewrite in a style similar to H.P. Lovecraft. Use complex, multi-clause sentences. Employ a rich, esoteric vocabulary and evoke a sense of cosmic, indescribable horror."
        }
    }
}


# --- Pydantic Models (API Data Contracts) ---

class ConfigItem(BaseModel):
    id: str
    name: str
    description: str

class ConfigurationResponse(BaseModel):
    personas: List[ConfigItem]
    namespaces: List[ConfigItem]
    styles: List[ConfigItem]

class TransformationRequest(BaseModel):
    text: str = Field(..., example="The CEO announced a new phone with a better camera.")
    persona_id: str = Field(..., example="cynical_journalist")
    namespace_id: str = Field(..., example="lamish_galaxy")
    style_id: str = Field(..., example="hemingway")

class TransformationResponse(BaseModel):
    original_text: str
    transformed_text: str
    debug_prompt: str
    llm_model: str

# --- API Endpoints ---

@app.get("/health", summary="Health Check")
async def health_check():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok"}


@app.get("/configurations", response_model=ConfigurationResponse, summary="Get UI Configurations")
async def get_configurations():
    """
    Provides the lists of available Personas, Namespaces, and Styles
    for the frontend dropdown menus.
    """
    return {
        "personas": list(db["personas"].values()),
        "namespaces": list(db["namespaces"].values()),
        "styles": list(db["styles"].values())
    }

@app.post("/transform", response_model=TransformationResponse, summary="Transform Narrative")
async def transform_narrative(request: TransformationRequest):
    """
    Takes an input text and a set of subjective layers (Persona, Namespace, Style)
    and returns a new, projected narrative.
    """
    print(f"Received transformation request: {request.dict()}")

    # --- 1. Validate Inputs ---
    try:
        persona = db["personas"][request.persona_id]
        namespace = db["namespaces"][request.namespace_id]
        style = db["styles"][request.style_id]
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Invalid configuration ID provided: {e}")

    # --- 2. Deconstruct (Placeholder) ---
    # In a real implementation, this would involve using spaCy for NER and the SQA
    # method with an LLM to extract the core essence. For now, we'll just identify
    # entities to be replaced.
    if not nlp:
         raise HTTPException(status_code=500, detail="NLP model not loaded. Cannot process text.")

    doc = nlp(request.text)
    named_entities = {ent.text: ent.label_ for ent in doc.ents}
    print(f"Identified entities: {named_entities}")


    # --- 3. Construct the LLM Prompt ---
    # This combines the instructions from the selected subjective layers.
    prompt = f"""
You are the Lamish Projection Engine. Your task is to deconstruct an input text to its core essence and then project it into a new narrative based on a specific Persona, Namespace, and Style.

**Input Text:**
"{request.text}"

**Instructions:**

1.  **Adopt Persona:** {persona['prompt_fragment']}
2.  **Apply Namespace:** Use the conceptual world of '{namespace['name']}'. If relevant, use these specific mappings: {namespace['mappings']}. Do not use names or concepts from the original text's namespace unless no mapping is available.
3.  **Apply Style:** {style['prompt_fragment']}

Produce only the final, transformed narrative text.
"""

    # --- 4. Call the LLM ---
    try:
        print("Sending prompt to LLM...")
        # litellm allows us to call any model provider (OpenAI, Anthropic, Cohere, local models via Ollama, etc.)
        # To use Ollama, you would set the model name like "ollama/llama3"
        response = litellm.completion(
            model="gpt-4o-mini", # or "claude-3-haiku-20240307", "ollama/llama3", etc.
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        transformed_text = response.choices[0].message.content.strip()
        llm_model = response.model
        print(f"LLM response received. Model used: {llm_model}")

    except Exception as e:
        print(f"ERROR: LLM call failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to communicate with the LLM provider. Error: {e}")

    # --- 5. Return the Result ---
    return {
        "original_text": request.text,
        "transformed_text": transformed_text,
        "debug_prompt": prompt,
        "llm_model": llm_model
    }

# To run this API locally:
# uvicorn api:app --reload --port 8100
