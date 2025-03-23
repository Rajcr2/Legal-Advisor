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

def get_pdf_data_from_db():
    conn = psycopg2.connect(
        dbname="RAG_db",
        user="postgres",
        password="rajcar18",
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
        data = collection.get()
        return set(meta['source'] for meta in data['metadatas'])
    except Exception as e:
        print(f"⚠️ Error reading from collection: {e}")
        return set()

def generate_embeddings_incrementally():
    print("🔍 Checking for new or deleted PDFs...")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("legal_embeddings")

    existing_sources = get_existing_sources(collection)
    pdf_data_list = get_pdf_data_from_db()

    db_pdf_names = set(name for name, _ in pdf_data_list)

    to_add = []
    to_add_data = {}
    for name, binary in pdf_data_list:
        if name not in existing_sources:
            to_add.append(name)
            to_add_data[name] = binary

    to_remove = list(existing_sources - db_pdf_names)

    print(f"📥 New PDFs to embed: {to_add}")
    print(f"🗑️ PDFs to remove: {to_remove}")

    # Step 1: Remove stale embeddings
    if to_remove:
        collection.delete(where={"source": {"$in": to_remove}})
        print(f"✅ Removed embeddings for: {to_remove}")

    # Step 2: Process new PDFs
    law_chunks, metadata_list = [], []
    for name in to_add:
        extracted_text = []
        pdf_stream = io.BytesIO(to_add_data[name])
        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
        if extracted_text:
            combined_text = "\n".join(extracted_text)
            splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_text(combined_text)
            law_chunks.extend(chunks)
            metadata_list.extend([{"source": name}] * len(chunks))

    if not law_chunks:
        print("✅ No new chunks to embed.")
        return

    # Step 3: Embedding & storing
    print(f"🔄 Embedding {len(law_chunks)} chunks with Mistral...")
    batch_size = 5
    embeddings = []
    for i in range(0, len(law_chunks), batch_size):
        batch = law_chunks[i:i+batch_size]
        print(f"⏳ Batch {i//batch_size + 1}...")
        start_time = time.time()
        batch_embeddings = get_mistral_embedding(batch)
        embeddings.extend(batch_embeddings)
        print(f"✅ Batch done in {time.time() - start_time:.2f}s")

    if len(embeddings) != len(law_chunks):
        print("❌ Mismatch in embeddings.")
        return

    collection.upsert(
        ids=[f"doc_{int(time.time())}_{i}" for i in range(len(law_chunks))],
        documents=law_chunks,
        embeddings=embeddings,
        metadatas=metadata_list
    )

    print("✅ New embeddings saved successfully!")

def retrieve_relevant_laws(query):
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("legal_embeddings")
        query_embedding = get_mistral_embedding([query])
        if not query_embedding or len(query_embedding[0]) == 0:
            return ["❌ Query embedding failed."]
        results = collection.query(query_embeddings=query_embedding, n_results=3)
        return results["documents"][0] if "documents" in results else []
    except Exception as e:
        print(f"❌ Error during retrieval: {e}")
        return ["Error retrieving legal information."]

if __name__ == "__main__":
    generate_embeddings_incrementally()
