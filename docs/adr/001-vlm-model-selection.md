## ADR-001: VLM Model Selection (SmolVLM2 vs Moondream2)

### Status
Accepted

### Context
The Vision Agent requires a Vision-Language Model (VLM) to describe video frames for the final report. I initially considered **Moondream2**, but encountered significant export issues with the 2026 OpenVINO stack on ARM64 (specifically `rms_norm` layer mismatches).

### Decision
I selected **SmolVLM2 (256M)** as the primary vision model.

### Rationale
* **Native Compatibility:** SmolVLM2 has a cleaner computational graph that exports to OpenVINO IR format without custom layer hacks.
* **Performance:** At 256M parameters, it fits comfortably in the unified memory of Apple Silicon and Intel Integrated graphics, allowing for 10+ frames-per-second analysis.
* **Quantization:** Supports INT4 quantization via `nncf`, reducing the memory footprint to under 200MB.

### Consequences
* **Positive:** Faster inference and more stable environment setup.
* **Neutral:** Requires slightly more prompt engineering to get specific "clinical" descriptions compared to Moondream.
