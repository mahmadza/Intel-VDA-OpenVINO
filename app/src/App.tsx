import { useState } from "react";
import { invoke } from "@tauri-apps/api/core"; // Tauri v2 standard
import "./App.css";

function App() {
  const [status, setStatus] = useState("Ready");
  const [videoPath, setVideoPath] = useState("");

  // Existing Ping function
  async function pingBackend() {
    try {
      const response: string = await invoke("ping_backend");
      setStatus(`Status: ${response}`);
    } catch (err) {
      setStatus(`Error: ${err}`);
    }
  }

  // New File Picker function
  async function handleSelectVideo() {
    try {
      setStatus("Opening file picker...");
      const path: string = await invoke("select_video_file");
      setVideoPath(path);
      setStatus("Video Selected");
    } catch (err) {
      // This catches the "User cancelled" error from Rust
      setStatus(`Picker: ${err}`);
    }
  }

  return (
    <main className="container">
      <h1>Intel VDA (Local AI)</h1>

      <div className="row">
        <button onClick={pingBackend}>Ping AI Engine</button>
        <button onClick={handleSelectVideo}>Select Video File</button>
      </div>

      <div className="status-box">
        <p><strong>System Status:</strong> {status}</p>
        {videoPath && (
          <p className="path-text">
            <strong>Selected File:</strong> {videoPath}
          </p>
        )}
      </div>
    </main>
  );
}

export default App;