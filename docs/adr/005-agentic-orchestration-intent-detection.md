
## ADR-005: Agentic Orchestration and Intent Detection

### Status
Accepted

### Context
The project requirements specify "Human-in-the-loop" (HITL) clarification for ambiguous queries and the ability to route tasks to specific agents (Transcription, Vision, Generation). A naive "single-prompt" approach often leads to hallucinations or incorrect tool usage.

### Decision
Implemented a **Gatekeeper/Orchestrator** pattern in the Python backend using a two-stage LLM reasoning loop.

### Rationale
* **Ambiguity Mitigation:** A lightweight "Intent Check" stage identifies vague user queries (e.g., "What is that?") and triggers a clarification request before executing expensive vision/audio inference.
* **Multi-Agent Routing:** Explicitly routes "Report" intents to a deterministic `GenerationAgent` (PDF/PPTX) rather than relying on the LLM to generate file content, ensuring document structural integrity.
* **Extensibility:** This modular design allows for the independent scaling of agents; for instance, the Vision Agent can be upgraded without modifying the Transcription or Orchestration logic.
