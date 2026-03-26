pub mod vda {
    tonic::include_proto!("vda"); 
}
pub mod commands;


#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        // ... setup code ...
        .invoke_handler(tauri::generate_handler![
            commands::select_video_file,
            commands::run_vda_pipeline,
            commands::get_video_history,
            commands::send_chat_message
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}