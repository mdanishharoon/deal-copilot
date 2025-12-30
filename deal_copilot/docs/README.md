# Deal Co-Pilot POC - Deep Research Agent

A proof-of-concept implementation of the Deep Research Agent from the Deal Co-Pilot system, designed to help VC/PE analysts conduct first-pass investment due diligence.

> **Note: Two Versions Available:**
> - **Gemini 2.5 + Tavily** (This README) - RAG architecture with explicit search control
> - **OpenAI GPT-4o** ([README_OPENAI.md](README_OPENAI.md)) - Integrated search, simpler setup
> 
> See [COMPARISON.md](COMPARISON.md) for detailed comparison.

## Overview

This POC implements the **Deep Research Agent** (Agent #2 from the full specification), which produces an investor-grade research document covering:

1. **Market Overview** - Market sizing, business models, dynamics, drivers/risks, and outcome potential
2. **Competitor Overview** - Competitive landscape, positioning, and moats analysis
3. **Company/Team Overview and Newsrun** - Company problem/solution, team background, and recent momentum signals

All outputs include inline citations from public web sources.

## Technology Stack

- **LangChain** - Agent orchestration and LLM integration
- **Google Gemini 2.5** - Latest LLM for analysis and report generation
- **Tavily** - Advanced web search API for gathering public intelligence
- **Python 3.8+** - Core implementation

## Prerequisites

Before running this POC, you'll need:

1. **Google Gemini API Key**
   - Get it from: https://makersuite.google.com/app/apikey
   - Free tier available

2. **Tavily API Key**
   - Get it from: https://tavily.com/
   - Free tier: 1000 searches/month

## Setup Instructions

### 1. Clone or navigate to the project directory

```bash
cd /home/danish/vinnie
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
EOF
```

Replace `your_gemini_api_key_here` and `your_tavily_api_key_here` with your actual API keys.

## Usage

### Interactive Mode

Run the script without arguments for interactive prompts:

```bash
python main.py
```

You'll be prompted to enter:
- Company name
- Sector (e.g., SaaS, Fintech, Marketplace, Healthtech)
- Region (e.g., Vietnam, Southeast Asia, Global)
- Website URL
- HQ location (optional)

### Command-Line Mode

Provide all parameters via command-line arguments:

```bash
python main.py \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/"
```

### Save to File

Save the output to a text file:

```bash
python main.py \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/" \
  --output reports/bizzi_research.txt
```

### JSON Output

Get structured JSON output:

```bash
python main.py \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/" \
  --output reports/bizzi_research.json \
  --json
```

## Example Usage

### Example 1: SaaS Company in Vietnam

```bash
python main.py \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/"
```

### Example 2: Fintech in Southeast Asia

```bash
python main.py \
  --company "GrabPay" \
  --sector "Fintech" \
  --region "Southeast Asia" \
  --website "https://www.grab.com/sg/pay/"
```

### Example 3: Marketplace Platform

```bash
python main.py \
  --company "Carousell" \
  --sector "Marketplace" \
  --region "Southeast Asia" \
  --website "https://www.carousell.com/"
```

## Output Format

The report includes:

```
================================================================================
DEEP RESEARCH REPORT
Deal Co-Pilot POC
================================================================================

Company: [Company Name]
Sector: [Sector]
Region: [Region]
Website: [Website URL]
Generated: [Timestamp]

================================================================================

## Market Overview

[Detailed market analysis with inline citations]
- Market sizing (TAM/SAM/SOM) and growth rates
- Industry business models and monetization
- Market structure and dynamics
- Key drivers and risks
- Outcome potential for leaders

--------------------------------------------------------------------------------

## Competitor Overview

[Competitive landscape analysis with inline citations]
- Key competitors and substitutes
- Competitive positioning and differentiation
- Moat analysis (network effects, data, brand, etc.)

--------------------------------------------------------------------------------

## Company/Team Overview and Newsrun

[Company and team analysis with inline citations]
- Company overview and problem/solution fit
- Founder and executive team backgrounds
- Recent milestones, funding, partnerships
- Risk signals and momentum indicators

--------------------------------------------------------------------------------

## References

[List of all cited sources with URLs]
```

## Project Structure

```
vinnie/
├── main.py                    # Entry point and CLI interface
├── deep_research_agent.py     # Core agent implementation
├── config.py                  # Configuration and API key management
├── requirements.txt           # Python dependencies
├── .env                       # API keys (create this, not in git)
├── .gitignore                # Git ignore file
├── README.md                  # This file
└── statement.md               # Full product requirements
```

## Configuration

You can modify agent behavior in `config.py`:

- `MODEL_NAME` - Gemini model (gemini-2.5-flash, gemini-2.5-pro, or gemini-1.5-flash)
- `TEMPERATURE` - LLM creativity (0.0-1.0)
- `MAX_OUTPUT_TOKENS` - Maximum response length
- `MAX_SEARCH_RESULTS` - Number of search results per query
- `SEARCH_DEPTH` - Tavily search depth (basic or advanced)

## Key Features

* **Multi-source research** - Combines multiple web searches per section  
* **Inline citations** - Every claim includes source URL  
* **Investment-focused** - Addresses key due diligence questions  
* **Flexible input** - Interactive or command-line modes  
* **Multiple outputs** - Text or JSON format  
* **Production-ready structure** - Easy to extend with additional agents  

## Limitations & Future Work

This POC implements the **Deep Research Agent** only. The full Deal Co-Pilot includes:

- [ ] Deal Pack/Data Room Ingestor Agent (private intel)
- [ ] Risk Scanner Agent (anomaly detection)
- [ ] IC Note Drafter Agent (final memo generation)
- [ ] Charting Agent (data visualization)

### Current Limitations:

- Public data only (no private data room access)
- Text output only (no Word/Google Docs generation)
- No benchmark data comparison
- No financial modeling or forecasting

## Troubleshooting

### API Key Errors

```
ValueError: GOOGLE_API_KEY not found in environment variables
```

**Solution**: Ensure your `.env` file exists and contains valid API keys.

### Rate Limiting

If you encounter rate limits:
- Use `gemini-2.5-flash` (fastest and latest) or fall back to `gemini-1.5-flash`
- Reduce `MAX_SEARCH_RESULTS` in `config.py`
- Add delays between requests

### No Results

If search returns empty results:
- Check your internet connection
- Verify Tavily API key is valid
- Try different search queries or company names

## Development

To extend this POC:

1. **Add more agents** - Implement Risk Scanner or IC Drafter
2. **Add document export** - Use `python-docx` for Word output
3. **Add data room ingestion** - Parse PDFs, Excel files
4. **Add caching** - Cache search results to avoid redundant API calls
5. **Add streaming** - Stream LLM responses for better UX

## License

This is a proof-of-concept for demonstration purposes.

## Support

For questions or issues, refer to:
- LangChain docs: https://python.langchain.com/
- Tavily docs: https://docs.tavily.com/
- Gemini docs: https://ai.google.dev/docs

---

