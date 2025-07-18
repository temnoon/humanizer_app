#!/usr/bin/env python3
"""
Lamish Lawyer API Standalone Launcher
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lawyer_api import app
from src.config import get_config
import uvicorn
import logging

def main():
    config = get_config()
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Lamish Lawyer API on port {config.api.lawyer_api_port}")
    logger.info(f"Using LLM provider: {config.llm.preferred_provider}")
    logger.info(f"Database: {config.get_database_url()}")
    
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.lawyer_api_port,
        log_level="info"
    )

if __name__ == "__main__":
    main()