import os
import concurrent.futures
from huggingface_hub import snapshot_download

MODELS = {
    "whisper": "openai/whisper-tiny",
    "vision": "HuggingFaceTB/SmolVLM2-256M-Instruct",
    "llm": "OpenVINO/phi-3-mini-4k-instruct-int4-ov"
}

def download_single_model(name, repo_id, base_path):
    print(f"📡 [START] {name} download initiated...")
    target_dir = os.path.join(base_path, name)
    
    try:
        snapshot_download(
            repo_id=repo_id, 
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            # This allows the library to parallelize individual file downloads within the repo
            max_workers=8 
        )
        print(f"✅ [DONE] {name} is ready in {target_dir}")
        return f"{name}: Success"
    except Exception as e:
        print(f"❌ [ERROR] {name} failed: {e}")
        return f"{name}: Failed"

def download_all_parallel():
    base_path = os.path.join(os.path.dirname(__file__), "models")
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    print("🚀 Intel VDA: Parallel Model Bootstrap Starting...")
    print(f"📦 Target Directory: {base_path}\n" + "-"*40)

    # Use ThreadPoolExecutor to run downloads in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(MODELS)) as executor:
        # Create a dictionary to track the futures
        future_to_model = {
            executor.submit(download_single_model, name, repo_id, base_path): name 
            for name, repo_id in MODELS.items()
        }
        
        for future in concurrent.futures.as_completed(future_to_model):
            result = future.result()
            # Logging handled inside the function for real-time feedback

    print("\n" + "-"*40)
    print("🎉 All parallel downloads completed.")
    print("💡 Note: Whisper and Vision models will undergo a one-time OpenVINO conversion on first launch.")

if __name__ == "__main__":
    download_all_parallel()