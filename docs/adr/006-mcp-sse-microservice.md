## ADR-006: Decoupled MCP Architecture via Server-Sent Events (SSE)

### Status
Accepted

### Context
The assessment requires the use of self-developed Model Context Protocol (MCP) servers. During initial development, the MCP client was configured to use standard input/output (`stdio`), which requires the host process to spawn a subprocess via `fork()`. Because the primary AI Orchestrator runs inside a highly concurrent gRPC `ThreadPoolExecutor`, executing a `fork()` call on macOS resulted in immediate POSIX deadlocks and thread panics.

### Decision
Isolated the artifact generation tools (PDF/PPTX) into a standalone **FastMCP microservice** that communicates with the main Orchestrator via **HTTP Server-Sent Events (SSE)** on Port 8000.

### Rationale
* **Thread Safety:** Bypasses the macOS multithreading `fork()` restriction entirely by relying on standard network protocols instead of process pipes.
* **Memory Isolation:** The generation libraries (`python-pptx`, `reportlab`) and their operations are kept entirely out of the primary AI Orchestrator's memory space, preventing memory fragmentation during heavy OpenVINO inference.
* **True Microservice Architecture:** Demonstrates a scalable pattern where additional MCP tool servers (e.g., a Web Search MCP or Database Query MCP) can be spun up on different ports without touching the core gRPC routing logic.

### Consequences
* **Positive:** Complete elimination of threading deadlocks and a highly modular architecture.
* **Neutral:** Requires the end-user/reviewer to instantiate two separate Python processes (gRPC on 50051, MCP on 8000) to run the full application suite.