# Environment Manifest

This document outlines the specific hardware, software, and networking configurations required to run the **Intel VDA** local-first AI pipeline. Adherence to these versions is critical for achieving optimal OpenVINO inference speeds and ensuring the MCP microservice communicates cleanly with the orchestrator.

---

### 💻 System Architecture
* **Host OS:** macOS Sequoia (15.x) or Linux/Windows equivalent
* **Architecture:** Darwin arm64 (Apple Silicon M-Series) or Intel x86_64
* **Memory:** 16GB+ System RAM (Unified Memory recommended for VLM inference)
* **Inference Target:** OpenVINO 2026.0 Runtime (CPU/NPU)

---

### 🐍 Python Backend Environment (The Microservices)
We utilize **Miniforge** (conda-forge) on macOS to ensure all binary dependencies are compiled natively for ARM64, avoiding the performance degradation of Rosetta 2.

* **Environment Name:** `intel-VDA-env`
* **Python Version:** `3.10.x`

| Dependency | Version | Purpose |
| :--- | :--- | :--- |
| `openvino` | `2026.0.0` | Primary inference engine for Phi-3, Whisper & SmolVLM2 |
| `nncf` | `2.14.0` | Neural Network Compression Framework (INT4 Quantization) |
| `mcp` | `1.0.x` | Anthropic's Model Context Protocol SDK (FastMCP / SSE routing) |
| `grpcio` | `1.70.0` | High-performance RPC for Rust-to-Python orchestrator communication |
| `librosa` | `0.10.x` | Audio preprocessing for Whisper transcription |
| `moviepy` | `2.0.x` | Frame extraction and video stream handling |

---

### 🦀 Rust & Middleware
The middleware handles the secure IPC (Inter-Process Communication) and SQLite WAL-mode connections.

* **Rust Toolchain:** `1.80.0` or later
* **Tauri Framework:** `v2.0.0` (Plugin-based architecture)
* **Tonic (gRPC):** `0.12.x`
* **System Libs:** `protobuf` (installed via `brew install protobuf`)

---

### ⚛️ Frontend Stack (The "Interface")
* **Framework:** React 19 (TypeScript)
* **Bundler:** Vite 7
* **Tauri API:** `@tauri-apps/api/core`, `@tauri-apps/api/event`
* **Styling:** CSS Modules / Standard CSS

---

### ⚠️ Critical Configuration "Gotchas"

1. **Dual-Port Networking:** The system requires two open local ports. The gRPC Orchestrator binds to `127.0.0.1:50051`. The FastMCP Server binds to `127.0.0.1:8000` via Server-Sent Events (SSE). Ensure no other local development servers are occupying these ports.
2. **ARM64 Native Execution:** Always verify the Python process is running natively by checking Activity Monitor. If the "Kind" says "Intel" instead of "Apple," the gRPC latency and OpenVINO inference speeds will degrade by ~40%.
3. **FFmpeg Dependency:** The host system must have `ffmpeg` installed (e.g., `brew install ffmpeg`) to allow `moviepy` and `librosa` to decode video containers.
4. **Tauri v2 Permissions:** Unlike Tauri v1, all custom IPC commands (e.g., `run_vda_pipeline`) must be explicitly declared in `src-tauri/permissions/vda-commands.toml` and linked in `capabilities/default.json`.

---
