# Document Assistant RAG

A sophisticated Retrieval Augmented Generation (RAG) system that allows users to upload documents and ask questions about their content with intelligent scope validation.

## Features

### 🚀 Core Capabilities
- **Multi-format Document Support**: PDF, DOCX, TXT, and Markdown files
- **Advanced Text Chunking**: Semantic, recursive character, and sentence-based splitting
- **High-Quality Embeddings**: Using Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB for efficient similarity search
- **Multiple LLM Options**: OpenAI GPT and Hugging Face models
- **Scope Validation**: Intelligent detection of out-of-scope queries
- **Interactive Web Interface**: Streamlit-based user-friendly interface

### 🧠 Advanced Features
- **Content-Aware Chunking**: Different strategies for code, tables, and paragraphs
- **Context Preservation**: Overlapping chunks maintain context continuity
- **Semantic Search**: Find relevant information using meaning, not just keywords
- **Source Attribution**: See which documents and sections answers came from
- **Error Handling**: Robust processing with graceful fallbacks

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd CodeLLM
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Set up OpenAI API** (for GPT models):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   # Or create a .env file with: OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Starting the Application

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`

### Using the Document Assistant

1. **Upload Documents**: 
   - Use the sidebar to upload PDF, DOCX, TXT, or Markdown files
   - Multiple files can be uploaded simultaneously
   - Processing happens automatically

2. **Ask Questions**:
   - Type questions about your uploaded documents in the chat interface
   - Get contextual answers with source attributions
   - Receive warnings for out-of-scope questions

3. **Review Sources**:
   - Click on source expandables to see which document sections were used
   - Understand the context behind each answer

### Example Queries

**Good (In-scope) Questions**:
- "What are the main points discussed in the document?"
- "Can you summarize the key findings from Chapter 3?"
- "What does the author say about [specific topic]?"
- "According to the document, how does [process] work?"

**Out-of-scope Questions** (will be flagged):
- "What's the weather today?"
- "Can you recommend a good restaurant?"
- "What's the latest news about [unrelated topic]?"

## Architecture

### Core Components

1. **RAG Engine** (`backend/rag_engine.py`)
   - Orchestrates the entire RAG pipeline
   - Manages embeddings and vector storage
   - Integrates with multiple LLM providers

2. **Document Processor** (`backend/document_processor.py`)
   - Extracts text from various document formats
   - Handles encoding detection and text cleaning
   - Robust error handling for corrupted files

3. **Text Chunker** (`backend/text_chunker.py`)
   - Advanced chunking strategies based on content type
   - Preserves context with intelligent overlapping
   - Handles code, tables, and regular text differently

4. **Scope Validator** (`backend/scope_validator.py`)
   - Validates query relevance using multiple methods
   - Semantic similarity and keyword analysis
   - Pattern-based out-of-scope detection

### Technology Stack

- **Frontend**: Streamlit for interactive web interface
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB with persistent storage
- **LLM Options**: 
  - OpenAI GPT-3.5/4 (requires API key)
  - Hugging Face Transformers (free, local)
- **Document Processing**: PyPDF2, pdfplumber, python-docx
- **Text Processing**: Advanced regex and NLP techniques

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API (optional, for GPT models)
OPENAI_API_KEY=your-openai-api-key

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MIN_CHUNK_SIZE=100

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM Configuration
LLM_PROVIDER=huggingface  # or "openai"
LLM_MODEL=microsoft/DialoGPT-small
```

### Customization Options

You can customize the RAG system by modifying parameters in the code:

- **Chunk sizes**: Adjust `chunk_size` and `chunk_overlap` in `text_chunker.py`
- **Embedding model**: Change the model in `rag_engine.py`
- **LLM provider**: Switch between OpenAI and Hugging Face models
- **Similarity thresholds**: Tune scope validation sensitivity

## Performance Tips

### For Better Results
1. **Upload high-quality documents**: Clear text, good formatting
2. **Use specific questions**: More specific queries get better answers
3. **Check document scope**: Ensure questions relate to uploaded content
4. **Multiple documents**: Upload related documents for comprehensive coverage

### System Requirements
- **Memory**: 4GB+ RAM recommended (8GB+ for large documents)
- **Storage**: Vector database grows with document size
- **CPU**: Modern multi-core processor for faster processing
- **GPU**: Optional, improves Hugging Face model performance

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **PDF Processing Fails**:
   ```bash
   pip install pymupdf  # Alternative PDF processor
   ```

3. **Memory Issues with Large Documents**:
   - Reduce chunk size
   - Process documents individually
   - Use a machine with more RAM

4. **Slow Performance**:
   - Use GPU acceleration if available
   - Switch to lighter embedding models
   - Reduce the number of retrieved chunks

### Logs and Debugging

The application logs important information to help with debugging:
- Document processing status
- Chunking statistics  
- Query processing details
- Error messages with context

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Check code style
flake8 .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Sentence Transformers**: For high-quality embeddings
- **ChromaDB**: For efficient vector storage
- **Streamlit**: For the interactive web interface
- **Hugging Face**: For free, accessible LLM models
- **OpenAI**: For advanced language understanding capabilities

## Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Include error logs and system information

---

**Built with ❤️ for better document understanding and knowledge extraction**# CODELLM
