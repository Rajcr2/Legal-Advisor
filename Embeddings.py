import fitz
import re
import psycopg2
import chromadb
from sentence_transformers import SentenceTransformer

# -------------------- LOAD PDFs FROM DB --------------------
def get_pdf_data():
    conn = psycopg2.connect(
        dbname="Act_db",
        user="postgres",
        password="qpss",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT name, pdf_data FROM legal_docs")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

# -------------------- READ PDF --------------------
def load_pdf_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

# -------------------- SECTION PARSER --------------------
section_pattern = re.compile(
    r'^\s*(\d+[A-Z]*)\.\s+(.*?)\.—',
    re.MULTILINE
)

def extract_sections(text):

    matches = list(section_pattern.finditer(text))
    sections = []

    for i, match in enumerate(matches):

        section_number = match.group(1)
        section_name = match.group(2).strip()

        start = match.end()
        end = matches[i + 1].start() if i < len(matches) - 1 else len(text)

        body = text[start:end].strip()

        sections.append({
            "section_number": section_number,
            "section_name": section_name,
            "section_body": body,
            "full_text": f"Section {section_number}: {section_name}\n\n{body}"
        })

    return sections

# -------------------- CHROMADB MANAGER --------------------
class EmbeddingStore:

    def __init__(self, chroma_path="./chroma_db"):

        print("→ Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("→ Initializing ChromaDB...")
        self.client = chromadb.PersistentClient(path=chroma_path)

        self.collection = self.client.get_or_create_collection(
            name="legal_sections"
        )

        print(f"Stored vectors: {self.collection.count()}")

    def get_processed_docs(self):

        data = self.collection.get()
        done = set()

        for m in data["metadatas"]:
            done.add(m["document_name"])

        return done

    def embed_and_store(self, doc_name, sections):

        if not sections:
            return

        print(f"→ Generating embeddings for {len(sections)} sections...")

        texts = [s["full_text"] for s in sections]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        ids, docs, metas, embs = [], [], [], []

        for sec, emb in zip(sections, embeddings):

            sec_id = f"{doc_name}__sec_{sec['section_number']}"

            ids.append(sec_id)
            docs.append(sec["full_text"])
            embs.append(emb.tolist())

            metas.append({
                "document_name": doc_name,
                "section_number": sec["section_number"],
                "section_name": sec["section_name"]
            })

        self.collection.upsert(
            ids=ids,
            embeddings=embs,
            documents=docs,
            metadatas=metas
        )

        print(f"[STORE] Total vectors now: {self.collection.count()}")

# -------------------- MAIN --------------------
def main():

    print("\nLoading PDFs from PostgreSQL...")
    pdfs = get_pdf_data()
    print(f"Found {len(pdfs)} PDFs")

    store = EmbeddingStore()
    processed = store.get_processed_docs()

    for name, pdf_bytes in pdfs:

        if name in processed:
            print(f"[SKIP] Already processed → {name}")
            continue

        print(f"\nProcessing → {name}")

        text = load_pdf_text(pdf_bytes)
        sections = extract_sections(text)

        print(f"Extracted {len(sections)} sections")

        store.embed_and_store(name, sections)

    print("\n✓ DONE")

if __name__ == "__main__":
    main()

