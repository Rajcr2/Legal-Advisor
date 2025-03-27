import streamlit as st
from Backend_Testing import generate_combined_response

st.set_page_config(page_title="Legal Advisor Chatbot", layout="centered")

# --------------------------
# 🧑‍⚖️ Legal Chatbot UI
# --------------------------
st.title("🧑‍⚖️ Legal Advisor Chatbot")
#st.write("Ask any legal question and get an AI-generated answer based on stored PDFs.")

# User input
query = st.text_area("Ask your legal question:", height=100)

# Button to generate legal advice
if st.button("Get Legal Advice"):
    if not query.strip():
        st.warning("⚠️ Please enter a legal question before submitting.")
    else:
        with st.spinner("🔍 Analyzing your question and fetching legal advice..."):
            try:
                response = generate_combined_response(query)
                st.success("✅ Legal Advice Retrieved Successfully")
                st.subheader("📜 Legal Advice")
                st.write(response)
            except Exception as e:
                st.error(f"❌ Error while generating advice: {str(e)}")

st.markdown(
    """
    **💡 Tip:** Try asking questions like:  
    - "Can I be evicted without notice?"  
    - "What are my rights under BNSS?"  
    If your question isn't covered, the chatbot will inform you.
    """,
    unsafe_allow_html=True,
)
