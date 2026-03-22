# Environment Manifest

This document outlines the specific hardware and software configurations required to run the **Intel VDA** local-first AI pipeline. Due to the high-performance requirements of OpenVINO inference on Apple Silicon, adherence to these versions is critical.

---

### 💻 System Architecture
* **Host OS:** macOS Sequoia (15.x) or later
* **Architecture:** Darwin arm64 (Apple Silicon M-Series)
* **Memory:** 16GB+ Unified Memory (Recommended for VLM inference)
* **Inference Target:** OpenVINO 2026.0 Runtime (CPU/NPU)

---

### Python Backend Environment
We utilize **Miniforge** (conda-forge) to ensure all binary dependencies are compiled natively for ARM64, avoiding the performance degradation of Rosetta 2.

* **Environment Name:** `vda_native`
* **Python Version:** `3.10.x`

| Dependency | Version | Purpose |
| :--- | :--- | :--- |
| `openvino` | `2026.0.0` | Primary inference engine for Whisper & SmolVLM2 |
| `nncf` | `2.14.0` | Neural Network Compression Framework (INT4 Quantization) |
| `grpcio` | `1.70.0` | High-performance RPC for Rust-to-Python communication |
| `librosa` | `0.10.x` | Audio preprocessing for Whisper transcription |
| `moviepy` | `2.0.x` | Frame extraction and video stream handling |

---

### Rust & Middleware
The middleware handles the secure IPC (Inter-Process Communication) and gRPC client logic.

* **Rust Toolchain:** `1.80.0` or later
* **Tauri Framework:** `v2.0.0` (Plugin-based architecture)
* **Tonic (gRPC):** `0.12.x`
* **System Libs:** `protobuf` (installed via `brew install protobuf`)

---

### Frontend Stack (The "Interface")
* **Framework:** React 19 (TypeScript)
* **Bundler:** Vite 7
* **Tauri API:** `@tauri-apps/api/core`, `@tauri-apps/api/event`
* **Styling:** CSS Modules / Standard CSS

---

### ⚠️ Critical Configuration "Gotchas"

1.  **ARM64 Native Execution:** Always verify the Python process is running natively by checking Activity Monitor. If the "Kind" says "Intel" instead of "Apple," the gRPC latency and inference speed will be degraded by ~40%.
2.  **FFmpeg Dependency:** The system must have `ffmpeg` installed (`brew install ffmpeg`) to allow `moviepy` and `librosa` to decode video containers.
3.  **Tauri v2 Permissions:** Unlike Tauri v1, all custom commands (e.g., `run_vda_pipeline`) must be explicitly declared in `src-tauri/permissions/vda-commands.toml` and linked in `capabilities/default.json`.
4.  **Protoc Path:** If `cargo build` fails on the proto step, ensure `protoc` is in your `$PATH`.

---

### Environment Setup Command
```bash
# Create native environment
conda create -n vda_native python=3.10
conda activate vda_native

# Install OpenVINO stack
pip install openvino nncf grpcio grpcio-tools librosa moviepy torch
```
