#!/bin/bash

set -e

echo "🏴‍☠️ AI Engineering Investigator - Setup Script"
echo "=============================================="
echo ""

if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - GITLAB_TOKEN"
    echo "   - GITLAB_WEBHOOK_SECRET"
    echo "   - GITLAB_PROJECT_ID"
    echo ""
else
    echo "✅ .env file already exists"
fi

if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "📁 Creating data directories..."
mkdir -p data/repos data/chroma
echo "✅ Data directories created"

echo ""
echo "=============================================="
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys and configuration"
echo "2. Run the service:"
echo "   source venv/bin/activate"
echo "   python src/main.py"
echo ""
echo "Or use Docker:"
echo "   docker-compose up -d"
echo ""
echo "3. Configure GitLab webhook pointing to:"
echo "   http://your-server:8000/webhook/gitlab"
echo ""
echo "Happy investigating! 🔍"
