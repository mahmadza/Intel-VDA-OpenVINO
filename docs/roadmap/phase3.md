## Phase 3 Roadmap & Backlog

### **1. Core Objectives**
The goal of Phase 3 is to move from a **Transient Pipeline** (where data disappears when the app closes) to a **Persistent Application** (where data is stored, searchable, and exportable).

---

### **2. The Backlog (Priority Order)**

| Feature | Description | Tech Involved |
| :--- | :--- | :--- |
| **SQLite Integration** | Save video metadata, transcription, and VLM descriptions to a local database. | `rusqlite` (Rust) |
| **Result History UI** | A "Dashboard" or sidebar to browse previous video analyses. | React / CSS |
| **The VDA Chatbot** | A RAG-based chat interface to ask questions about the video content. | Python / OpenVINO / LangChain |
| **Human-in-the-Loop** | Allow users to edit the AI-generated descriptions before report generation. | React Forms |
| **Report Export v2** | Polished PDF/PPTX generation with custom branding and charts. | Python (ReportLab / python-pptx) |

---

### **3. Immediate Next Steps (Day 1 after break)**
1.  **Database Schema:** Define the SQLite tables for `videos`, `transcripts`, and `vision_tags`.
2.  **Rust Persistence:** Update the `run_vda_pipeline` command in `commands.rs` to insert the final results into SQLite.
3.  **UI Refactor:** Create a "Results View" component in React to display the data we just processed in Phase 2.

---

### **4. Technical Debt / Cleanup**
* [ ] **Error Handling:** Add a "Retry" button if the gRPC connection fails.
* [ ] **Styling:** Move from inline styles in `App.tsx` to a dedicated CSS module or Tailwind.
* [ ] **Model Loading:** Implement a "Warm-up" state so the UI shows "Loading Models into NPU..." instead of just hanging for 3 seconds.

---

## Final Handover Message
> **Current Status:** The "Vertical Slice" is complete. React talks to Rust, Rust streams from Python, and Python runs OpenVINO agents. The progress bar moves, and the terminal prints the analysis.
>
> **Last Test:** Verified on macOS ARM64 with `sample.mp4`. Output was successful.
