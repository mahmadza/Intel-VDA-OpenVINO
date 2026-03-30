## ADR-004: Data Persistence Strategy (SQLite with WAL Mode)

### Status
Accepted

### Context
The application must persist video metadata, transcription results, visual segments, and chat history across sessions. Because the architecture involves a Rust frontend and a Python backend potentially accessing the database simultaneously, we required a solution that handles local concurrency without the overhead of a server-based DB.

### Decision
Implemented **SQLite** as the primary datastore, explicitly configured with **Write-Ahead Logging (WAL) mode**.

### Rationale
* **Concurrency:** WAL mode allows multiple readers (Rust UI) and one writer (Python AI Backend) to operate simultaneously, preventing "Database is locked" errors during intensive AI processing.
* **Relational Integrity:** Using a relational schema with `ON DELETE CASCADE` ensures that deleting a video record automatically purges all associated analysis and chat data, maintaining database hygiene.
* **Zero-Config Deployment:** SQLite is a single-file database, making it ideal for a local-first desktop application that must run offline without external dependencies.
