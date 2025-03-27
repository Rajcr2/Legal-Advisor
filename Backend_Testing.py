# Backend_Testing.py

import psycopg2
import pymupdf  # PyMuPDF
from io import BytesIO
import ollama
from Embedded_Testing import retrieve_relevant_laws  # ✅ Use similarity search

def fetch_pdf_from_db(pdf_name):
    conn = psycopg2.connect(
        dbname="RAG_db",  # 🔁 Same as Embeddings.py
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT pdf_data FROM legal_docs WHERE name = %s", (pdf_name,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return BytesIO(result[0]) if result else None

def extract_text(pdf_stream):
    doc = pymupdf.open(stream=pdf_stream.read(), filetype="pdf")
    return "\n".join(page.get_text("text") for page in doc)

def generate_response(pdf_name):
    pdf_stream = fetch_pdf_from_db(pdf_name)
    if not pdf_stream:
        return f"❌ No PDF found: {pdf_name}"
    pdf_text = extract_text(pdf_stream)
    prompt = f"Summarize the key legal points from this document:\n\n{pdf_text}"
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

def get_all_pdf_names():
    conn = psycopg2.connect(
        dbname="RAG_db",
        user="postgres",
        password="rajcar18",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT name FROM legal_docs")
    results = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results

def generate_combined_response(user_query):
    # ✅ Step 1: Use ChromaDB to get relevant chunks
    relevant_chunks = retrieve_relevant_laws(user_query)

    if not relevant_chunks:
        return "⚠️ No relevant documents found to answer this query."

    # ✅ Step 2: Use retrieved chunks to query Ollama
    combined_context = "\n\n".join(relevant_chunks)
    prompt = (
        f"Based on the following legal information, answer the user's question:\n\n"
        f"{combined_context}\n\n"
        f"User's Question: {user_query}\n\n"
        "If you don't find an answer, say: 'I need more legal documents to answer this properly.'"
    )

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]
