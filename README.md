# Intel VDA: Local Video Intelligence Orchestrator

**Intel VDA** is a high-performance, privacy-centric desktop application that transforms raw video data into queryable structured intelligence. Built for the **Intel GenAI Software Solutions** assessment, it demonstrates a robust multi-agent architecture optimized for local hardware via **OpenVINO**.

-----

## 🚀 Key Features

* **100% Offline AI:** Privacy-first architecture. No data ever leaves the device.
* **Agentic Intelligence:** Multi-agent routing for Transcription, Vision, and Report Generation.
* **Human-in-the-Loop:** Active ambiguity detection that asks for clarification on vague queries.
* **Persistent Memory:** SQLite-backed history for video analysis and chat conversations.
* **Hardware Optimized:** Leverages $INT4$ quantization for LLMs and VLMs to run on consumer-grade CPUs and NPUs.

-----

## 🛠️ The Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 19, Vite 7, TypeScript |
| **Middleware** | Tauri v2 (Rust), gRPC (Tonic), SQLite |
| **AI Engine** | OpenVINO Runtime (Python 3.10) |
| **Models** | Whisper-tiny, SmolVLM2-256M, Phi-3-Mini ($INT4$) |

-----

## 📈 Project Status

* **Phase 1: Foundation** ✅
    * gRPC Bridge & Protobuf contract.
* **Phase 2: Orchestration** ✅
    * OpenVINO integration for Whisper & SmolVLM2.
    * Real-time progress streaming.
* **Phase 3: Persistence & Interface** ✅
    * SQLite persistence for history and chat.
    * Agentic HITL (Human-in-the-loop) ambiguity detection.
    * Report Generation Engine (PDF/PPTX).

-----

## 📦 Installation & Setup

### 1. Prerequisites
* **Conda** (Miniconda or Anaconda)
* **Node.js** (v18+)
* **Rust** (Latest stable)

### 2. AI Engine Setup (Python)
```bash
# Create and activate environment
conda create -n vda_native python=3.10 -y
conda activate vda_native

# Install dependencies
pip install -r backend/requirements.txt
````

### 3\. Launching the Application

1.  **Start Backend:** `python backend/server.py --db_path "/path/to/your/db"`
2.  **Start Frontend:** `npm run tauri dev`

-----

## 📚 Architecture & ADRs

  * [Full Architecture Overview](https://www.google.com/search?q=docs/architecture/architecture.md)
  * [Data Flow Deep-Dive](https://www.google.com/search?q=docs/architecture/data-flow.md)
  * [ADR-004: SQLite WAL Persistence](https://www.google.com/search?q=docs/adr/004-data-persistence-sqlite-wal.md)
  * [ADR-005: Agentic HITL Orchestration](https://www.google.com/search?q=docs/adr/005-agentic-orchestration-intent-detection.md)

-----

## License

MIT - Developed for Intel Assessment 2026.

-----