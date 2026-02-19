"""
Quick start guide for running the OpenClaw Python Skills.
"""

# First time setup:
# 1. Create virtual environment:
#    python -m venv venv
#    
# 2. Activate virtual environment:
#    On Windows: venv\Scripts\activate
#    On macOS/Linux: source venv/bin/activate
#
# 3. Install package and dependencies:
#    pip install -e ".[dev]"
#
# 4. Run example:
#    python example.py
#
# 5. Run tests:
#    pytest tests/

echo "Welcome to OpenClaw Python Skills!"
echo "Setting up environment..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

echo "✅ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev]"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Try these commands:"
echo "- Run examples:  python example.py"
echo "- Run tests:     pytest tests/"
echo "- Format code:   black src tests"
echo "- Lint code:     ruff check src tests"
echo "- Type check:    mypy src"
