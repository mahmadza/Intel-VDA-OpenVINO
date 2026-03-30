use tauri::Emitter;
use tauri_plugin_dialog::DialogExt;
use rusqlite::{params, Connection};
use std::sync::Mutex;
use serde::Serialize;

use crate::vda::video_service_client::VideoServiceClient;
use crate::vda::{VideoRequest, ChatRequest, AnalysisResult};

#[derive(Serialize, Clone)]
pub struct ProgressPayload {
    pub status: String,
    pub percentage: f32,
}

#[derive(Serialize)]
pub struct VideoHistory {
    pub id: i64,
    pub file_name: String,
    pub created_at: String,
}

#[derive(Serialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
}

pub struct DbState(pub Mutex<Connection>);

#[tauri::command]
pub async fn select_video_file(app: tauri::AppHandle) -> Result<String, String> {
    let file_path = app
        .dialog()
        .file()
        .add_filter("Video", &["mp4", "mkv", "avi"])
        .blocking_pick_file();

    match file_path {
        Some(path) => Ok(path.to_string()),
        None => Err("User cancelled the picker".into()),
    }
}

#[tauri::command]
pub async fn run_vda_pipeline(
    window: tauri::Window, 
    db_state: tauri::State<'_, DbState>, 
    path: String
) -> Result<String, String> {
    let mut client: VideoServiceClient<tonic::transport::Channel> = 
        VideoServiceClient::connect("http://127.0.0.1:50051")
            .await
            .map_err(|e| format!("Connection error: {}", e))?;

    let mut stream: tonic::Streaming<crate::vda::ProgressUpdate> = 
        client.process_video(VideoRequest { file_path: path.clone() })
            .await
            .map_err(|e| format!("gRPC error: {}", e))?
            .into_inner();

    while let Some(update) = stream.message().await.map_err(|e| e.to_string())? {
        window.emit("pipeline-progress", ProgressPayload {
            status: update.status.clone(),
            percentage: update.percentage,
        }).map_err(|e| e.to_string())?;

        if let Some(data) = update.final_data {
            save_to_db(&db_state, &path, data)?;
        }
    }

    Ok("Analysis Complete".into())
}

#[tauri::command]
pub async fn send_chat_message(
    db_state: tauri::State<'_, DbState>, // Add DB state access
    video_id: i64,
    message: String,
) -> Result<String, String> {
    // 1. Save User Message to DB
    {
        let conn = db_state.0.lock().unwrap();
        conn.execute(
            "INSERT INTO chat_messages (video_id, role, content) VALUES (?1, 'user', ?2)",
            params![video_id, message],
        ).map_err(|e| e.to_string())?;
    }

    // 2. Call gRPC Backend
    let mut client = VideoServiceClient::connect("http://127.0.0.1:50051")
        .await
        .map_err(|e| format!("Connection error: {}", e))?;

    let response = client.chat(ChatRequest { video_id, message })
        .await
        .map_err(|e| format!("Chat error: {}", e))?;

    let ai_reply = response.into_inner().reply;

    // 3. Save Assistant Message to DB
    {
        let conn = db_state.0.lock().unwrap();
        conn.execute(
            "INSERT INTO chat_messages (video_id, role, content) VALUES (?1, 'assistant', ?2)",
            params![video_id, ai_reply],
        ).map_err(|e| e.to_string())?;
    }

    Ok(ai_reply)
}

#[tauri::command]
pub async fn get_video_history(db_state: tauri::State<'_, DbState>) -> Result<Vec<VideoHistory>, String> {
    let conn = db_state.0.lock().unwrap();
    
    let mut stmt = conn
        .prepare("SELECT id, file_name, created_at FROM videos ORDER BY id DESC")
        .map_err(|e| e.to_string())?;

    let history_iter = stmt.query_map([], |row| {
        Ok(VideoHistory {
            id: row.get(0)?,
            file_name: row.get(1)?,
            created_at: row.get::<_, String>(2).unwrap_or_else(|_| "Unknown".into()),
        })
    }).map_err(|e| e.to_string())?;

    let history: Vec<VideoHistory> = history_iter
        .filter_map(|res| res.ok())
        .collect();

    Ok(history)
}

fn save_to_db(db_state: &DbState, path: &str, data: AnalysisResult) -> Result<(), String> {
    let conn = db_state.0.lock().unwrap();
    
    let file_name = std::path::Path::new(path)
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("unknown_video");

    let video_id: i64 = match conn.query_row(
        "SELECT id FROM videos WHERE file_path = ?1",
        params![path],
        |row| row.get(0),
    ) {
        Ok(id) => id, // Found existing
        Err(_) => {
            // Not found, insert new
            conn.execute(
                "INSERT INTO videos (file_path, file_name) VALUES (?1, ?2)",
                params![path, file_name],
            ).map_err(|e| e.to_string())?;
            conn.last_insert_rowid()
        }
    };

    // Clean up old results for this video (so we don't have duplicates)
    conn.execute("DELETE FROM analysis_results WHERE video_id = ?1", params![video_id])
        .map_err(|e| e.to_string())?;
    conn.execute("DELETE FROM video_segments WHERE video_id = ?1", params![video_id])
        .map_err(|e| e.to_string())?;

    // Insert fresh analysis result
    conn.execute(
        "INSERT INTO analysis_results (video_id, transcription_text, summary, status) VALUES (?1, ?2, ?3, ?4)",
        params![video_id, data.transcription, data.summary, "completed"],
    ).map_err(|e| e.to_string())?;

    // Insert fresh segments
    for seg in data.segments {
        conn.execute(
            "INSERT INTO video_segments (video_id, start_time, end_time, segment_type, content) VALUES (?1, ?2, ?3, ?4, ?5)",
            params![video_id, seg.start_time, seg.end_time, seg.segment_type, seg.content],
        ).map_err(|e| e.to_string())?;
    }

    Ok(())
}

#[tauri::command]
pub async fn delete_video(db_state: tauri::State<'_, DbState>, video_id: i64) -> Result<(), String> {
    let conn = db_state.0.lock().unwrap();
    
    conn.execute("DELETE FROM videos WHERE id = ?1", [video_id])
        .map_err(|e| format!("Failed to delete video: {}", e))?;
        
    Ok(())
}

#[tauri::command]
pub async fn get_chat_history(
    db_state: tauri::State<'_, DbState>, 
    video_id: i64
) -> Result<Vec<ChatMessage>, String> {
    println!("🔍 Rust: Fetching chat for ID: {}", video_id);
    let conn = db_state.0.lock().unwrap();
    let mut stmt = conn
        .prepare("SELECT role, content FROM chat_messages WHERE video_id = ?1 ORDER BY id ASC")
        .map_err(|e| e.to_string())?;

    let history = stmt.query_map([video_id], |row| {
        Ok(ChatMessage {
            role: row.get(0)?,
            content: row.get(1)?,
        })
    }).map_err(|e| e.to_string())?
      .filter_map(|res| res.ok())
      .collect();

    Ok(history)
}