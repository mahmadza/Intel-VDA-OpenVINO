import { useState, useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { ask } from '@tauri-apps/plugin-dialog';
import "./App.css";

function App() {
  const [status, setStatus] = useState("Ready");
  const [progress, setProgress] = useState(0);
  const [history, setHistory] = useState<any[]>([]);
  const [activeVideoId, setActiveVideoId] = useState<number | null>(null);
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [isChatting, setIsChatting] = useState(false);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    loadHistory(); // Load existing history

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
      const path = await invoke<string>("select_video_file");
      
      setStatus("Starting analysis...");
      setProgress(0); // Reset bar
      
      await invoke("run_vda_pipeline", { path });
      setStatus("Analysis Complete");
      const updatedHistory = await loadHistory();
      
      if (updatedHistory && updatedHistory.length > 0) {
        handleSelectVideo(updatedHistory[0].id);
      }
      
    } catch (err) {
      setStatus(`Error: ${err}`);
    }
};

  const handleSendMessage = async () => {
    if (!chatInput || !activeVideoId || isChatting) return;
    const userMsg = { role: "user", content: chatInput };
    setMessages(prev => [...prev, userMsg]);
    setChatInput("");

    setIsChatting(true);
    
    try {
      const aiReply = await invoke<string>("send_chat_message", { 
        videoId: activeVideoId, 
        message: chatInput 
      });
      setMessages(prev => [...prev, { role: "assistant", content: aiReply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: `Error: ${err}` }]);
    } finally {
      setIsChatting(false);
    }
  };

  const handleDeleteVideo = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();

    const confirmed = await ask(
      'This will permanently remove the analysis results from the database.', 
      { 
        title: 'Delete Analysis?',
        kind: 'warning',
        okLabel: 'Delete',
        cancelLabel: 'Cancel'
      }
    );

    if (confirmed) {
      try {
        console.log("🗑️ Deleting ID:", id);
        await invoke("delete_video", { videoId: id });
        
        setHistory(prev => prev.filter(v => v.id !== id));
        
        if (activeVideoId === id) {
          setActiveVideoId(null);
          setMessages([]);
        }
        
        setStatus("Video deleted successfully.");
      } catch (err) {
        console.error("❌ Delete failed:", err);
        setStatus(`Error: ${err}`);
      }
    } else {
      console.log("❌ Deletion cancelled by user.");
    }
  };


  return (
    <div className="app-layout">
      <aside className="sidebar">
        <h3>History ({history.length})</h3>
        <button onClick={handleProcess}>+ New Video</button>
        
        <div className="history-list">
          {history.map((v) => (
            <div 
              key={v.id} 
              className={`history-item ${activeVideoId === v.id ? 'active' : ''}`} 
              onClick={() => handleSelectVideo(v.id)}
              style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
            >
              <span>{v.file_name}</span>
              <button 
                onClick={(e) => handleDeleteVideo(v.id, e)}
                style={{ padding: '2px 8px', background: 'transparent', border: 'none', color: '#ff4d4f', fontSize: '1.2rem' }}
              >
                &times;
              </button>
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

                {isChatting && (
                  <div className="message assistant thinking">
                    <strong>VDA Agent:</strong> <span className="typing-dots">Thinking...</span>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
              <div className="input-group">
                <input 
                  value={chatInput}
                  disabled={isChatting}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={isChatting ? "AI is thinking..." : "Search video content..."}
                />
                <button onClick={handleSendMessage} disabled={isChatting || !chatInput}
                >
                  {isChatting ? "..." : "Ask AI"}
                </button>
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