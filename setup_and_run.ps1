Write-Host "🚀 Document Assistant RAG - Setup and Run" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.8 or higher." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
if (!(Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install python-docx

# Verify installation
Write-Host "✅ Verifying installation..." -ForegroundColor Yellow
python -c "import streamlit, docx, chromadb; print('✅ All dependencies installed successfully!')"

# Ask user what to run
Write-Host ""
Write-Host "🎯 What would you like to run?" -ForegroundColor Cyan
Write-Host "1) Main Streamlit Application (app.py)" -ForegroundColor White
Write-Host "2) Production DOCX Testing" -ForegroundColor White
Write-Host "3) Comprehensive Testing Suite" -ForegroundColor White
$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host "🌟 Starting Streamlit Application..." -ForegroundColor Green
        streamlit run app.py
    }
    "2" {
        Write-Host "🧪 Running Production DOCX Testing..." -ForegroundColor Green
        python production_docx_tester.py
    }
    "3" {
        Write-Host "🔬 Running Comprehensive Testing Suite..." -ForegroundColor Green
        python comprehensive_test_advanced.py
    }
    default {
        Write-Host "❌ Invalid choice. Starting Streamlit Application by default..." -ForegroundColor Yellow
        streamlit run app.py
    }
}

Read-Host "Press Enter to exit"