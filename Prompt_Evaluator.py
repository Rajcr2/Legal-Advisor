import streamlit as st
import ollama
import chromadb
import requests

# 🔍 Function to retrieve relevant legal chunks using ChromaDB
def retrieve_relevant_laws(user_query, top_k=5):
    # Connect to the existing ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("legal_embeddings")

    # Step 1: Get embedding for user query using Ollama
    OLLAMA_URL = "http://localhost:11434/api/embeddings"
    MODEL_NAME = "mistral"
    
    response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": user_query})
    if response.status_code != 200:
        print("❌ Error generating embedding for user query.")
        return []

    query_embedding = response.json().get("embedding", [])
    if not query_embedding:
        print("⚠️ No embedding returned for query.")
        return []

    # Step 2: Query ChromaDB using vector similarity
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents"]
        )
        return results["documents"][0]
    except Exception as e:
        print(f"❌ Error querying ChromaDB: {e}")
        return []

# 🔁 Define multiple prompt templates
prompt_variants = [
    "Use the context below to answer the legal question.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:",
    "Given the following legal information, provide a concise response to the user's query.\n\n{context}\n\nQ: {question}\nA:",
    "With reference to the legal context, respond briefly.\n\n{context}\n\nQuery: {question}\nAnswer:",
    "Please read the following context and answer accordingly:\n\n{context}\n\nLegal Query: {question}\nAnswer:",
    "Based on legal context, give an accurate reply.\n\n{context}\n\nQ: {question}\nA:",
    "Answer the legal question using ONLY the context.\n\n{context}\n\nQuestion: {question}\nAnswer:"
]

# ⚙️ Function to evaluate all prompt variants
def evaluate_prompts(question):
    responses = []

    # Step 1: Get relevant legal chunks from ChromaDB
    relevant_chunks = retrieve_relevant_laws(question)
    if not relevant_chunks:
        return ["⚠️ No relevant context found for the question."] * len(prompt_variants)

    context = "\n\n".join(relevant_chunks)

    # Step 2: Generate responses for each prompt variant
    for idx, template in enumerate(prompt_variants):
        filled_prompt = template.format(context=context, question=question)
        try:
            response = ollama.chat(
                model="mistral",
                messages=[{"role": "user", "content": filled_prompt}]
            )
            responses.append(response["message"]["content"])
        except Exception as e:
            responses.append(f"❌ Error in Prompt {idx + 1}: {str(e)}")

    return responses

# --------------------------
# 🚀 Streamlit UI
# --------------------------
st.set_page_config(page_title="Prompt Evaluator", layout="centered")

st.title("Prompt Evaluator")
st.write("Test multiple prompt templates at once and compare responses. To find out Best performing Prompt.")

# User input
user_question = st.text_area("🔍 Enter your legal question :", height=100)

if st.button("Evaluate Prompts"):
    if not user_question.strip():
        st.warning("⚠️ Please enter a question first.")
    else:
        with st.spinner("🚀 Evaluating prompts..."):
            responses = evaluate_prompts(user_question)

        st.success("✅ Prompt Evaluation Completed")

        # Display results
        for i, response in enumerate(responses):
            with st.expander(f"Prompt  {i+1}"):
                st.code(prompt_variants[i], language="markdown")
                st.subheader("📜 Response")
                st.write(response)

# Footer
st.markdown(
    """
    ---
    **💡 Tip:** Try asking questions like:  
    - "Can I be evicted without notice?"  
    - "What are my rights under BNSS?"  
    If your question isn't covered, the chatbot will inform you.
    """,
    unsafe_allow_html=True
)


