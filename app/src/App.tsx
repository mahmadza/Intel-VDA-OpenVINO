import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import "./App.css";

function App() {
  const [status, setStatus] = useState("Waiting for backend...");

  async function checkConnection() {
    try {
      // This calls the Rust function we just wrote!
      const msg: string = await invoke("ping_backend");
      setStatus(msg);
    } catch (err) {
      setStatus(`Error: ${err}`);
    }
  }

  return (
    <div className="container">
      <h1>Intel VDA - Phase 1</h1>
      <div className="card">
        <button onClick={checkConnection}>Ping Backend</button>
        <p>Status: <strong>{status}</strong></p>
      </div>
    </div>
  );
}

export default App;