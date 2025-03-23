import streamlit as st
import ollama
from Embeddings_Testing import retrieve_relevant_laws

# Define multiple prompts (you can expand as needed)
prompt_variants = [
    "Use the context below to answer the legal question.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:",
    "Given the following legal information, provide a concise response to the user's query.\n\n{context}\n\nQ: {question}\nA:",
    "With reference to the legal context, respond briefly.\n\n{context}\n\nQuery: {question}\nAnswer:",
    "Please read the following context and answer accordingly:\n\n{context}\n\nLegal Query: {question}\nAnswer:",
    "Based on legal context, give an accurate reply.\n\n{context}\n\nQ: {question}\nA:",
    "Answer the legal question using ONLY the context.\n\n{context}\n\nQuestion: {question}\nAnswer:"
]

def evaluate_prompts_on_single_query(user_question):
    responses = []
    relevant_chunks = retrieve_relevant_laws(user_question)
    if not relevant_chunks:
        return [{"prompt": p, "response": "❌ No relevant context found."} for p in prompt_variants]

    context = "\n\n".join(relevant_chunks)

    for i, template in enumerate(prompt_variants):
        full_prompt = template.format(context=context, question=user_question)

        try:
            response = ollama.chat(model="mistral", messages=[
                {"role": "user", "content": full_prompt}
            ])
            answer = response["message"]["content"]
        except Exception as e:
            answer = f"❌ LLM Error: {str(e)}"

        responses.append({
            "prompt_id": f"Prompt {chr(65 + i)}",
            "prompt": template,
            "response": answer
        })

    return responses

# 🔹 Streamlit App
st.title("Prompt Evaluator")
user_question = st.text_input("🔍 Enter your legal question")

if st.button("🚀 Evaluate Prompts") and user_question.strip():
    with st.spinner("Generating responses from multiple prompt styles..."):
        prompt_outputs = evaluate_prompts_on_single_query(user_question)

    st.success("✅ Done! Review the responses below:")

    for output in prompt_outputs:
        st.markdown(f"### 🧾 {output['prompt_id']}")
        with st.expander("📄 Prompt Template"):
            st.code(output["prompt"], language="text")
        with st.expander("🧠 LLM Response"):
            st.write(output["response"])
