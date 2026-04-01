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
  * **FFmpeg** (Required for audio extraction. Please install it via `brew install ffmpeg` or `sudo apt install ffmpeg`)

### 2\. Environment Setup

Create a dedicated native environment to ensure OpenVINO links correctly to your local hardware.

```bash
# Clone the repository and navigate to the root directory
conda create -n intel-VDA-env python=3.10 -y
conda activate intel-VDA-env

# Install required ML and backend dependencies
pip install -r backend/requirements.txt
```

### 3\. Bootstrap Local Models

Run the automated downloader to fetch the required Hugging Face models. *(Note: Whisper and SmolVLM2 will undergo a one-time OpenVINO IR conversion during their first inference run).*

```bash
python backend/download_models.py
```

### 4\. Boot the Microservices & App

Because of the decoupled MCP architecture, this application requires **three** terminal windows. To easily capture the cross-platform database path, please start the frontend application first.

**Terminal 1: Start the Tauri Desktop App (Frontend)**
This step initializes the local SQLite database for your specific operating system and prints its absolute path.
```bash
cd app
npm install
npm run tauri dev
```

> ### 🛑 **CRITICAL ACTION REQUIRED**
> Before proceeding to **Terminal 3**, look at the output of **Terminal 1**.
> 
> **Copy the absolute path** printed next to the message `🦀 Rust DB Path:`
> 
> *Example:* `/Users/name/Library/Application Support/com.intel.vda/vda_intelligence.db`
>
> You will need to paste this path when starting the **AI Orchestrator** to bridge the Frontend and Backend intelligence.


**Terminal 2: Start the MCP Server (Generation Tools)**
Leave Terminal 1 running, open a new terminal tab, and start the isolated MCP tool server.
```bash
conda activate intel-VDA-env
cd backend
python agents/generation_mcp_server.py
# Expected: "🚀 Starting Intel VDA Generation MCP Server on port 8000 (SSE)..."
```

**Terminal 3: Start the AI Orchestrator (gRPC Backend)**
Open a final terminal tab to start the primary AI engine, passing in the database path you copied from Terminal 1.
```bash
conda activate intel-VDA-env
cd backend

# Paste the path you copied from Terminal 1:
python server.py --db_path "/paste/the/rust/db/path/here/vda_intelligence.db"
# Expected: "🚀 gRPC Server running on 127.0.0.1:50051"
```
*(💡 Note: When the process in Terminal 3 finished after about 5 minutes, the frontend UI will automatically detect the AI Engine and switch its status indicator to "Ready" Green.)*


Alternatively, you could also use C# to launch the AI Orchestrator.
Compile the launcher for your specific architecture:
```bash
# Navigate to the launcher directory
cd launcher

# Initialize the project
dotnet new console --force 

# Build the self-contained binary for your OS
# For macOS (Apple Silicon):
dotnet publish -c Release -r osx-arm64 --self-contained

# For Windows:
dotnet publish -c Release -r win-x64 --self-contained
```
The binary will be generated in launcher/bin/Release/net10.0/[ARCH]/publish/launcher.

Finally, use the use the C# Launcher to bootstrap the AI engine with the correct DB path:
```bash
./launcher/bin/Release/net10.0/[ARCH]/publish/launcher "[PATH_FROM_TAURI]"
```
Once you see the Terminal says "🚀 gRPC Server running on 127.0.0.1:50051", that means the backend is ready.

-----

## 🧪 Testing the Capabilities

Once the UI is running, click **"+ New Video"** and select a short `.mp4` file (you can use the sample videos in `samples/` directory). Wait for the OpenVINO progress bar to reach 100%. Then, try these exact queries to test the specific rubric requirements:

1.  **Test RAG & Cross-Modal Synthesis:** *"What objects are shown in the video, and what is being said?"*
2.  **Test MCP Integration:** *"Summarize our discussion so far and generate a PDF."* (Watch Terminal 1 intercept the tool call).
3.  **Test Human-in-the-Loop (HITL):** *"Tell me more about it."* (The router will flag this as ambiguous and ask for clarification).

-----

## 📚 Project Documentation (Start Here for Architecture Review)

To understand the engineering decisions, trade-offs, and architecture of this application, please review the following documents:

1. [Assessment Summary: Challenges & Strategic Pivots](docs/ASSESSMENT_SUMMARY.md) *(Required reading per rubric)*
2. [Environment Manifest: Hardware & Dependency Specs](docs/environment-manifest.md)
3. [Full Architecture & Data Flow](docs/architecture/architecture.md)
4. [Model Registry & OpenVINO Optimization](docs/models-registry.md)
5. [Sidecar Packaging Report (Why we chose Conda)](docs/sidecar-attempt.md)

### Architecture Decision Records (ADRs)
* [ADR-001: VLM Model Selection](docs/adr/001-vlm-model-selection.md)
* [ADR-002: Command Isolation in Tauri](docs/adr/002-command-isolation.md)
* [ADR-003: Data Persistence (SQLite WAL)](docs/adr/003-data-persistence-sqlite-wal.md)
* [ADR-004: Agentic Orchestration & Routing](docs/adr/004-agentic-orchestration-intent-detection.md)
* [ADR-006: Decoupled MCP via SSE](docs/adr/006-mcp-sse-microservice.md)

-----

*Developed for Intel Assessment 2026. MIT License.*
