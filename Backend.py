#### Backend.py

import psycopg2
import pymupdf  # PyMuPDF
from io import BytesIO
import ollama
from Embeddings import retrieve_relevant_laws  # ✅ Use similarity search

def fetch_pdf_from_db(pdf_name):
    conn = psycopg2.connect(
        dbname="RAG_db_llama",  # 🔁 Same as Embeddings.py
        user="postgres",
        password="rajcar18",
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
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

def get_all_pdf_names():
    conn = psycopg2.connect(
        dbname="RAG_db_llama",
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
    # ✅ Step 1: Retrieve relevant context via ChromaDB
    relevant_chunks = retrieve_relevant_laws(user_query)
    combined_context = "\n\n".join(relevant_chunks) if relevant_chunks else ""

    # ✅ Step 2: Weighted Prompt (60% embeddings/context + 40% LLM reasoning)
    prompt = f"""
    You are an intelligent legal assistant trained to answer queries using both:
    - Legal context from trusted PDF sources and embeddings (priority: 60%)
    - Your own legal reasoning and general knowledge (limited to 2023 cutoff) (priority: 40%)

    Follow this approach:

    1. First, examine the legal context below and try to directly answer the user's question.
    2. If partial info is found, use your own legal reasoning to fill gaps (based on known legal frameworks).
    3. If no relevant info is available in context and your knowledge is outdated or insufficient (e.g., for 2025 events), say: "I need more legal documents or up-to-date resources to answer this properly."

    Legal Context:
    {combined_context}

    User Question:
    {user_query}

    Answer:
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt.strip()}]
    )
    return response["message"]["content"]
