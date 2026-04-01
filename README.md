# 🚀 Intel VDA: Local Video Intelligence Orchestrator

**Intel VDA** is a high-performance, privacy-centric desktop application that transforms raw video data into queryable structured intelligence. 

Built for the **Intel GenAI Software Solutions** assessment, it demonstrates a robust multi-agent architecture optimized for local hardware via **OpenVINO**, featuring a dedicated **Model Context Protocol (MCP)** server for artifact generation and an intelligent semantic routing engine.

---

## ✨ Key Capabilities (Assessment Alignment)

* **100% Offline & Local Inference:** Privacy-first architecture. No data ever leaves the device. Models are INT4 quantized via NNCF to run efficiently on consumer CPUs/NPUs.
* **Agentic Routing (Phi-3):** A semantic router dynamically classifies user intents (e.g., Query, Generate PDF, Generate PPT, or Clarify) before taking action.
* **Self-Developed MCP Server:** Report generation is completely decoupled into a standalone `FastMCP` microservice communicating via Server-Sent Events (SSE).
* **Human-in-the-Loop (HITL):** Active ambiguity detection that pauses execution and asks the user for clarification on vague queries (e.g., *"What is that?"*).
* **Persistent Memory (WAL):** SQLite-backed history configured with Write-Ahead Logging to safely handle concurrent reads (Rust UI) and writes (Python AI).

---

## 🏗️ The Three-Tier Architecture

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite, Tauri v2 (Rust) | Lightweight, stateless hydration UI with persistent SQLite views. |
| **AI Orchestrator** | Python 3.10, gRPC, OpenVINO | The primary backend. Handles video processing, Whisper/SmolVLM inference, and Phi-3 semantic routing. |
| **MCP Tool Server** | Python 3.10, `mcp` SDK (FastMCP) | An isolated microservice (Port 8000) dedicated to deterministic PDF and PPTX report generation. |

```mermaid
graph TD
    subgraph Client [Tauri Desktop App]
        UI[React UI] <-->|IPC| RustBridge[Rust Core]
        RustBridge <--> DB[(SQLite)]
    end

    subgraph Backend [gRPC AI Orchestrator]
        RustBridge <==>|gRPC / Port 50051| Server[Python Server]
        Server <--> Router[Phi-3 Semantic Router]
        Router -->|Audio| Whisper[Whisper Agent]
        Router -->|Vision| VLM[SmolVLM2 Agent]
    end

    subgraph MCP [Generation Microservice]
        Router -.->|SSE / Port 8000| MCPServer[FastMCP Server]
        MCPServer --> PDF[PDF Generator]
        MCPServer --> PPT[PPTX Generator]
    end
````

-----

## 🚀 Quick Start Runbook (Reviewer Guide)

### 1\. Prerequisites

  * **macOS (Apple Silicon)** or Linux/Windows equivalent.
  * **Conda** (Miniconda or Anaconda)
  * **Node.js** (v18+)
  * **Rust** (Latest stable)
  * **FFmpeg** (Required for audio extraction: `brew install ffmpeg`)

### 2\. Environment Setup

Create a dedicated native environment to ensure OpenVINO links correctly to your local hardware.

```bash
# Clone the repository and navigate to the root directory
conda create -n vda_native python=3.10 -y
conda activate vda_native

# Install required ML and backend dependencies
pip install -r backend/requirements.txt
```

### 3\. Bootstrap Local Models

Run the automated downloader to fetch the required Hugging Face models. *(Note: Whisper and SmolVLM2 will undergo a one-time OpenVINO IR conversion during their first inference run).*

```bash
python backend/download_models.py
```

### 4\. Boot the Microservices

Because of the decoupled MCP architecture, this application requires **three** terminal windows.

**Terminal 1: Start the MCP Server (Generation Tools)**

```bash
conda activate vda_native
cd backend
python agents/generation_mcp_server.py
# Expected: "🚀 Starting Intel VDA Generation MCP Server on port 8000 (SSE)..."
```

**Terminal 2: Start the AI Orchestrator (gRPC Backend)**

```bash
conda activate vda_native
cd backend
# Note: Ensure the absolute path is provided for the SQLite DB
python server.py --db_path "$HOME/Library/Application Support/com.intel.vda/vda_intelligence.db"
# Expected: "🚀 gRPC Server running on 127.0.0.1:50051"
```

**Terminal 3: Start the Tauri Desktop App**

```bash
cd app
npm install
npm run tauri dev
```

-----

## 🧪 Testing the Capabilities

Once the UI is running, click **"+ New Video"** and select a short `.mp4` file. Wait for the OpenVINO progress bar to reach 100%. Then, try these exact queries to test the specific rubric requirements:

1.  **Test RAG & Cross-Modal Synthesis:** *"What objects are shown in the video, and what is being said?"*
2.  **Test MCP Integration:** *"Summarize our discussion so far and generate a PDF."* (Watch Terminal 1 intercept the tool call).
3.  **Test Human-in-the-Loop (HITL):** *"Tell me more about it."* (The router will flag this as ambiguous and ask for clarification).
4.  **Test Negative Constraints:** *"Who is the CEO of Intel?"* (The AI will refuse to hallucinate outside the video context).

-----

## 📚 Project Documentation

  * [Assessment Summary: Challenges, Constraints & Future Improvements](docs/ASSESSMENT_SUMMARY.md)
  * [Full Architecture & Data Flow](docs/architecture/architecture.md)
  * [Model Registry & OpenVINO Optimization](docs/models/models-registry.md)

-----

*Developed for Intel Assessment 2026. MIT License.*
