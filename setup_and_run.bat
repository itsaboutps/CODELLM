@echo off
echo 🚀 Document Assistant RAG - Setup and Run
echo =========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt
pip install python-docx

REM Verify installation
echo ✅ Verifying installation...
python -c "import streamlit, docx, chromadb; print('✅ All dependencies installed successfully!')"

REM Ask user what to run
echo.
echo 🎯 What would you like to run?
echo 1) Main Streamlit Application (app.py)
echo 2) Production DOCX Testing
echo 3) Comprehensive Testing Suite
set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" (
    echo 🌟 Starting Streamlit Application...
    streamlit run app.py
) else if "%choice%"=="2" (
    echo 🧪 Running Production DOCX Testing...
    python production_docx_tester.py
) else if "%choice%"=="3" (
    echo 🔬 Running Comprehensive Testing Suite...
    python comprehensive_test_advanced.py
) else (
    echo ❌ Invalid choice. Starting Streamlit Application by default...
    streamlit run app.py
)

pause