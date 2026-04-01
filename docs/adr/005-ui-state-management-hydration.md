## ADR-005: UI State Management and Hydration

### Status
Accepted

### Context
React state is volatile and cleared on application restart or component unmounting. To provide a seamless user experience, the chat window and sidebar must reflect the current state of the database immediately upon selecting a video.

### Decision
Adopted a **Database-Driven Hydration** strategy where the UI remains stateless regarding historical data, re-fetching context from the DB on every "Active Video" change.

### Rationale
* **Single Source of Truth:** By treating SQLite as the absolute state, we avoid synchronization bugs between the React memory and the physical disk.
* **Memory Efficiency:** The frontend does not need to store the entire application history in RAM; it only "hydrates" the messages relevant to the currently selected video.
* **Persistence:** Ensures that user-agent interactions are "remembered" even if the application process is killed and restarted, satisfying the persistent chat history requirement.
