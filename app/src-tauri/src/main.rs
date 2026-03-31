mod vda;
mod commands;

use rusqlite::Connection;
use std::sync::Mutex;
use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let data_dir = app.path().app_data_dir().expect("Failed to get data dir");
            
            if !data_dir.exists() {
                std::fs::create_dir_all(&data_dir).map_err(|e| e.to_string())?;
            }

            let db_path = data_dir.join("vda_intelligence.db");
            println!("🦀 Rust DB Path: {:?}", db_path);

            let conn = Connection::open(db_path).map_err(|e| e.to_string())?;
            
            // Enable WAL mode (Write-Ahead Logging) 
            // This is CRITICAL for when both Rust and Python are touching the DB.
            conn.execute("PRAGMA journal_mode=WAL;", []).ok();

            conn.execute_batch("
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL UNIQUE,
                    file_name TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    transcription_text TEXT,
                    summary TEXT,
                    status TEXT,
                    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS video_segments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    start_time REAL,
                    end_time REAL,
                    segment_type TEXT,
                    content TEXT,
                    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    role TEXT NOT NULL, -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
                );
            ").expect("Failed to initialize database schema");

            
            app.manage(commands::DbState(Mutex::new(conn)));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::select_video_file,
            commands::run_vda_pipeline,
            commands::get_video_history,
            commands::send_chat_message,
            commands::delete_video,
            commands::get_chat_history,
            commands::check_engine_status
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}