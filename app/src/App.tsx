import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

function App() {
  const [status, setStatus] = useState("Ready");
  const [progress, setProgress] = useState(0);
  const [videoPath, setVideoPath] = useState("");

  useEffect(() => {
    // Setup listener for progress events
    const unlisten = listen("pipeline-progress", (event: any) => {
      setStatus(event.payload.status);
      setProgress(event.payload.percentage);
    });

    return () => {
      unlisten.then((f) => f());
    };
  }, []);

  const handleProcess = async () => {
    try {
      // 1. Get the file path first
      const path = await invoke<string>("select_video_file");
      setVideoPath(path);
      
      // 2. Start the AI pipeline
      setStatus("Starting analysis...");
      await invoke("run_vda_pipeline", { path });
      
    } catch (err) {
      setStatus(`Error: ${err}`);
    }
  };

  return (
    <div className="container">
      <h1>Intel VDA</h1>
      <button onClick={handleProcess}>Select & Process Video</button>
      
      <div className="status-area">
        <p><strong>Status:</strong> {status}</p>
        <div className="progress-bg">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
        {videoPath && <small>File: {videoPath}</small>}
      </div>
    </div>
  );
}

export default App;