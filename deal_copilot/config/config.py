"""Configuration for the Deal Co-Pilot POC"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model Configuration
MODEL_NAME = "gemini-2.5-flash" 
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 8192

# Search Configuration
MAX_SEARCH_RESULTS = 10
SEARCH_DEPTH = "advanced"  # basic or advanced

# Validate API keys
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in environment variables")

