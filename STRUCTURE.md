# Deal Co-Pilot - Project Structure

## 📁 Organized Folder Structure

```
vinnie/
├── deal_copilot/                    # 🎯 Main package
│   │
│   ├── agents/                      # 🤖 Agent implementations
│   │   ├── __init__.py
│   │   ├── deep_research_agent.py          # Gemini 2.5 + Tavily (RAG)
│   │   └── deep_research_agent_openai.py   # OpenAI GPT-4o
│   │
│   ├── config/                      # ⚙️  Configuration files
│   │   ├── __init__.py
│   │   ├── config.py                # Gemini + Tavily settings
│   │   └── config_openai.py         # OpenAI settings
│   │
│   ├── cli/                         # 💻 Command-line interfaces
│   │   ├── __init__.py
│   │   ├── main.py                  # Gemini + Tavily CLI
│   │   └── main_openai.py           # OpenAI CLI
│   │
│   ├── examples/                    # 🚀 Example scripts
│   │   ├── __init__.py
│   │   ├── example_run.py           # Gemini + Tavily example
│   │   └── example_run_openai.py    # OpenAI example
│   │
│   ├── docs/                        # 📚 Documentation
│   │   ├── README.md                # Gemini + Tavily docs
│   │   ├── README_OPENAI.md         # OpenAI docs
│   │   ├── COMPARISON.md            # Version comparison
│   │   ├── QUICKSTART.md            # 5-minute guide
│   │   └── PROJECT_SUMMARY.md       # Complete overview
│   │
│   └── output/                      # 📊 Generated reports
│       ├── .gitkeep
│       ├── bizzi_research_report.md
│       └── bizzi_research_report_openai.md
│
├── README.md                        # 📖 Main project README
├── STRUCTURE.md                     # 📁 This file
├── requirements.txt                 # 📦 Python dependencies
├── setup.sh                         # 🔧 Setup script
├── run_example_openai.sh           # ▶️  Quick run OpenAI
├── run_example_gemini.sh           # ▶️  Quick run Gemini
├── .env                            # 🔑 API keys (not in git)
├── .gitignore                      # 🚫 Git ignore rules
├── statement.md                    # 📋 Original requirements
└── venv/                           # 🐍 Python virtual environment
```

## 🎯 Key Directories

### `/deal_copilot/agents/`
Contains the two agent implementations:
- **Gemini + Tavily**: RAG architecture with explicit search control
- **OpenAI**: Integrated search, simpler setup

### `/deal_copilot/config/`
Configuration files for both versions:
- API keys management
- Model settings
- Search parameters

### `/deal_copilot/cli/`
Command-line interfaces:
- Accept company info via CLI arguments
- Interactive mode
- Save reports to files

### `/deal_copilot/examples/`
Example scripts for quick testing:
- Uses Bizzi (from statement.md) as example
- Easy to modify for other companies

### `/deal_copilot/docs/`
All documentation in one place:
- Version-specific README files
- Comparison guide
- Quick start guide
- Project summary

### `/deal_copilot/output/`
Generated reports go here:
- Text and Markdown formats
- Automatically ignored by git (except .gitkeep)

## 🚀 Quick Commands

### Run Examples

```bash
# OpenAI version (simplest)
./run_example_openai.sh
# or
python -m deal_copilot.examples.example_run_openai

# Gemini + Tavily version
./run_example_gemini.sh
# or
python -m deal_copilot.examples.example_run
```

### Run CLI

```bash
# OpenAI
python -m deal_copilot.cli.main_openai --company "Bizzi" --sector "SaaS" --region "Vietnam" --website "https://bizzi.vn/en/"

# Gemini + Tavily
python -m deal_copilot.cli.main --company "Bizzi" --sector "SaaS" --region "Vietnam" --website "https://bizzi.vn/en/"
```

### Use as Python Package

```python
# Import from organized structure
from deal_copilot.agents.deep_research_agent_openai import DeepResearchAgentOpenAI
from deal_copilot.agents.deep_research_agent import DeepResearchAgent

# Use the agent
agent = DeepResearchAgentOpenAI()
report = agent.generate_full_report(
    company_name="Bizzi",
    website="https://bizzi.vn/en/",
    sector="SaaS",
    region="Vietnam"
)
```

## 📦 Python Package Structure

The project is now a proper Python package with:
- `__init__.py` files in all directories
- Proper import paths: `from deal_copilot.agents import ...`
- Can be installed with `pip install -e .` for development

## 🔄 Module Imports

All imports have been updated to use the new structure:

```python
# Old imports (before reorganization)
from deep_research_agent import DeepResearchAgent
import config

# New imports (after reorganization)
from deal_copilot.agents.deep_research_agent import DeepResearchAgent
from deal_copilot.config import config
```

## 🎨 Benefits of This Structure

### ✅ **Organized**
- Clear separation of concerns
- Easy to navigate
- Professional structure

### ✅ **Scalable**
- Easy to add new agents
- Can add tests/ directory
- Can add utils/ directory

### ✅ **Maintainable**
- Grouped related files
- Clear module boundaries
- Easy to find things

### ✅ **Professional**
- Follows Python best practices
- Proper package structure
- Ready for PyPI if needed

### ✅ **Clean Root**
- Only essential files at root
- All code in deal_copilot/
- Documentation organized

## 📚 Documentation Locations

| Topic | Location |
|-------|----------|
| **Quick Start** | `/README.md` (root) |
| **Project Structure** | `/STRUCTURE.md` (this file) |
| **Gemini Version** | `/deal_copilot/docs/README.md` |
| **OpenAI Version** | `/deal_copilot/docs/README_OPENAI.md` |
| **Comparison** | `/deal_copilot/docs/COMPARISON.md` |
| **5-Min Guide** | `/deal_copilot/docs/QUICKSTART.md` |
| **Complete Summary** | `/deal_copilot/docs/PROJECT_SUMMARY.md` |
| **Requirements** | `/statement.md` |

## 🔧 Development Workflow

```bash
# 1. Setup
./setup.sh

# 2. Activate environment
source venv/bin/activate

# 3. Run examples
./run_example_openai.sh

# 4. Develop
# Edit files in deal_copilot/
# Imports will work automatically

# 5. Test changes
python -m deal_copilot.examples.example_run_openai
```

## 📝 Adding New Features

### Add a New Agent

1. Create `deal_copilot/agents/new_agent.py`
2. Add imports in `deal_copilot/agents/__init__.py`
3. Create example in `deal_copilot/examples/`
4. Add CLI in `deal_copilot/cli/`

### Add New Configuration

1. Create `deal_copilot/config/config_new.py`
2. Import in your agent
3. Document in `/deal_copilot/docs/`

### Add Tests

```bash
mkdir deal_copilot/tests
touch deal_copilot/tests/__init__.py
touch deal_copilot/tests/test_agents.py
```

## 🎯 Summary

The project is now well-organized with:

✅ All code in `deal_copilot/` package  
✅ Clear separation of agents, config, CLI, examples  
✅ All docs in `deal_copilot/docs/`  
✅ Clean root directory  
✅ Proper Python package structure  
✅ Easy to navigate and extend  

Everything works with the new structure - just use the updated import paths! 🚀

