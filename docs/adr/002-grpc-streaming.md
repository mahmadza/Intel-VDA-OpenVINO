## ADR-002: Communication via gRPC Streaming

### Status
Accepted

### Context
Video analysis is a long-running process (1–5 minutes). A standard HTTP request-response would time out, and polling for status creates unnecessary CPU overhead.

### Decision
Implemented **gRPC Server-Side Streaming** using `tonic` (Rust) and `grpcio` (Python).

### Rationale
* **Real-Time Feedback:** Allows the Python backend to `yield` progress updates (e.g., "Transcribing... 40%") which are immediately reflected in the React UI.
* **Type Safety:** Protobuf ensures that the data structure passed between Rust and Python is identical, preventing "runtime surprise" errors.
* **Efficiency:** Uses HTTP/2 for a persistent, low-latency connection.