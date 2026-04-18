from fastmcp import FastMCP
from ReAct import autonomous_agent

mcp = FastMCP("Legal Advisor")

@mcp.tool()
def ask_legal_question(question: str) -> str:
    return autonomous_agent(question)

if __name__ == "__main__":
    mcp.run()
