## ADR-004: Agentic Orchestration and Intent Detection

### Status
Accepted

### Context
The project requirements specify "Human-in-the-loop" (HITL) clarification for ambiguous queries and the ability to route tasks to specific agents. A naive "single-prompt" approach often leads to hallucinations or incorrect tool usage.

### Decision
Implemented a **Semantic Router** pattern in the Python backend using a local **Phi-3-Mini (INT4)** model to perform zero-shot intent classification before taking action.

### Rationale
* **Ambiguity Mitigation:** A lightweight "Intent Check" identifies vague user queries (e.g., "What is that?") and triggers a clarification request before executing expensive RAG retrieval.
* **Deterministic Handoff:** Explicitly routes "Report" intents out of the probabilistic LLM loop and delegates them to an isolated `FastMCP` microservice, ensuring document structural integrity.