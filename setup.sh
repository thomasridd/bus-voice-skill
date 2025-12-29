#!/bin/bash
# Quick setup script for TfL Bus Checker development environment

set -e  # Exit on error

echo "🚀 Setting up TfL Bus Checker development environment..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or later."
    echo "   macOS: brew install python@3.11"
    echo "   Ubuntu: sudo apt install python3.11 python3.11-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if venv exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📚 Installing production dependencies..."
cd lambda
pip install -r requirements.txt --quiet

echo "🛠️  Installing development dependencies..."
pip install -r requirements-dev.txt --quiet
cd ..

# Set up pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

echo ""
echo "✨ Setup complete! ✨"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "Quick start commands:"
echo "  make help       - Show all available commands"
echo "  make test       - Run tests"
echo "  make ci         - Run all CI checks"
echo ""
echo "📖 Read QUICKSTART.md for next steps!"
