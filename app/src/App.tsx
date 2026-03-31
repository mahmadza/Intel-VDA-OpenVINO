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
    loadHistory();

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

  useEffect(() => {
    const checkHealth = async () => {
      // Only poll if we aren't currently in the middle of a video analysis
      if (progress > 0 && progress < 100) return;

      try {
        const engineStatus = await invoke<string>("check_engine_status");
        
        if (engineStatus === "READY") {
          setStatus("Ready");
        } else if (engineStatus.startsWith("MODELS_MISSING")) {
          setStatus("Missing Models");
        }
      } catch (err) {
        // If the invoke fails (e.g., Python server isn't running)
        setStatus("Offline");
      }
    };

    // Check every 5 seconds
    const interval = setInterval(checkHealth, 5000);
    checkHealth(); // Run once immediately on mount

    return () => clearInterval(interval);
  }, [progress]); // Re-run if progress changes to ensure we resume polling when done

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
      
      // Clear the active video to force the UI back to the "Welcome/Loading" screen
      setActiveVideoId(null);
      setMessages([]);
      
      // Reset progress and status
      setStatus("Starting analysis...");
      setProgress(0); 
      
      // Run the pipeline (this will emit 'pipeline-progress' events)
      await invoke("run_vda_pipeline", { path });
      
      setStatus("Analysis Complete");
      const updatedHistory = await loadHistory();
      
      // Once finished, automatically jump to the new video
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

    const currentInput = chatInput; // Capture the input before clearing
    setMessages(prev => [...prev, { role: "user", content: currentInput }]);
    setChatInput("");
    
    console.log("⏳ UI: Setting isChatting to TRUE");
    setIsChatting(true);
    
    try {
      const aiReply = await invoke<string>("send_chat_message", { 
        videoId: activeVideoId, 
        message: currentInput 
      });

      if (aiReply.startsWith("SUCCESS_FILE: ")) {
        const filePath = aiReply.replace("SUCCESS_FILE: ", "").trim();
        setMessages(prev => [...prev, { 
          role: "assistant", 
          content: `✅ Report generated successfully!\n\nPath: ${filePath}` 
        }]);
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: aiReply }]);
      }

    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: `System Error: ${err}` }]);
    } finally {
      console.log("✅ UI: Setting isChatting to FALSE");
      setIsChatting(false); // This MUST run regardless of success or error
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
              title={v.file_name}
            >
              <span>{v.file_name}</span>
              <button 
                className="delete-btn" 
                onClick={(e) => handleDeleteVideo(v.id, e)}
              >
                ×
              </button>
            </div>
          ))}
        </div>

        <div className="system-status">
          <div className={`status-dot ${status === "Ready" ? "online" : "busy"}`}></div>
          <span>AI Engine: {status}</span>
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
                    <strong>Intel AI Analyst:</strong> <span className="typing-dots">Thinking...</span>
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
                <button onClick={handleSendMessage} disabled={isChatting || !chatInput}>
                  {isChatting ? "..." : "Ask AI"}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="welcome-screen">
            {progress > 0 && progress < 100 ? (
              <div className="processing-hero">
                <h2>AI is Analyzing Video Intelligence...</h2>
                <p>Please wait while OpenVINO processes the audio and visual streams.</p>
              </div>
            ) : (
              <div className="hero-content">
                <div className="hero-header">
                  <h1>Intel VDA</h1>
                  <p className="subtitle">Local-First Video Data Analytics Orchestrator</p>
                </div>
                
                <div className="feature-grid">
                  <div className="feature-card">
                    <div className="icon">🔒</div>
                    <h3>Privacy First</h3>
                    <p>Frames and transcripts never leave your local OpenVINO runtime.</p>
                  </div>
                  <div className="feature-card">
                    <div className="icon">⚡</div>
                    <h3>INT4 Optimized</h3>
                    <p>Leveraging Intel hardware with quantized INT4 precision for low latency.</p>
                  </div>
                  <div className="feature-card">
                    <div className="icon">📂</div>
                    <h3>Multi-Agent</h3>
                    <p>Integrated Whisper (Audio) and SmolVLM2 (Vision) intelligence.</p>
                  </div>
                </div>

                <div className="getting-started">
                  <h3>Quick Start Guide</h3>
                  <div className="steps">
                    <div className="step">
                      <span className="step-num">1</span>
                      <p>Check the <strong>AI Engine status</strong> in the sidebar (should be Green).</p>
                    </div>
                    <div className="step">
                      <span className="step-num">2</span>
                      <p>Click <strong>+ New Video</strong> to upload and analyze an MP4 file.</p>
                    </div>
                    <div className="step">
                      <span className="step-num">3</span>
                      <p>Ask the <strong>Forensic Analyst</strong> about specific events, objects, or audio content.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>

    
  );
}

export default App;