# Legal-Advisor

## Introduction
I have built an **Agentic Legal Question-Answering System** using **LangGraph**, **Retrieval-Augmented Generation (RAG)** and **DeepEval**.
The system performs multi-step ReAct reasoning, retrieves and then filters legal context, generates grounded answers with respect to query and also, evaluates QA system performance using structured semantic and retrieval-based metrics.

## Overview

This project implements an **Semi-Autonomous ReAct-style AI agent** capable of :

- **Understanding legal questions**
- **Planning multi-step reasoning**
- **Retrieving relevant legal documents with respect to questions**
- **Filtering useful context from retrieved context**
- **Generating grounded answers**
- **Evaluating answer quality automatically**

The system demonstrates **agentic behavior**, **non-deterministic reasoning** and evaluation-driven development.

## Key Features

- **Autonomous LangGraph agent workflow**
- **ReAct-style reasoning** (Think → Act → Observe → Answer)
- **Retrieval-Augmented Generation** (RAG)
- **Vector-based semantic search**
- **Context filtering** (Selector)
- **Grounded answers**
- **Multi-step reasoning loop**
- **Evaluation framework using DeepEval**
- **Golden dataset regression testing**

## System Architecture

<img width="350" height="692" alt="System Architecture - Final" src="https://github.com/user-attachments/assets/1d503668-b3fa-4958-b6e1-41ca99b6e04d" />

## Agent Workflow

The agent follows a **ReAct-style autonomous loop** :

1. **Think** - analyze query & decide next action
2. **Act** - retrieve legal context from vector database
3. **Observe** - evaluate retrieved information
4. **Repeat** - until sufficient knowledge obtained
5. **Answer** - generate final grounded response

The agent stops naturally when retrieved knowledge stabilizes.

### Prerequisites
To run this project, you need to install the following libraries :

### Required Libraries

- **Python 3.12+**
- **PostgreSQL**: PostgreSQL is a powerful, open-source object-relational database system known for its reliability along with SQL compliance.
- **ChromaDB**: ChromaDB is an open-source embedding database designed for storing, querying, and retrieving vector embeddings for RAG applications.
- **Ollama**: Ollama is a lightweight tool that lets you run large language models (LLMs) like Mistral-7B, llama3 locally.
- **Langgraph**: LangGraph is a framework for building stateful, multi-step AI agent workflows. It enables controlled reasoning, tool orchestration, and conditional execution using graph-based pipelines.
- **Deepeval**: DeepEval is an evaluation framework for LLM and RAG systems that measures answer quality, faithfulness, hallucination, retrieval relevance, and overall task performance using structured metrics.

Other Utility Libraries : **psycopg2**, **textwrap**.

### Installation

   ```
   ollama serve
   ollama run mistral
   pip install langgraph
   pip install psycopg2-binary
   pip install chromadb
   pip install deepeval
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

   <img width="1920" height="1080" alt="Store py" src="https://github.com/user-attachments/assets/d313727c-7d69-4600-aacb-25307e80ee16" />

   <img width="1920" height="1080" alt="Store Postgre" src="https://github.com/user-attachments/assets/30c64697-6ff7-41ef-8b1f-02e8b4ba877b" />

________

7.   Lets, generate vector Embeddings now. for that, Run following command :
   
    python Embeddings.py

<img width="1920" height="1080" alt="Embeddings py" src="https://github.com/user-attachments/assets/f5f8e812-4efa-4699-8830-0782e960532e" />

________

8.   Now, we are almost done. Now, Run **'python ReAct.py'** file from Terminal. This will start "Legal Advisor" in Terminal.
   
    python ReAct.py


Ask any legal question like this **"My employer ignored my complaint, what are my rights ? Under POSH Act ?"** and get the **'legal Advice'**.

### Output

https://github.com/user-attachments/assets/e3975903-e483-4f30-9dfa-000920a14f15


