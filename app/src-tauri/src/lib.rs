pub mod vda {
    tonic::include_proto!("vda"); 
}

use vda::video_service_client::VideoServiceClient;
use vda::Empty;

#[tauri::command]
async fn ping_backend() -> Result<String, String> {
    // 127.0.0.1 is safer for Mac/Windows interop than [::1]
    let mut client = VideoServiceClient::connect("http://127.0.0.1:50051")
        .await
        .map_err(|e| e.to_string())?;

    let request = tonic::Request::new(Empty {});
    let response = client.ping(request).await.map_err(|e| e.to_string())?;

    Ok(response.into_inner().message)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![ping_backend])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}