# Model Registry: Intel VDA

This registry tracks the versions, architectures, and optimization parameters for the models used in the pipeline. All models are optimized for the **OpenVINO 2026.0** runtime.

---

## High-Level Summary

| Model ID | Task | Base Architecture | Precision | Size (Optimized) |
| :--- | :--- | :--- | :--- | :--- |
| **Whisper-Base** | Speech-to-Text | Transformer (Encoder-only) | FP16 | ~150 MB |
| **SmolVLM2-256M** | Vision-Language | Transformer (Multimodal) | INT4 (NNCF) | ~190 MB |

---

## Audio Agent: Whisper-Base

The Audio Agent is responsible for transcribing video dialogue and timestamps into structured text.

* **Model Source:** OpenAI / HuggingFace (`openai/whisper-base`)
* **Optimization Strategy:** Exported to OpenVINO Intermediate Representation (IR) via `optimum-intel`.
* **Precision:** **FP16**. I chose FP16 over INT8 to maintain high word error rate (WER) performance on technical terminology while still utilizing the Apple Silicon GPU/NPU effectively.
* **Performance Note:** Capable of transcribing a 5-minute video in under 30 seconds on M-Series hardware.

---

## Vision Agent: SmolVLM2-256M

The Vision Agent analyzes sampled video frames to provide descriptive context (e.g., "A person is presenting a slide about quarterly earnings").

* **Model Source:** HuggingFace (`HuggingFaceTB/SmolVLM2-256M-Instruct`)
* **Optimization Strategy:** Quantized using the **Neural Network Compression Framework (NNCF)**.
* **Precision:** **INT4**. Weight-only quantization was applied to the language model head and vision encoder to fit within the 256MB-512MB RAM budget, preventing memory swaps during concurrent audio/vision processing.
* **Reasoning for Choice:** Replaced Moondream2 due to superior native OpenVINO graph compatibility and lower latency on ARM64 unified memory.

---

## Hardware Mapping

| Model | Primary Compute Device | Rationale |
| :--- | :--- | :--- |
| **Whisper** | NPU / GPU | Parallelizable transformer blocks; low latency requirements. |
| **SmolVLM2** | CPU / GPU | High memory bandwidth requirement; benefits from unified memory access. |

---

## Reproduction & Export

To re-export these models for the registry, use the following CLI commands within the `vda_native` environment:

```bash
# Export Whisper to OpenVINO
optimum-cli export openvino --model openai/whisper-base whisper_ov_model/

# Quantize SmolVLM2 to INT4
nncf_quantize --model smolvlm2_path --precision int4 --output_dir smol_ov_model/
```
