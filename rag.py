# rag.py
import os
import numpy as np
import faiss
from utils.pdf_reader import extract_text_from_pdf
from utils.embeddings import get_embeddings
from utils.vector_store import create_vector_store, search
import subprocess
import tempfile
import time

DATA_DIR = "data/vectors"
os.makedirs(DATA_DIR, exist_ok=True)

# Global storage
PDF_CHUNKS = []
PDF_INDEX = None

# ---------------------------
# 🔹 Run Ollama - UNLIMITED Version
# ---------------------------
def ask_ollama(question, context="", model="phi3", callback=None):
    """
    Ask Ollama a question with optional context.
    Uses temp file method for reliability on Windows.
    This version has no time or length limits.
    """
    
    # Build prompt
    if context and len(context.strip()) > 0:
        # Limit context to prevent overflow (this is for the input, not the output)
        if len(context) > 1500:
            context = context[:1500] + "..."
        prompt = f"Based on this context, answer the question briefly.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
    else:
        prompt = question
    
    try:
        # Write prompt to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(prompt)
            temp_path = f.name
        
        # Run ollama with input from file
        command = f'ollama run {model} < "{temp_path}"'
        
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        full_response = ""
        
        # Simplified loop to read output without timeouts or length checks
        while True:
            # Read output character by character for smooth streaming
            try:
                char = process.stdout.read(1)
            except Exception as e:
                # This can happen if the process is closed unexpectedly
                break
            
            # If there's no more output and the process has ended, break the loop
            if not char and process.poll() is not None:
                break

            if not char:
                time.sleep(0.005) # Small sleep to prevent a busy-wait loop
                continue
            
            # Filter out non-printable characters (except newlines/tabs/spaces)
            if char.isprintable() or char in ['\n', '\r', '\t', ' ']:
                full_response += char
                if callback:
                    callback(char)
                else:
                    print(char, end='', flush=True)
            elif ord(char) < 32 and char not in ['\n', '\r', '\t']:
                # Skip control characters
                continue
        
        process.wait()
        
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        if not callback:
            print()
        
        return full_response.strip()
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}\n"
        if callback:
            callback(error_msg)
        else:
            print(error_msg)
        return error_msg

# ---------------------------
# 🔹 Process PDF
# ---------------------------
def process_pdf(pdf_path):
    """Process PDF and create vector store"""
    global PDF_CHUNKS, PDF_INDEX
    
    try:
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            return False
        
        print(f"\n📄 Extracting text from: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)
        
        if not text or len(text.strip()) == 0:
            print("❌ No text extracted from PDF")
            return False
        
        print(f"✅ Extracted {len(text)} characters")
        print("🔪 Splitting into chunks...")

        # Create chunks with better size
        chunk_size = 400
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size].strip()
            if len(chunk) > 50:  # Filter out tiny chunks
                chunks.append(chunk)
        
        print(f"🧩 Created {len(chunks)} chunks")
        
        if len(chunks) == 0:
            print("❌ No valid chunks created")
            return False
        
        print("🔮 Generating embeddings...")
        embeddings = get_embeddings(chunks)
        
        print("💾 Creating vector store...")
        index = create_vector_store(np.array(embeddings))

        # Store globally for fast access
        PDF_CHUNKS = chunks
        PDF_INDEX = index
        
        # Save to disk
        faiss.write_index(index, os.path.join(DATA_DIR, "index.faiss"))
        with open(os.path.join(DATA_DIR, "chunks.txt"), "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(c + "\n<<<SEPARATOR>>>\n")

        print(f"✅ PDF processed successfully ({len(chunks)} chunks indexed)")
        return True
    
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

# ---------------------------
# 🔹 Ask from PDF
# ---------------------------
def ask_from_pdf(question, callback=None):
    """Query PDF using RAG"""
    global PDF_CHUNKS, PDF_INDEX
    
    try:
        # Load if not in memory
        if PDF_INDEX is None or len(PDF_CHUNKS) == 0:
            index_path = os.path.join(DATA_DIR, "index.faiss")
            chunks_path = os.path.join(DATA_DIR, "chunks.txt")

            if not os.path.exists(index_path):
                error_msg = "⚠️ No PDF loaded. Please load a PDF first.\n"
                if callback:
                    callback(error_msg)
                else:
                    print(error_msg)
                return error_msg

            print("📂 Loading PDF data from disk...")
            PDF_INDEX = faiss.read_index(index_path)
            with open(chunks_path, "r", encoding="utf-8") as f:
                PDF_CHUNKS = [c.strip() for c in f.read().split("\n<<<SEPARATOR>>>\n") if c.strip()]
            print(f"✅ Loaded {len(PDF_CHUNKS)} chunks")

        # Search for relevant chunks
        print(f"🔍 Searching for: {question[:50]}...")
        query_embedding = get_embeddings([question])
        
        # Get top 2 most relevant chunks (using 2 instead of 3 for faster responses)
        top_indices = search(np.array(query_embedding), PDF_INDEX, k=2)[0]
        
        # Build context
        context_parts = []
        for idx in top_indices:
            if 0 <= idx < len(PDF_CHUNKS):
                context_parts.append(PDF_CHUNKS[idx])
        
        if not context_parts:
            error_msg = "⚠️ No relevant context found in PDF.\n"
            if callback:
                callback(error_msg)
            else:
                print(error_msg)
            return error_msg
        
        context = " ".join(context_parts)
        print(f"✅ Using {len(context_parts)} chunks ({len(context)} chars)")
        print("🤖 Generating answer...\n")
        
        # Ask Ollama with context
        response = ask_ollama(question, context=context, model="phi3", callback=callback)
        return response
    
    except Exception as e:
        error_msg = f"❌ Error querying PDF: {e}\n"
        if callback:
            callback(error_msg)
        else:
            print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg

# ---------------------------
# 🔹 Clear PDF data
# ---------------------------
def clear_pdf_data():
    """Clear PDF data from memory"""
    global PDF_CHUNKS, PDF_INDEX
    PDF_CHUNKS = []
    PDF_INDEX = None
    print("🗑️ PDF data cleared from memory")