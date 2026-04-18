import { useState, useRef, useEffect } from "react";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function ask() {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setMessages(p => [...p, { role: "user", text: question }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/v1/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question })
      });

      const data = await res.json();
      setMessages(p => [...p, { role: "bot", text: data.answer }]);
    } catch {
      setMessages(p => [...p, { role: "bot", text: "⚠️ Backend not reachable" }]);
    }

    setLoading(false);
  }

  function end() {
    setMessages([]);
    setInput("");
  }

  return (
    <div className="container">
      <h1>🧑‍⚖️ Legal Advisor Chatbot</h1>

      <div className="card">
        <label>Ask your legal question:</label>

        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && ask()}
          placeholder="e.g. What are duties of employer under POSH Act?"
        />

        <div className="buttons">
          <button onClick={ask} disabled={loading} className="primary">
            {loading ? "Getting Legal Advice..." : "Get Legal Advice"}
          </button>

          <button onClick={end} className="danger">
            End Conversation
          </button>
        </div>
      </div>

      {messages.length === 0 && (
        <div className="tips">
          <p><strong>💡 Tip:</strong> Try asking questions like:</p>
          <ul>
            <li>What are the conditions for a valid Hindu marriage?</li>
            <li>What are duties of an employer under POSH Act?</li>
            <li>What rights does a Hindu wife have?</li>
          </ul>
        </div>
      )}

      <div className="chat">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "user-msg" : "bot-msg"}>
            {m.text}
          </div>
        ))}

        {loading && <div className="bot-msg">Thinking...</div>}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}