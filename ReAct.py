import chromadb
from typing import TypedDict, List
from langchain_ollama import ChatOllama
from textwrap import dedent
from langgraph.graph import StateGraph, END

# ---------------- CONFIG ----------------
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "legal_sections"
LLM_MODEL = "mistral:7b"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(COLLECTION_NAME)

llm = ChatOllama(model=LLM_MODEL, temperature=0.6)

# ---------------- STATE ----------------
class State(TypedDict):
    query: str
    retrieved_docs: List[str]
    selected_docs: List[str]
    final_answer: str
    scratchpad: str
    last_docs: List[str]
    next_action: str 

# ---------------- Tools ----------------
def retriever(state: State):
    results = collection.query(query_texts=[state["query"]], n_results=10)
    state["retrieved_docs"] = results["documents"][0]
    print(f"\n[Retriever] Retrieved {len(state['retrieved_docs'])} chunks")
    return state

def selector(state: State):
    shortlisted = []

    for chunk in state["retrieved_docs"]:
        prompt = dedent(f"""
            You are a STRICT legal relevance evaluator.

            TASK:
            Decide whether the given legal chunk is DIRECTLY useful to answer the query.

            RULES:
            - Accept ONLY if chunk contains legal meaning related to the query.
            - Accept if synonyms or different legal wording express same meaning.
            - Reject if chunk is general, unrelated, procedural, or weakly related.
            - Reject if chunk does not help answer the query directly.
            - Be strict. Do NOT guess.

            Query:
            {state['query']}

            Chunk:
            {chunk}

            Answer ONLY in one word:
            YES or NO
            """)

        if "YES" in llm.invoke(prompt).content.upper():
            shortlisted.append(chunk)

    state["selected_docs"] = shortlisted
    print(f"[Selector] Shortlisted {len(shortlisted)} relevant chunks")
    return state

def answer_generator(state: State):
    if not state["selected_docs"]:
        state["final_answer"] = "No relevant legal information found."
        return state

    context = "\n\n".join(state["selected_docs"])

    prompt = dedent(f"""
        You are a precise Legal AI Assistant.

        Use ONLY the provided legal context to answer the query.
        Do NOT hallucinate.
        If answer not fully available, answer using best possible legal interpretation from context.

        Legal Context:
        {context}

        Query:
        {state['query']}

        Give clear, legally correct, concise answer.
        Answer Clearly in points.
        """)

    state["final_answer"] = llm.invoke(prompt).content.strip()

    print("\n=========== FINAL ANSWER ===========\n")
    print(state["final_answer"])
    print("\n====================================\n")

    return state

# ---------------- RE-ACT DECISION NODE ----------------
def react_decision(state: State):

    prompt = dedent(f"""
        You are an autonomous Legal ReAct Agent.

        Question:
        {state['query']}

        Previous reasoning:
        {state['scratchpad']}

        Decide next action:

        - retrieve → search legal database for evidence
        - answer → produce final grounded legal answer

        Reply EXACTLY in format:

        Thought: <your reasoning>
        Action: <retrieve OR answer>
        """)

    decision = llm.invoke(prompt).content.strip()
    print("\n[AGENT THINKING]\n", decision)

    state["scratchpad"] += f"\n{decision}\n"

    state["next_action"] = "retrieve" if "retrieve" in decision.lower() else "answer"

    return state

def route_from_react(state: State):
    return state["next_action"]

# ---------------- CHECK INFORMATION SUFFICIENCY ----------------
def check(state: State):

    docs = state.get("selected_docs", [])
    print("[AGENT OBSERVATION] → Collected", len(docs), "legal chunks")

    current_docs = tuple(docs)
    last_docs = tuple(state.get("last_docs", []))

    # If same docs repeated → stop and answer
    if current_docs == last_docs and len(current_docs) > 0:
        print("[AGENT] Enough information to Answer the Query → generating final answer.")
        state["next_action"] = "answer"
    else:
        state["last_docs"] = list(current_docs)
        state["next_action"] = "react"

    return state

def route_from_check(state: State):
    return state["next_action"]

# ---------------- LANGGRAPH WORKFLOW ----------------
graph = StateGraph(State)

graph.add_node("react", react_decision)
graph.add_node("retrieve", retriever)
graph.add_node("select", selector)
graph.add_node("check", check)
graph.add_node("answer", answer_generator)

graph.set_entry_point("react")

graph.add_conditional_edges(
    "react",
    route_from_react,
    {"retrieve": "retrieve", "answer": "answer"}
)

graph.add_edge("retrieve", "select")
graph.add_edge("select", "check")

graph.add_conditional_edges(
    "check",
    route_from_check,
    {"react": "react", "answer": "answer"}
)

graph.add_edge("answer", END)

graph = graph.compile()

# ---------------- AUTONOMOUS EXECUTION ----------------
def autonomous_agent(query):

    state: State = {
        "query": query,
        "retrieved_docs": [],
        "selected_docs": [],
        "final_answer": "",
        "scratchpad": "",
        "last_docs": [],
        "next_action": ""
    }

    result = graph.invoke(state)
    return result["final_answer"]

# ---------------- CLI ----------------
if __name__ == "__main__":

    print("\nLegal Advisor Ready (type 'exit' to quit)\n")

    while True:
        q = input("Ask legal question: ").strip()
        if q.lower() == "exit":
            break

        autonomous_agent(q)
        print("\n------------------------------------\n")
