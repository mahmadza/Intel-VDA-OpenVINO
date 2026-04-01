# Model Registry: Intel VDA

This registry tracks the versions, architectures, and optimization parameters for the models used in the local pipeline. All models are explicitly optimized for the **OpenVINO** runtime to ensure maximum performance across Intel and Apple Silicon hardware.

---

## High-Level Summary

| Model ID | Task | Base Architecture | Precision | Size (Optimized) |
| :--- | :--- | :--- | :--- | :--- |
| **Phi-3-Mini-4K-Instruct** | Semantic Routing & RAG | Transformer (LLM) | INT4 | ~2.3 GB |
| **Whisper-Tiny** | Speech-to-Text | Transformer (Encoder-only) | FP16 | ~150 MB |
| **SmolVLM2-256M** | Vision-Language | Transformer (Multimodal) | INT4 | ~190 MB |

---

## 1. Orchestration Agent: Phi-3-Mini-4K

The Orchestration Agent acts as the "brain" of the application. It evaluates user inputs for zero-shot intent classification (Semantic Routing), manages Human-in-the-Loop (HITL) ambiguity prompts, and synthesizes final answers from the SQLite RAG context.

* **Model Source:** Microsoft / OpenVINO (`OpenVINO/phi-3-mini-4k-instruct-int4-ov`)
* **Optimization Strategy:** Pre-quantized to 4-bit integer precision by the OpenVINO team.
* **Precision:** **INT4**. 
* **Reasoning for Choice:** Phi-3 punches massively above its weight class. At INT4, it fits comfortably in consumer RAM while maintaining the strict instruction-following capabilities required to accurately route intents (e.g., `GENERATE_PDF` vs `RAG_QUERY`) without falling into infinite hallucination loops.

---

## 2. Audio Agent: Whisper-Tiny

The Audio Agent is responsible for transcribing video dialogue into structured text prior to LLM evaluation.

* **Model Source:** OpenAI / HuggingFace (`openai/whisper-tiny`)
* **Optimization Strategy:** Exported dynamically to OpenVINO Intermediate Representation (IR) via `optimum-intel` on first launch.
* **Precision:** **FP16**. I chose FP16 over INT8 to maintain high word error rate (WER) performance on technical terminology while still keeping the memory footprint nearly invisible.

---

## 3. Vision Agent: SmolVLM2-256M

The Vision Agent analyzes sampled video keyframes to provide descriptive context (e.g., "A cat sitting in a futuristic laboratory") to the SQLite database.

* **Model Source:** HuggingFace (`HuggingFaceTB/SmolVLM2-256M-Instruct`)
* **Optimization Strategy:** Exported to OpenVINO IR. 
* **Precision:** **INT4** (via NNCF Weight Compression).
* **Reasoning for Choice:** Replaced Moondream2 due to superior native OpenVINO graph compatibility and drastically lower latency. By quantizing the vision encoder and LLM head to INT4, it prevents memory swap thrashing when running concurrently with the Whisper and Phi-3 models.

---

## Hardware Mapping & Execution

| Model | Primary Compute Device | Rationale |
| :--- | :--- | :--- |
| **Phi-3-Mini** | CPU / GPU | High memory bandwidth requirement; benefits from unified memory access for fast token generation. |
| **Whisper** | NPU / CPU | Parallelizable transformer blocks; highly efficient on low-power neural engines. |
| **SmolVLM2** | CPU | Small enough to run entirely in L3 cache on modern processors, freeing up the GPU/NPU for the LLM router. |

---

## Reproduction & Export Commands

To manually re-export or quantize these models for the registry outside of the automated `download_models.py` script, use the following CLI commands within the `vda_native` conda environment:

```bash
# Export Whisper to OpenVINO (FP16)
optimum-cli export openvino --model openai/whisper-tiny whisper_ov_model/

# Export and Quantize SmolVLM2 (INT4)
optimum-cli export openvino --model HuggingFaceTB/SmolVLM2-256M-Instruct --weight-format int4 smol_ov_model/

# Download pre-quantized Phi-3 OpenVINO IR
huggingface-cli download OpenVINO/phi-3-mini-4k-instruct-int4-ov --local-dir phi3_ov_model/