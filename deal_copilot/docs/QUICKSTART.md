# Quick Start Guide

Get up and running with the Deep Research Agent in 5 minutes!

## Step 1: Get API Keys (5 minutes)

### Google Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Tavily API Key
1. Go to https://tavily.com/
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key

## Step 2: Setup (2 minutes)

### Option A: Automated Setup (Linux/Mac)
```bash
./setup.sh
```

Then edit `.env` file with your API keys.

### Option B: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
EOF
```

Replace `your_gemini_api_key_here` and `your_tavily_api_key_here` with your actual keys.

## Step 3: Run Your First Research (1 minute)

### Option A: Example Script
```bash
python example_run.py
```

This runs research on **Bizzi** (the example from statement.md).

### Option B: Interactive Mode
```bash
python main.py
```

Then enter your company details when prompted.

### Option C: Command Line
```bash
python main.py \
  --company "Bizzi" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://bizzi.vn/en/"
```

## What to Expect

The agent will:
1. 🔍 Search public web sources using Tavily
2. 🤖 Analyze findings using Google Gemini
3. 📄 Generate a comprehensive report with:
   - Market Overview
   - Competitor Overview
   - Company/Team Overview
4. ✅ Include citations for every claim

Typical runtime: **2-5 minutes** depending on the company and sector.

## Sample Output

```
================================================================================
DEEP RESEARCH REPORT
================================================================================

Company: Bizzi
Sector: SaaS
Region: Vietnam
...

## Market Overview

The SaaS market in Vietnam is experiencing rapid growth... [Source: URL]

TAM for enterprise software in Southeast Asia is estimated at $X billion... [Source: URL]

...
```

## Need Help?

- **API Key Issues**: Check your `.env` file
- **Import Errors**: Make sure virtual environment is activated
- **No Results**: Verify internet connection and API keys

See full [README.md](README.md) for detailed documentation.

---

**Pro Tip**: Save reports to files for later review:
```bash
python main.py \
  --company "YourCompany" \
  --sector "SaaS" \
  --region "Vietnam" \
  --website "https://example.com" \
  --output reports/mycompany.txt
```
