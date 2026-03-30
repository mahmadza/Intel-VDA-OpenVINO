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

  const handleSelectVideo = async (id: number) => {
    console.log("--- 🖱️ UI START: handleSelectVideo ---");

    setActiveVideoId(id);
    setMessages([]); 

    try {
      const chatHistory = await invoke<any[]>("get_chat_history", { videoId: id });
      console.log("--- 📦 DATABASE RETURNED ---", chatHistory);
      
      if (chatHistory) {
        setMessages(chatHistory);
      }
    } catch (err) {
      console.error("--- ❌ INVOKE FAILED ---", err);
      alert("Invoke Error: " + err);
    }
  };

  const handleProcess = async () => {
    try {
      const path = await invoke<string>("select_video_file");
      
      // 1. CLEAR the active video to force the UI back to the "Welcome/Loading" screen
      setActiveVideoId(null);
      setMessages([]);
      
      // 2. Reset progress and status
      setStatus("Starting analysis...");
      setProgress(0); 
      
      // 3. Run the pipeline (this will emit 'pipeline-progress' events)
      await invoke("run_vda_pipeline", { path });
      
      setStatus("Analysis Complete");
      const updatedHistory = await loadHistory();
      
      // 4. Once finished, automatically jump to the new video
      if (updatedHistory && updatedHistory.length > 0) {
        handleSelectVideo(updatedHistory[0].id);
      }
      
    } catch (err) {
      setStatus(`Error: ${err}`);
      console.error(err);
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
              onClick={() => handleSelectVideo(v.id)} // <--- MUST BE EXACTLY THIS
              style={{ cursor: 'pointer', border: '1px solid #ccc', margin: '5px', padding: '10px' }}
            >
              <span>{v.file_name}</span>
              <button onClick={(e) => handleDeleteVideo(v.id, e)}>×</button>
            </div>
          ))}
        </div>
      </aside>

      <main className="main-content">
        {(progress > 0 && progress < 100) && (
          <div className="global-progress">
            <p><strong>{status}</strong></p>
            <progress value={progress} max={100} style={{ width: '100%', height: '10px' }} />
            <span style={{ fontSize: '0.8rem', color: '#666' }}>{Math.round(progress)}% Complete</span>
          </div>
        )}
        {activeVideoId ? (
          <div className="intelligence-view">
            <div className="chat-container">
              <div className="messages-log">
                {messages.map((m, i) => (
                  <div key={i} className={`message ${m.role}`}>
                    <strong>{m.role === 'user' ? 'You' : 'Intel AI Analyst'}:</strong> {m.content}
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
            <h2>{progress > 0 && progress < 100 ? "" : "Select a video to begin"}</h2>
            {status === "Ready" && <p>Upload an .mp4 to start local analysis.</p>}
          </div>
        )}
      </main>
    </div>

    
  );
}

export default App;