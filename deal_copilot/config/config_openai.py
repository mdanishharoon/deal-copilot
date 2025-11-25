"""Configuration for OpenAI Deep Research Agent"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
OPENAI_MODEL = "gpt-5"  # Default: GPT-4o (use max_completion_tokens)
# Supported models:
# "gpt-4o" - Latest GPT-4 Omni with vision and web search (recommended)
# "gpt-4-turbo" - GPT-4 Turbo with search
# "gpt-4" - Standard GPT-4 (older, uses max_tokens)
# "o1-preview" - O1 reasoning model (uses max_completion_tokens)
# "o1-mini" - O1 mini reasoning model (uses max_completion_tokens)
TEMPERATURE = 0.7  # Note: Not used with GPT-5 (only supports default of 1)
MAX_TOKENS = 16000  # Used as max_completion_tokens for newer models

# Validate API key
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")





