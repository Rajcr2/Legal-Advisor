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
- **PostgreSQL**: This library performs data manipulation and analysis also provides powerful data structures like dataframes.
- **ChromaDB**: A forecasting tool for time-series data, designed to handle trends, seasonality and holidat effects.
- **Ollama**: Scikit-learn library provides tools for machine learning, including scalling, classification, regression, clustering, and dimensionality reduction.
- **Langchain**: Streamlit is a framework that builds interactive, data-driven web applications directly in python.  

Other Utility Libraries : **psycopg2**, **pdfplumber**, **pyMupdf**.

### Installation

   ```
   pip install ollama
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
6.   After, that Run **'streamlit run Frontend_Testing.py'** file from Terminal. To activate the dashboard on your browser.
   ```
   streamlit run QP_main.py
   ``` 
7. Now, move to your browser.
8. Ask any legal question like this **"What are the provisions for anticipatory bail under the Bhartiya Nyaya Sanhita ?"**.
   and all set you will get response just verify that.

Currently, Model is in still developement stage I am adding more legal documents one by the one. Currently, response you are seeing is based on "BNS.pdf" legal doucment and Mistral LLm knowledge.



### Output

1. #### Legal Advisor

https://github.com/user-attachments/assets/558d1134-e2bf-4326-95b1-d4a4b32da48a

2. #### Prompt Evaluator

https://github.com/user-attachments/assets/14f4e4b4-6fb9-42f1-82c1-eef0db0b0225









### Conclusion






