// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

pub mod vda {
    tonic::include_proto!("vda"); 
}

use vda::video_service_client::VideoServiceClient;
use vda::Empty;

#[tauri::command]
async fn ping_backend() -> Result<String, String> {
    // Note: Use 127.0.0.1 instead of [::1] for better cross-platform compatibility
    let mut client = VideoServiceClient::connect("http://127.0.0.1:50051")
        .await
        .map_err(|e| e.to_string())?;

    let request = tonic::Request::new(Empty {});
    let response = client.ping(request).await.map_err(|e| e.to_string())?;

    Ok(response.into_inner().message)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init()) // REQUIRED for Tauri v2
        .invoke_handler(tauri::generate_handler![ping_backend])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}