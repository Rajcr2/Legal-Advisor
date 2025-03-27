# Embedded_Testing.py (FINAL VERSION - FIXED & CLEAN)
import psycopg2
import chromadb
import requests
import pdfplumber
import time
import io
from langchain.text_splitter import CharacterTextSplitter

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "mistral"

def get_mistral_embedding(texts):
    embeddings = []
    for text in texts:
        response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": text})
        if response.status_code == 200:
            embeddings.append(response.json().get("embedding", []))
        else:
            print(f"❌ Error fetching embedding for text: {response.text}")
            embeddings.append([])
    return embeddings

def get_pdf_data():
    conn = psycopg2.connect(
        dbname="RAG_db",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT name, pdf_data FROM legal_docs")
    pdf_data_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return pdf_data_list

def get_existing_sources(collection):
    try:
        results = collection.get(include=["metadatas"])
        sources = {meta["source"] for meta in results["metadatas"]}
        return sources
    except Exception:
        return set()

def generate_embeddings():
    print("🔄 Generating embeddings incrementally...")

    pdf_data_list = get_pdf_data()
    if not pdf_data_list:
        print("❌ No documents found in PostgreSQL.")
        return

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("legal_embeddings")
    existing_sources = get_existing_sources(collection)

    doc_count = 0
    for pdf_name, pdf_binary in pdf_data_list:
        if pdf_name in existing_sources:
            print(f"✅ Vector embeddings already exist for '{pdf_name}'. Skipping.")
            continue

        extracted_text = []
        pdf_stream = io.BytesIO(pdf_binary)
        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)

        if not extracted_text:
            print(f"⚠️ No text found in '{pdf_name}'. Skipping.")
            continue

        combined_text = "\n".join(extracted_text)
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(combined_text)

        if not chunks:
            print(f"⚠️ No valid text chunks for '{pdf_name}'. Skipping.")
            continue

        batch_size = 5
        total_chunks = len(chunks)
        embeddings = []  # ✅ Initialize embeddings inside the loop

        print(f"\n📄 '{pdf_name}' split into {total_chunks} chunks. Processing in {total_chunks // batch_size + 1} batches...\n")

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            print(f"⏳ Processing batch {i // batch_size + 1}/{(total_chunks // batch_size) + 1} for '{pdf_name}'...")
            start_time = time.time()

            try:
                batch_embeddings = get_mistral_embedding(batch)
                if len(batch_embeddings) == len(batch):  # Ensure embedding length matches batch size
                    embeddings.extend(batch_embeddings)
                else:
                    print(f"⚠️ Skipping batch {i // batch_size + 1} due to embedding mismatch.")
            except Exception as e:
                print(f"❌ Error in embedding batch {i // batch_size + 1}: {e}")
                continue

            print(f"✅ Batch {i // batch_size + 1} completed in {time.time() - start_time:.2f}s.\n")

        # Push new embeddings
        ids = [f"{pdf_name}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": pdf_name} for _ in range(len(chunks))]

        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

        doc_count += 1
        print(f"✅ Embedded '{pdf_name}' successfully.")

    if doc_count == 0:
        print("📭 No new PDFs were embedded.")
    else:
        print(f"\n🎉 Finished embedding {doc_count} new document(s).")

if __name__ == "__main__":
    generate_embeddings()
