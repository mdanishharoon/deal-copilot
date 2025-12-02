# Deal Co-Pilot (small change)

A modern **full-stack SaaS application** for AI-powered investment due diligence research.

🌐 **Web Application** | 🚀 **FastAPI Backend** | 🤖 **AI Agents** | ✨ **Beautiful UI**

## ⚡ Quick Start - Full-Stack Application

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install frontend dependencies
cd frontend && npm install && cd ..

# 3. Set API key
export OPENAI_API_KEY="your_key_here"

# 4. Run full-stack (backend + frontend)
./run_fullstack.sh

# 5. Open browser
open http://localhost:3000
```

That's it! 🎉

### Or Run Separately

```bash
# Backend only (port 8000)
./run_server.sh

# Frontend only (port 3000)
cd frontend && npm run dev
```

## 🎯 What You Get

- ✨ **Next.js 15 Frontend** - Modern React with TypeScript
- 🎨 **Tailwind CSS** - Beautiful, responsive design
- 💬 **Natural Language Input** - Just describe the company
- ⚡ **Real-time Progress** - Watch research generate live
- 📊 **Formatted Reports** - Professional, cited research
- 📱 **Fully Responsive** - Works on all devices
- 🚀 **Fast API Backend** - Python-based REST API
- 🤖 **Dual AI Agents** - OpenAI & Gemini options

## 📖 Quick Start - Command Line

### Option 1: OpenAI (Simplest - No Tavily!)

```bash
# 1. Set up environment
export OPENAI_API_KEY="your_key_here"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run example
python -m deal_copilot.examples.example_run_openai
```

### Option 2: Gemini + Tavily (Cost-effective)

```bash
# 1. Set up environment
export GOOGLE_API_KEY="your_gemini_key"
export TAVILY_API_KEY="your_tavily_key"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run example
python -m deal_copilot.examples.example_run
```

## 📁 Project Structure

```
vinnie/
├── frontend/                         # 🎨 Next.js Frontend
│   ├── app/
│   │   ├── globals.css              # Tailwind styles
│   │   ├── layout.tsx               # Root layout
│   │   └── page.tsx                 # Main page
│   ├── components/
│   │   ├── Header.tsx               # Navigation
│   │   ├── HeroSection.tsx          # Input form
│   │   ├── LoadingSection.tsx       # Progress tracking
│   │   └── ResultsSection.tsx       # Report display
│   ├── lib/
│   │   ├── api.ts                   # API client
│   │   └── types.ts                 # TypeScript types
│   ├── package.json                 # NPM dependencies
│   └── README.md                    # Frontend docs
│
├── deal_copilot/                     # 🐍 Python Backend
│   ├── api/                         # 🔌 FastAPI Backend
│   │   └── main.py                  # REST API server
│   ├── agents/                      # 🤖 AI Research Agents
│   │   ├── deep_research_agent.py        # Gemini + Tavily
│   │   └── deep_research_agent_openai.py # OpenAI
│   ├── config/                      # ⚙️  Configuration
│   │   ├── config.py                # Gemini + Tavily
│   │   └── config_openai.py         # OpenAI
│   ├── cli/                         # 💻 Command-line tools
│   ├── examples/                    # 🚀 Example scripts
│   ├── docs/                        # 📚 Documentation
│   └── output/                      # 📊 Generated reports
│
├── run_fullstack.sh                 # ▶️  Run frontend + backend
├── run_server.sh                    # ▶️  Backend only
├── requirements.txt                 # 📦 Python dependencies
├── .env                            # 🔑 API keys
├── README.md                        # 📖 This file
└── GETTING_STARTED.md              # 🚀 Setup guide
```

## 📚 Documentation

### 🌟 Start Here
- **[Getting Started](GETTING_STARTED.md)** - Complete setup guide (5 minutes)
- **[Quick Reference](QUICK_REFERENCE.md)** - Commands cheat sheet

### 📖 Full Documentation
- **[Full-Stack Guide](deal_copilot/docs/FULLSTACK.md)** - Web app architecture & API docs
- **[Project Summary](deal_copilot/docs/PROJECT_SUMMARY.md)** - Complete project overview
- **[Comparison Guide](deal_copilot/docs/COMPARISON.md)** - OpenAI vs Gemini + Tavily
- **[OpenAI Version](deal_copilot/docs/README_OPENAI.md)** - OpenAI-specific docs
- **[Gemini Version](deal_copilot/docs/README.md)** - Gemini + Tavily docs

## 🎯 What It Does

The Deep Research Agent produces investor-grade research reports with:

1. **Market Overview** - Market sizing, business models, dynamics, drivers/risks
2. **Competitor Overview** - Competitive landscape, positioning, moats
3. **Company/Team Overview** - Company analysis, team background, recent news

All with inline citations from web sources!

## 💻 Usage

### Run with Command Line

```bash
# OpenAI version
python -m deal_copilot.cli.main_openai \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/"

# Gemini + Tavily version
python -m deal_copilot.cli.main \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/"
```

### Use Programmatically

```python
from deal_copilot.agents.deep_research_agent_openai import DeepResearchAgentOpenAI

agent = DeepResearchAgentOpenAI()
report = agent.generate_full_report(
    company_name="Bizzi",
    website="https://bizzi.vn/en/",
    sector="SaaS",
    region="Vietnam"
)

print(agent.format_report_as_text(report))
```

## 🔑 API Keys Required

### For OpenAI Version (Simpler):
- **OpenAI API Key**: Get at https://platform.openai.com/api-keys

### For Gemini + Tavily Version (Cheaper):
- **Google Gemini API Key**: Get at https://makersuite.google.com/app/apikey
- **Tavily API Key**: Get at https://tavily.com/ (1000 searches/month free)

Add to `.env` file:
```bash
# OpenAI version
OPENAI_API_KEY=your_key_here

# Or Gemini + Tavily version
GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## 💡 Which Version to Use?

| Feature | Gemini + Tavily | OpenAI |
|---------|----------------|---------|
| **Setup** | 2 API keys | 1 API key ✨ |
| **Cost** | ~$0.10-0.30/report | ~$0.50-1.00/report |
| **Control** | Full search control | No control |
| **Free Tier** | Yes ✨ | No |

**Recommendation:** Start with OpenAI for simplicity, switch to Gemini + Tavily for production.

## 🛠️ Development

```bash
# Install in development mode
pip install -e .

# Run tests (coming soon)
pytest

# Format code
black deal_copilot/
```

## 📝 License

This is a proof-of-concept for demonstration purposes.

## 🤝 Contributing

See documentation in `deal_copilot/docs/` for details.

---

**Built with** ❤️ **using LangChain, Gemini, OpenAI, and Tavily**

