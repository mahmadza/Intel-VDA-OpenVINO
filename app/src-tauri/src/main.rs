mod vda;
mod commands;

use rusqlite::Connection;
use std::sync::Mutex;
use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let data_dir = app.path().app_data_dir().expect("Failed to get data dir");
            println!("📂 App Data Directory: {:?}", data_dir);
            std::fs::create_dir_all(&data_dir).unwrap();
            let db_path = data_dir.join("vda_intelligence.db");
            println!("🦀 Rust DB Path: {:?}", db_path);
            let conn = Connection::open(db_path).map_err(|e| e.to_string())?;
            
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
            ").expect("Failed to initialize database schema");

            app.manage(commands::DbState(Mutex::new(conn)));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::select_video_file,
            commands::run_vda_pipeline,
            commands::get_video_history,
            commands::send_chat_message
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}