import { useState, useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import "./App.css";

function App() {
  const [status, setStatus] = useState("Ready");
  const [progress, setProgress] = useState(0);
  const [history, setHistory] = useState<any[]>([]);
  const [activeVideoId, setActiveVideoId] = useState<number | null>(null);
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);
  

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    loadHistory(); // Load existing on mount

    const unlisten = listen("pipeline-progress", (event: any) => {
      setStatus(event.payload.status);
      setProgress(event.payload.percentage);

      // If analysis hits 100%, trigger a refresh of the history sidebar
      if (event.payload.percentage >= 100) {
        setTimeout(() => loadHistory(), 500); // Small delay to ensure DB write is closed
      }
    });

    return () => { unlisten.then((f) => f()); };
  }, []);

  useEffect(scrollToBottom, [messages]);  

  const loadHistory = async () => {
    try {
      const data = await invoke<any[]>("get_video_history");
      console.log("History loaded:", data);
      setHistory(data);
      return data;
    } catch (err) {
      // This will catch if the command name is wrong or Rust panics
      console.error("CRITICAL INVOKE ERROR:", err);
      setStatus(`Failed to load history: ${err}`);
    }
  };

  const handleSelectVideo = (id: number) => {
    setActiveVideoId(id);
    setMessages([]); 
    setStatus(`Viewing Video ID: ${id}`);
  };

  const handleProcess = async () => {
    try {
      // 1. Get the path from the native picker
      const path = await invoke<string>("select_video_file");
      
      // 2. Start the AI pipeline
      setStatus("Starting analysis...");
      setProgress(0); // Reset bar
      
      await invoke("run_vda_pipeline", { path });
      
      // 3. Finalize
      setStatus("Analysis Complete");
      const updatedHistory = await loadHistory();
      
      // Auto-select the one we just finished (usually the first in ID DESC order)
      if (updatedHistory && updatedHistory.length > 0) {
        handleSelectVideo(updatedHistory[0].id);
      }
      
    } catch (err) {
      setStatus(`Error: ${err}`);
    }
};

  const handleSendMessage = async () => {
    if (!chatInput || !activeVideoId) return;
    const userMsg = { role: "user", content: chatInput };
    setMessages(prev => [...prev, userMsg]);
    setChatInput("");

    try {
      const aiReply = await invoke<string>("send_chat_message", { 
        videoId: activeVideoId, 
        message: chatInput 
      });
      setMessages(prev => [...prev, { role: "assistant", content: aiReply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: `Error: ${err}` }]);
    }
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <h3>History ({history.length})</h3>
        <button onClick={handleProcess}>+ New Video</button>
        
        <div className="history-list">
          {history.map((v) => (
            <div key={v.id} className="history-item" onClick={() => handleSelectVideo(v.id)}>
              {v.file_name}
            </div>
          ))}
        </div>
      </aside>

      <main className="main-content">
        {activeVideoId ? (
          <div className="intelligence-view">
            <div className="chat-container">
              <div className="messages-log">
                {messages.map((m, i) => (
                  <div key={i} className={`message ${m.role}`}>
                    <strong>{m.role === 'user' ? 'User' : 'VDA Agent'}:</strong> {m.content}
                  </div>
                ))}
              </div>
              <div className="input-group">
                <input 
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Search video content..."
                />
                <button onClick={handleSendMessage}>Ask AI</button>
              </div>
            </div>
          </div>
        ) : (
          <div className="welcome-screen">
            <h2>{status === "Ready" ? "Select a video to begin" : status}</h2>
            {progress > 0 && <progress value={progress} max={100} />}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;