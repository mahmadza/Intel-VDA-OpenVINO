use tauri::Emitter; // For sending events to React
use tauri_plugin_dialog::DialogExt;
use crate::vda::video_service_client::VideoServiceClient;
use crate::vda::VideoRequest;

#[derive(serde::Serialize, Clone)]
pub struct ProgressPayload {
    pub status: String,
    pub percentage: f32,
}

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
pub async fn run_vda_pipeline(window: tauri::Window, path: String) -> Result<String, String> {
    // 1. Connect to Python
    let mut client = VideoServiceClient::connect("http://127.0.0.1:50051")
        .await
        .map_err(|e| format!("Connection failed: {}", e))?;

    let request = tonic::Request::new(VideoRequest { file_path: path });

    // 2. Call the streaming RPC
    let mut stream = client.process_video(request)
        .await
        .map_err(|e: tonic::Status| format!("gRPC Error: {}", e))?
        .into_inner();

    // 3. Listen to Python and Emit to React
    while let Some(update) = stream.message().await.map_err(|e: tonic::Status| e.to_string())? {
        window.emit("pipeline-progress", ProgressPayload {
            status: update.status,
            percentage: update.percentage,
        }).map_err(|e| e.to_string())?;
    }

    Ok("Analysis Complete".into())
}