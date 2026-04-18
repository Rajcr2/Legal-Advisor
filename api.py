from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ReAct import autonomous_agent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Legal Advisor API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/ask")
async def ask(query: Query):

    print("\n>>> API HIT")
    print("Query:", query.question)

    if not query.question.strip():
        print(">>> ERROR: Empty question received")
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        answer = autonomous_agent(query.question)
        return {"answer": answer}
    except Exception as e:
        print(">>> ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Legal Advisor API Running"}