# Intel-VDA-OpenVINO

### Local-First Video Data Analytics (VDA) Orchestrator

**Intel-VDA-OpenVINO** is a high-performance, privacy-centric desktop application designed to transform raw video data into structured intelligence. It uses **Intel OpenVINO** to perform all inference (Audio & Vision) locally on the edge, ensuring zero data leakage and sub-second latency.

-----

## Key Features

  * **Privacy-by-Design:** No video frames or transcripts ever leave your local machine.
  * **Multi-Modal Pipeline:** Integrated **Whisper** (Audio) and **SmolVLM2** (Vision) agents.
  * **Hardware Optimized:** Native support for Apple Silicon (M-Series) and Intel NPUs via the OpenVINO toolkit.
  * **Real-Time Streaming:** gRPC-based communication provides a smooth, reactive UI experience during heavy AI tasks.

-----

## The Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 19, Vite 7, TypeScript |
| **Desktop Shell** | Tauri v2 (Rust) |
| **Inference Engine** | OpenVINO Runtime (Python 3.10) |
| **Communication** | gRPC (Tonic/Protobuf) |
| **Models** | Whisper-base, SmolVLM2-256M |

-----

## Architecture Overview

The system utilizes a **Triad Architecture** to decouple the heavy computation backend from the lightweight interface.

1.  **The Interface, React:** A modern UI for file management and report editing.
2.  **The Bridge, Rust:** A secure middleware layer managing OS permissions and gRPC client-side streaming.
3.  **The Engine, Python:** An OpenVINO-optimized orchestrator that handles multi-modal AI tasks.

> **Deep Dive:** See [Architecture Documentation](docs/architecture/architecture.md) for data flow diagrams.

-----

## Project Status

  * **Phase 1: Foundation** ✅
      * gRPC Bridge & Protobuf contract established.
      * Basic Rust-to-Python "Ping" connectivity.
  * **Phase 2: Orchestration** ✅
      * OpenVINO integration for Whisper & SmolVLM2.
      * Real-time progress streaming to UI.
      * Native OS File Picker integration.
  * **Phase 3: Persistence & Interface** 🚧
      * SQLite integration for historical analysis.
      * RAG-based Chat interface for video querying.
      * Export engine (PDF/PPTX).

-----

## Quick Start (Development)

### ADD INSTALLING THE CONDA ENV HERE

### 1\. Start the AI Engine (Python)

```bash
conda activate vda_native
python server.py
```

### 2\. Launch the Desktop App (Tauri)

```bash
npm run tauri dev
```

-----

## Engineering Standards

This project maintains high transparency through **Architecture Decision Records (ADRs)**.

  * [ADR-001: Model Selection (SmolVLM2 vs Moondream2)](docs/adr/001-vlm-selection.md)
  * [ADR-002: gRPC Streaming Implementation](docs/adr/002-grpc-streaming.md)
  * [ADR-003: Tauri v2 Command Isolation](docs/adr/003-command-isolation.md)

-----

## License

MIT - See [LICENSE](LICENSE.md) for details.
