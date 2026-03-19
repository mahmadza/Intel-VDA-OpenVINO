fn main() {
    tonic_build::configure()
        .compile_protos(
            &["../../proto/vda.proto"], // Path to your proto file
            &["../../proto"],           // Parent folder
        )
        .unwrap();
    tauri_build::build();
}