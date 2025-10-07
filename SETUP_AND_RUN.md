# Document Assistant RAG - Setup and Run Guide

## 🚀 Quick Start Guide for Windows and macOS

### Prerequisites
- Python 3.8 or higher
- Git (optional, for cloning)

---

## 📦 Installation Instructions

### For macOS/Linux:

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install additional DOCX support
pip install python-docx

# 6. Verify installation
python -c "import streamlit, docx, chromadb; print('✅ All dependencies installed successfully!')"
```

### For Windows (Command Prompt):

```cmd
REM 1. Create virtual environment
python -m venv .venv

REM 2. Activate virtual environment
.venv\Scripts\activate

REM 3. Upgrade pip
python -m pip install --upgrade pip

REM 4. Install dependencies
pip install -r requirements.txt

REM 5. Install additional DOCX support
pip install python-docx

REM 6. Verify installation
python -c "import streamlit, docx, chromadb; print('✅ All dependencies installed successfully!')"
```

### For Windows (PowerShell):

```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
.venv\Scripts\Activate.ps1

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install additional DOCX support
pip install python-docx

# 6. Verify installation
python -c "import streamlit, docx, chromadb; print('✅ All dependencies installed successfully!')"
```

---

## 🏃‍♂️ Running the Application

### Method 1: Run Streamlit App (Main Application)

**macOS/Linux:**
```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run the main Streamlit application
streamlit run app.py
```

**Windows (Command Prompt):**
```cmd
REM Activate virtual environment (if not already active)
.venv\Scripts\activate

REM Run the main Streamlit application
streamlit run app.py
```

**Windows (PowerShell):**
```powershell
# Activate virtual environment (if not already active)
.venv\Scripts\Activate.ps1

# Run the main Streamlit application
streamlit run app.py
```

### Method 2: Run Production Testing

**macOS/Linux:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Run production DOCX testing
python production_docx_tester.py
```

**Windows (Command Prompt):**
```cmd
REM Activate virtual environment
.venv\Scripts\activate

REM Run production DOCX testing
python production_docx_tester.py
```

**Windows (PowerShell):**
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run production DOCX testing
python production_docx_tester.py
```

### Method 3: Run Comprehensive Testing

**macOS/Linux:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Run comprehensive testing suite
python comprehensive_test_advanced.py
```

**Windows (Command Prompt):**
```cmd
REM Activate virtual environment
.venv\Scripts\activate

REM Run comprehensive testing suite
python comprehensive_test_advanced.py
```

**Windows (PowerShell):**
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run comprehensive testing suite
python comprehensive_test_advanced.py
```

---

## 🛠️ Automated Setup Scripts

### For macOS/Linux: `setup_and_run.sh`

```bash
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
```

### For Windows: `setup_and_run.bat`

```batch
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
```

### For Windows PowerShell: `setup_and_run.ps1`

```powershell
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
```

---

## 📋 One-Line Commands

### Quick Start Commands:

**macOS/Linux:**
```bash
# Setup and run in one command
bash -c "python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt python-docx && streamlit run app.py"
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt python-docx && streamlit run app.py
```

**Windows (PowerShell):**
```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt python-docx; streamlit run app.py
```

---

## 🔧 Troubleshooting

### Common Issues:

1. **Permission Error on Windows PowerShell:**
   ```powershell
   # Run this command first to allow script execution:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Python not found:**
   - Ensure Python 3.8+ is installed and added to PATH
   - Try using `python3` instead of `python` on macOS/Linux

3. **Virtual environment activation fails:**
   - Delete `.venv` folder and recreate it
   - Ensure you have proper permissions

4. **Dependencies installation fails:**
   - Upgrade pip: `pip install --upgrade pip`
   - Try installing dependencies individually

5. **ChromaDB issues:**
   - Install Visual C++ Redistributable on Windows
   - Update to latest pip version

### System Requirements:
- **Python:** 3.8 or higher
- **RAM:** Minimum 4GB, recommended 8GB
- **Storage:** At least 2GB free space
- **OS:** Windows 10+, macOS 10.14+, or Linux

---

## 🎯 Usage After Installation

1. **Main Application:** Upload DOCX documents and ask questions
2. **Testing Suite:** Verify system performance with test documents
3. **Production Testing:** Run comprehensive validation tests

The application will be available at: `http://localhost:8501`

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure you're using the correct Python version (3.8+)