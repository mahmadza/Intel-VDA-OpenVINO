import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";

export function ChatInterface({ activeVideoId }: { activeVideoId: number }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);

  const sendMessage = async () => {
    if (!input) return;

    // 1. Add user message to UI
    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      // 2. Call local AI via Rust bridge
      const reply = await invoke<string>("send_chat_message", {
        videoId: activeVideoId,
        message: input,
      });

      // 3. Add AI response to UI
      setMessages((prev) => [...prev, { role: "assistant", text: reply }]);
    } catch (err) {
      console.error("Chat failed:", err);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-log">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <strong>{m.role === "user" ? "You" : "AI"}:</strong> {m.text}
          </div>
        ))}
      </div>
      <div className="input-row">
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="Ask about the video..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}