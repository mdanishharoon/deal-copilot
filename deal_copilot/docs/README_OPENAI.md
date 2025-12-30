# Deal Co-Pilot POC - OpenAI Deep Research Agent

A simplified version of the Deep Research Agent using **OpenAI's built-in web search** - no external search API needed!

## Overview

This version uses **OpenAI GPT-4o** which has native web browsing capabilities, eliminating the need for Tavily or any external search API.

**What it generates:**

1. **Market Overview** - Market sizing, business models, dynamics, drivers/risks
2. **Competitor Overview** - Competitive landscape, positioning, and moats
3. **Company/Team Overview and Newsrun** - Company analysis, team background, recent news

All with inline citations from web sources.

## Technology Stack

- **OpenAI GPT-4o** - Single LLM handles both search and analysis
- **Python 3.8+** - Core implementation

That's it! No separate search API needed.

## Prerequisites

You'll need:

1. **OpenAI API Key**
   - Get it from: https://platform.openai.com/api-keys
   - Requires paid account (no free tier)
   - Cost: ~$0.50-1.00 per full report

## Setup Instructions

### 1. Install dependencies

```bash
pip install openai python-dotenv
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure API key

Create or update your `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run!

```bash
# Run example
python example_run_openai.py

# Or interactive mode
python main_openai.py

# Or command line
python main_openai.py \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/"
```

## Usage

### Interactive Mode

```bash
python main_openai.py
```

### Command-Line Mode

```bash
python main_openai.py \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/"
```

### Save to File

```bash
python main_openai.py \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/" \
  --output reports/bizzi_openai.txt
```

### Programmatic Usage

```python
from deep_research_agent_openai import DeepResearchAgentOpenAI

agent = DeepResearchAgentOpenAI()

report = agent.generate_full_report(
    company_name="Bizzi",
    website="https://bizzi.vn/en/",
    sector="SaaS",
    region="Vietnam"
)

# Format as text
text = agent.format_report_as_text(report)
print(text)
```

## Project Files

```
vinnie/
├── deep_research_agent_openai.py  # OpenAI agent implementation
├── config_openai.py               # OpenAI configuration
├── main_openai.py                 # CLI entry point
├── example_run_openai.py          # Example script
└── README_OPENAI.md               # This file
```

## Configuration

Edit `config_openai.py` to customize:

```python
OPENAI_MODEL = "gpt-4o"           # Model to use
TEMPERATURE = 0.7                  # Creativity (0.0-1.0)
MAX_TOKENS = 16000                 # Max response length
```

**Available models:**
- `gpt-4o` - Latest GPT-4 Omni with vision and web search (recommended)
- `gpt-4-turbo` - GPT-4 Turbo with search
- `gpt-4` - Standard GPT-4

## How It Works

Unlike the Gemini + Tavily version which uses RAG (Retrieval-Augmented Generation), this version is simpler:

```
User Input
    ↓
OpenAI GPT-4o
(handles web search internally)
    ↓
Research Report with Citations
```

**Single API call per section:**
1. You provide research questions
2. OpenAI searches the web internally
3. OpenAI analyzes findings
4. Returns structured report with citations

No manual orchestration of search + analysis needed!

## Pros & Cons

### Advantages

- **Simpler** - Only one API key needed
- **Faster** - Single call per section (vs multiple with RAG)
- **Less code** - No manual search orchestration
- **Powerful** - GPT-4o is state-of-the-art
- **Easier maintenance** - Fewer moving parts

### Disadvantages

- **More expensive** - GPT-4o costs more than Gemini 2.5
- **Less control** - Can't see what OpenAI searches
- **No free tier** - Requires paid OpenAI account
- **Black box** - Internal search strategy unknown
- **Vendor lock-in** - Fully dependent on OpenAI

## Cost Comparison

**Per full report (3 sections):**

| Version | Cost |
|---------|------|
| Gemini + Tavily | ~$0.10-0.30 |
| OpenAI | ~$0.50-1.00 |

OpenAI is 3-5x more expensive but simpler to implement.

## When to Use This Version

**Use OpenAI version if:**
- Building quick POC/demo
- Need fastest development time
- Already using OpenAI
- Want simplest architecture
- Quality > cost

**Use Gemini + Tavily if:**
- Need cost optimization
- Want control over sources
- Compliance requires audit trails
- Building for production/enterprise

See [COMPARISON.md](COMPARISON.md) for detailed comparison.

## Troubleshooting

### API Key Error

```
ValueError: OPENAI_API_KEY not found
```

**Solution:** Ensure `.env` file exists with valid OpenAI API key.

### Rate Limiting

If you hit rate limits:
- Check your OpenAI account tier
- Add delays between requests
- Use `gpt-4-turbo` instead of `gpt-4o` (cheaper)

### No Web Search

If citations are missing or output seems outdated:
- Verify you're using `gpt-4o` or `gpt-4-turbo` (have search)
- Check OpenAI status page for outages
- Try being more explicit in prompts about searching

## Example Output

```
================================================================================
DEEP RESEARCH REPORT - OpenAI Edition
================================================================================

Company: Bizzi
Sector: SaaS
Region: Vietnam
Model: gpt-4o
Generated: 2025-11-12T...

================================================================================

## Market Overview

The SaaS market in Vietnam is experiencing rapid growth, driven by digital
transformation... [Source: TechInAsia]

Market sizing indicates a TAM of $X billion... [Source: Statista]

...
```

## Development

To extend this version:

1. **Add more sections** - Create new `generate_*` methods
2. **Add tools** - Use OpenAI's function calling
3. **Add streaming** - Stream responses for better UX
4. **Add caching** - Cache responses to reduce costs

## Support

- OpenAI docs: https://platform.openai.com/docs
- OpenAI API reference: https://platform.openai.com/docs/api-reference

---

**Built with love using OpenAI GPT-4o**





