import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";

export function HistoryView({ onSelectVideo }: { onSelectVideo: (id: number) => void }) {
  const [history, setHistory] = useState<any[]>([]);

  const loadHistory = async () => {
    const data = await invoke<any[]>("get_video_history");
    setHistory(data);
  };

  useEffect(() => { loadHistory(); }, []);

  return (
    <div className="history-sidebar">
      <h3>Recent Analysis</h3>
      {history.map((item) => (
        <div key={item.id} className="history-item" onClick={() => onSelectVideo(item.id)}>
          <p>{item.file_name}</p>
          <small>{new Date(item.created_at).toLocaleDateString()}</small>
        </div>
      ))}
    </div>
  );
}