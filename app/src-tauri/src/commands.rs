use tauri_plugin_dialog::DialogExt;

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