# Legal-Advisor

## Introduction

In this project, I am developing a RAG Based Legal advisor system. which gives you legal advice as per your query.

### Key Features

1. **Uses Legal law documents (vector embedded to extract more relevant data) to form response.**
2. **Mistral-7B (Ollama) lighweight llm**

### Objectives

The primary goal of this project generate response based on stored pdf's in database if context is missing then use llm and provide most close accurate legal solution.

### Prerequisites
To run this project, you need to install the following libraries:
### Required Libraries

- **Python 3.12+**
- **PostgreSQL**: PostgreSQL is a powerful, open-source object-relational database system known for its reliability along with SQL compliance.
- **ChromaDB**: ChromaDB is an open-source embedding database designed for storing, querying, and retrieving vector embeddings for RAG applications.
- **Ollama**: Ollama is a lightweight tool that lets you run large language models (LLMs) like Mistral-7B locally.
- **Langchain**: LangChain is a framework that helps developers build applications powered by large language models (LLMs) by connecting them with data sources for for tasks like chatbots, RAG, and agents.

Other Utility Libraries : **psycopg2**, **pdfplumber**, **pyMupdf**.

### Installation

   ```
   ollama serve
   ollama run mistral
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
   You will get output like below :
   
![image](https://github.com/user-attachments/assets/db02c381-7c15-4894-bb98-0b84b1e52c98)

7.   Lets, generate vector Embeddings now.s   
7.   After, that Run **'streamlit run Frontend_Testing.py'** file from Terminal. To activate the dashboard on your browser.
   ```
   streamlit run QP_main.py
   ``` 
7. Now, move to your browser.
8. Ask any legal question like this **"What are the provisions for anticipatory bail under the Bhartiya Nyaya Sanhita ?"**.
   and all set you will get response just verify that.

Currently, Model is in still developement stage I am adding more legal documents one by the one. Currently, response you are seeing is based on "BNS.pdf" legal doucment and Mistral LLM knowledge.

### PromptEvaluator

The main reason for developing this tool is because, prompt allows you indirectly set how much power you want to give to llm and here, in case if for specific question uploaded documents are just not enough sometimes at that prompt which is leveraging Documents & LLM equally is required. 
Thats where PromptEvaluator is needed which helps in designing and testing different parallely without affecting whole main RAG project.

### Output

1. #### Legal Advisor



https://github.com/user-attachments/assets/558d1134-e2bf-4326-95b1-d4a4b32da48a

2. #### Prompt Evaluator

https://github.com/user-attachments/assets/14f4e4b4-6fb9-42f1-82c1-eef0db0b0225

### Conclusion






