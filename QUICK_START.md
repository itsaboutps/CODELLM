# 🚀 Quick Start Commands

## One-Command Setup and Run

### macOS/Linux:
```bash
# Make executable and run
chmod +x setup_and_run.sh && ./setup_and_run.sh
```

### Windows (Command Prompt):
```cmd
setup_and_run.bat
```

### Windows (PowerShell):
```powershell
# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run:
.\setup_and_run.ps1
```

## Manual Quick Setup

### Prerequisites Installation

**macOS/Linux:**
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt python-docx
```

**Windows:**
```cmd
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt python-docx
```

### Run Commands

**Start Main Application:**
```bash
# macOS/Linux
source .venv/bin/activate && streamlit run app.py

# Windows
.venv\Scripts\activate && streamlit run app.py
```

**Run Production Testing:**
```bash
# macOS/Linux  
source .venv/bin/activate && python production_docx_tester.py

# Windows
.venv\Scripts\activate && python production_docx_tester.py
```

## Dependencies Summary

Core dependencies that will be installed:
- `streamlit` - Web interface
- `chromadb` - Vector database
- `python-docx` - DOCX document processing
- `sentence-transformers` - Text embeddings
- `transformers` - NLP models
- `torch` - Machine learning framework
- `pandas`, `numpy` - Data processing
- `bert-score` - Semantic evaluation
- `spacy` - Advanced NLP processing

## System Requirements

- **Python:** 3.8 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space for models
- **OS:** Windows 10+, macOS 10.14+, Linux

## Access URLs

After starting the application:
- **Main App:** http://localhost:8501
- **Alternative Port:** http://localhost:8502 (if 8501 is busy)

## Troubleshooting

1. **Python not found:** Install Python 3.8+ and add to PATH
2. **Permission denied (macOS/Linux):** Run `chmod +x setup_and_run.sh`
3. **PowerShell execution policy:** Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
4. **Dependencies fail:** Update pip with `pip install --upgrade pip`