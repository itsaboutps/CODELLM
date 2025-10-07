#!/bin/bash

echo "🚀 Document Assistant RAG - Setup and Run"
echo "========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
pip install python-docx

# Verify installation
echo "✅ Verifying installation..."
python -c "import streamlit, docx, chromadb; print('✅ All dependencies installed successfully!')"

# Ask user what to run
echo ""
echo "🎯 What would you like to run?"
echo "1) Main Streamlit Application (app.py)"
echo "2) Production DOCX Testing"
echo "3) Comprehensive Testing Suite"
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🌟 Starting Streamlit Application..."
        streamlit run app.py
        ;;
    2)
        echo "🧪 Running Production DOCX Testing..."
        python production_docx_tester.py
        ;;
    3)
        echo "🔬 Running Comprehensive Testing Suite..."
        python comprehensive_test_advanced.py
        ;;
    *)
        echo "❌ Invalid choice. Starting Streamlit Application by default..."
        streamlit run app.py
        ;;
esac