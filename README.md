# Legal-Advisor

## Introduction

In this project, I am developing a RAG Based Legal advisor system. which gives you legal advice as per your query.

### Objectives

The primary goal of this project generate response based on stored pdf's in database if context is missing then use llm and provide most close accurate legal solution.

### Prerequisites
To run this project, you need to install the following libraries:
### Required Libraries

- **Python 3.12+**
- **PostgreSQL**: PostgreSQL is a powerful, open-source object-relational database system known for its reliability along with SQL compliance.
- **ChromaDB**: ChromaDB is an open-source embedding database designed for storing, querying, and retrieving vector embeddings for RAG applications.
- **Ollama**: Ollama is a lightweight tool that lets you run large language models (LLMs) like Mistral-7B, llama3 locally.
- **Langchain**: LangChain is a framework that helps developers build applications powered by large language models (LLMs) by connecting them with data sources for for tasks like chatbots, RAG, and agents.

Other Utility Libraries : **psycopg2**, **pdfplumber**, **pyMupdf**.

### Installation

   ```
   ollama serve
   ollama run llama3
   pip install langchain
   pip install psycopg2-binary
   pip install pdfplumber
   pip install puMupdf
   pip install chromadb
   pip install time
   pip install requests
   ```

### Procedure

1.   Create new directory **'Legal Advisor'**.
2.   Inside that directory/folder create new environment.
   
   ```
   python -m venv legaladv
   ```

  Now, activate this **'legaladv'** venv.
  
4.   Clone this Repository :

   ```
   git clone https://github.com/Rajcr2/LegalAdvisor.git
   ```
5.   Now, Install all mentioned required libraries in your environment.
6.   Firstly Store legal documents in PostgreSQL for that run following command.
   ```
   python Store.py
   ``` 
   When pdfs are succefully stored you will get output like below :
   
![store](https://github.com/user-attachments/assets/6ef8066f-191b-44ad-aedb-3eaae503acc8)

7.   Lets, generate vector Embeddings now. for that, Run following command :
   
    python Embeddings.py
    
![embeddings](https://github.com/user-attachments/assets/b30ddc17-7ebb-4b51-bb1a-ef0b7ef65d7b)

8.   Now, we are almost done. Just Run **'streamlit run Frontend.py'** file from Terminal. To activate the UI Interface on your browser.
   
    streamlit run Frontend.py
   
   Ask any legal question like this **"What are Non-bailable offences under BNS ?"** and get the **'legal Advice'**. 

### Currently, Model is in still developement stage I am adding more legal documents one by the one. Currently, response you are seeing is based on limited legal documents (all are uploaded here) and llama3 LLM knowledge.

### Output

1. #### Legal Advisor

https://github.com/user-attachments/assets/2b45d4e0-4bdc-4372-86d7-365522d36d11

                           _____________________________________________________________

## PromptEvaluator

The main reason for developing this tool is because, prompt allows you indirectly to set how much power you want to give to llm and here, in case if for specific question uploaded documents are just not enough sometimes at that time a prompt is required which can leverage Documents & LLM equally to generate response. 
So, Thats where PromptEvaluator is needed which helps in designing and testing different Prompts parallely without affecting whole main RAG project.


https://github.com/user-attachments/assets/97ef5a04-2786-474e-85a4-8769e848fffe

Along with Evaluating Multiple Prompts at once, It also Benchmarks Prompts on the basis of various metrics such as **Hallucination Score, Latency, Perplexity** and **Semantic Similarity**.
that directly helps in structuring best possible prompt without chopping and changing main project each and every time.

![image](https://github.com/user-attachments/assets/e7e5c4ee-4b5d-44e0-b2da-0853a197502e)

### Conclusion

The Legal advisor is ready which acts as **Mini AI Advocate** you will see better version soon. Stay Tuned.






