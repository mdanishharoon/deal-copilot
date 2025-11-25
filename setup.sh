#!/bin/bash

# Setup script for Deal Co-Pilot POC

echo "=================================="
echo "Deal Co-Pilot POC - Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

# Check if .env exists
echo ""
if [ -f .env ]; then
    echo "✅ .env file found"
else
    echo "⚠️  .env file not found"
    echo ""
    echo "Creating .env template..."
    cat > .env << EOF
# API Keys - Replace with your actual keys
GOOGLE_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
EOF
    echo ""
    echo "📝 Please edit .env and add your API keys:"
    echo "   - Get Gemini API key from: https://makersuite.google.com/app/apikey"
    echo "   - Get Tavily API key from: https://tavily.com/"
    echo ""
fi

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the example: python example_run.py"
echo "   Or use: python main.py --company 'Bizzi' --sector 'SaaS' --region 'Vietnam' --website 'https://bizzi.vn/en/'"
echo ""
