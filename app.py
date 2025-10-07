"""
Document Assistant RAG - Main Application Entry Point

A sophisticated Retrieval Augmented Generation system for document Q&A
with advanced chunking, embedding, and scope validation.
"""

import streamlit as st
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.document_processor import DocumentProcessor

# Try to import enhanced components first, fallback to basic if needed
try:
    from backend.enhanced_rag_engine import EnhancedRAGEngine as RAGEngine
    from backend.enhanced_scope_validator import EnhancedScopeValidator as ScopeValidator
    enhanced_mode = True
    print("✨ Using enhanced RAG engine with best free models")
except ImportError as e:
    print(f"⚠️ Enhanced models not available ({e}), using basic versions")
    from backend.rag_engine import RAGEngine
    from backend.scope_validator import ScopeValidator
    enhanced_mode = False

def main():
    """Main Streamlit application for Document Assistant RAG"""
    st.set_page_config(
        page_title="Document Assistant RAG",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Document Assistant RAG")
    
    # Show which version is running
    if enhanced_mode:
        st.success("✨ Running with Enhanced RAG Engine (Best Free Models)")
        st.caption("Features: FAISS vector storage, all-mpnet-base-v2 embeddings, BERT-Score validation, spaCy NLP")
    else:
        st.info("⚙️ Running with Basic RAG Engine")
        st.caption("Enhanced models not available - using fallback implementations")
    
    st.markdown("Upload documents and ask questions about their content with intelligent scope validation.")
    
    # Initialize session state
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = RAGEngine()
    if 'processed_docs' not in st.session_state:
        st.session_state.processed_docs = []
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("📁 Document Upload")
        uploaded_files = st.file_uploader(
            "Choose documents",
            type=['pdf', 'txt', 'docx', 'md'],
            accept_multiple_files=True,
            help="Upload PDF, TXT, DOCX, or Markdown files"
        )
        
        if uploaded_files:
            with st.spinner("Processing documents..."):
                for file in uploaded_files:
                    if file.name not in [doc['name'] for doc in st.session_state.processed_docs]:
                        try:
                            # Process and add document
                            success = st.session_state.rag_engine.add_document(file)
                            if success:
                                st.session_state.processed_docs.append({
                                    'name': file.name,
                                    'size': file.size
                                })
                                st.success(f"✅ {file.name} processed successfully")
                            else:
                                st.error(f"❌ Failed to process {file.name}")
                        except Exception as e:
                            st.error(f"❌ Error processing {file.name}: {str(e)}")
        
        # Display processed documents
        if st.session_state.processed_docs:
            st.subheader("📄 Processed Documents")
            for doc in st.session_state.processed_docs:
                st.write(f"• {doc['name']} ({doc['size']:,} bytes)")
            
            if st.button("🗑️ Clear All Documents"):
                st.session_state.rag_engine.clear_documents()
                st.session_state.processed_docs = []
                st.rerun()
    
    # Main chat interface
    if not st.session_state.processed_docs:
        st.info("👆 Please upload documents using the sidebar to start asking questions.")
        return
    
    st.header("💬 Ask Questions About Your Documents")
    
    # Display chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat input
    question = st.chat_input("Ask a question about your documents...")
    
    if question:
        # Add user question to chat history
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        with st.spinner("Thinking..."):
            try:
                # Get response from RAG engine
                response = st.session_state.rag_engine.query(question)
                
                # Add response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": response['answer'],
                    "sources": response.get('sources', []),
                    "in_scope": response.get('in_scope', True)
                })
            except Exception as e:
                st.error(f"Error processing question: {str(e)}")
    
    # Display chat history
    for i, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show sources and scope info for assistant messages
            if message["role"] == "assistant":
                if not message.get("in_scope", True):
                    st.warning("⚠️ This question appears to be outside the scope of the uploaded documents.")
                
                if message.get("sources"):
                    with st.expander("📖 Sources"):
                        for j, source in enumerate(message["sources"], 1):
                            st.write(f"**Source {j}:**")
                            st.write(f"Document: {source.get('document', 'Unknown')}")
                            st.write(f"Content: {source.get('content', '')[:200]}...")

if __name__ == "__main__":
    main()