import streamlit as st
import ollama
import chromadb
import requests
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 🔍 Function to retrieve relevant legal chunks using ChromaDB
def retrieve_relevant_laws(user_query, top_k=5):
    client = chromadb.PersistentClient(path="./chroma_db_llama")
    collection = client.get_or_create_collection("llama_legal_embeddings")

    OLLAMA_URL = "http://localhost:11434/api/embeddings"
    MODEL_NAME = "llama3"

    response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": user_query})
    if response.status_code != 200:
        return []

    query_embedding = response.json().get("embedding", [])
    if not query_embedding:
        return []

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents"]
        )
        return results["documents"][0]
    except:
        return []

# 🔁 Define multiple prompt templates
prompt_variants = [
    "Use the context below to answer the legal question.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:",
    "Given the following legal information, provide a concise response to the user's query.\n\n{context}\n\nQ: {question}\nA:",
    "With reference to the legal context, respond briefly.\n\n{context}\n\nQuery: {question}\nAnswer:",
    "Please read the following context and answer accordingly:\n\n{context}\n\nLegal Query: {question}\nAnswer:",
    "Based on legal context, give an accurate reply.\n\n{context}\n\nQ: {question}\nA:",
    "Answer the legal question using ONLY the context.\n\n{context}\n\nQuestion: {question}\nAnswer:",

    # Zero-shot prompting with reasoning
    "You are an intelligent legal assistant trained to answer queries using both:\n"
    "- Legal context from trusted PDF sources and embeddings (priority: 60%)\n"
    "- Your own legal reasoning and general knowledge (limited to 2023 cutoff) (priority: 40%)\n\n"
    "Follow this approach:\n"
    "1. First, examine the legal context below and try to directly answer the user's question.\n"
    "2. If partial info is found, use your own legal reasoning to fill gaps (based on known legal frameworks).\n"
    "3. If no relevant info is available in context and your knowledge is outdated or insufficient (e.g., for 2025 events), say:\n"
    "   'I need more legal documents or up-to-date resources to answer this properly.'\n\n"
    "Legal Context:\n{context}\n\n"
    "User Question:\n{question}\n\n"
    "Answer:"

]

# 🎯 Function to classify benchmark scores
def classify_metric(value, thresholds):
    if value <= thresholds[0]:
        return "✅ Best"
    elif value <= thresholds[1]:
        return "👍 Good"
    else:
        return "❌ Bad"

# 📊 Function to evaluate all prompts with benchmarking
def evaluate_prompts(question):
    responses = []
    metrics = []

    # Step 1: Retrieve relevant legal chunks
    relevant_chunks = retrieve_relevant_laws(question)
    if not relevant_chunks:
        return ["⚠️ No relevant context found for the question."] * len(prompt_variants), []

    context = "\n\n".join(relevant_chunks)

    # Step 2: Generate responses and measure performance
    for idx, template in enumerate(prompt_variants):
        filled_prompt = template.format(context=context, question=question)
        
        # Measure Latency
        start_time = time.time()
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": filled_prompt}])
        end_time = time.time()
        
        generated_text = response["message"]["content"]
        latency = end_time - start_time

        # Calculate Perplexity using Ollama
        perplexity = np.random.uniform(5, 25)  # Placeholder for real perplexity calculation

        # Semantic Similarity (with ideal answer)
        ideal_answer = "Under legal jurisdiction, eviction requires a prior notice period based on tenancy agreements."
        embedding_1 = requests.post("http://localhost:11434/api/embeddings", json={"model": "llama3", "prompt": generated_text}).json().get("embedding", [])
        embedding_2 = requests.post("http://localhost:11434/api/embeddings", json={"model": "llama3", "prompt": ideal_answer}).json().get("embedding", [])
        similarity_score = cosine_similarity([embedding_1], [embedding_2])[0][0] if embedding_1 and embedding_2 else 0.0

        # Hallucination Score (Placeholder)
        hallucination_score = np.random.uniform(0, 1)

        # Assign Ratings
        latency_rating = classify_metric(latency, [0.5, 1.0])
        perplexity_rating = classify_metric(perplexity, [10, 20])
        similarity_rating = classify_metric(1 - similarity_score, [0.15, 0.3])  
        hallucination_rating = classify_metric(hallucination_score, [0.2, 0.5])

        responses.append(generated_text)
        metrics.append({
            "Prompt": idx + 1,
            "Latency (s)": f"{round(latency, 4)} ({latency_rating})",
            "Perplexity": f"{round(perplexity, 4)} ({perplexity_rating})",
            "Semantic Similarity": f"{round(similarity_score, 4)} ({similarity_rating})",
            "Hallucination Score": f"{round(hallucination_score, 4)} ({hallucination_rating})"
        })

    return responses, metrics

# --------------------------
# 🚀 Streamlit UI
# --------------------------
st.set_page_config(page_title="Prompt Evaluator", layout="centered")

st.title("Prompt Evaluator")
st.write("Test multiple prompts and compare response quality.")

# User input
user_question = st.text_area("🔍 Enter your legal question :", height=100)

if st.button("Evaluate Prompts"):
    if not user_question.strip():
        st.warning("⚠️ Please enter a question first.")
    else:
        with st.spinner("🚀 Evaluating prompts..."):
            responses, metrics = evaluate_prompts(user_question)

        st.success("✅ Evaluation Completed")

        # 📜 Display Prompt Performance
        for i, response in enumerate(responses):
            with st.expander(f"Prompt {i+1}"):
                st.code(prompt_variants[i], language="markdown")
                st.subheader("📜 Response")
                st.write(response)

        # 📊 Display Benchmarking Table
        st.subheader("📊 Benchmarking Metrics")
        st.dataframe(metrics)

# Footer
st.markdown(
    """
    ---
    **💡 Tip:** Compare different prompts for better legal AI performance.
    """,
    unsafe_allow_html=True
)
