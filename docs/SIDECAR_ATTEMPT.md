# Sidecar Packaging & Distribution Report

## Objective
To fulfill the bonus requirement for a packaged backend executable, I attempted to bundle the Python gRPC backend into a **Tauri Sidecar** using PyInstaller. The goal was to provide a zero-dependency installation experience for the end-user.

## Technical Approach
The packaging strategy involved:
1. **PyInstaller Spec Configuration**: Using a `one-dir` layout to handle the heavy shared libraries (`.dylib`) of OpenVINO and PyTorch.
2. **Surgical Injection**: Excluding massive AI frameworks from PyInstaller's static analysis to bypass macOS code-signing "internal errors" (specifically with `libtbb.dylib`), and manually injecting them into the `_internal` directory post-build.
3. **Ad-hoc Signing & Entitlements**: Using a custom `entitlements.plist` to disable Library Validation (`com.apple.security.cs.disable-library-validation`), allowing the sidecar to load manually injected, unsigned AI libraries.
4. **Environment Bootstrapping**: A custom `server.py` entry point designed to re-map `sys.path` to the sidecar’s internal runtime.

## Encountered Challenges

### 1. macOS Code-Signing Subsystem Conflicts
The primary blocker was an "Internal Error in Code Signing subsystem" when attempting to sign OpenVINO-optimized binaries. Even with manual `codesign --remove-signature` and permission resets, the macOS kernel frequently rejected the signature of `libtbb.12.dylib` during the Tauri bundling phase.

### 2. Standard Library Pruning ("Dependency Whack-a-Mole")
Because the AI libraries were manually injected to bypass the signing errors, PyInstaller's static analysis could not see their sub-dependencies. This led to a cascade of `ModuleNotFoundError` at runtime for core Python modules that are usually lazy-loaded:
- `http.cookies`, `uuid`, `cmath`, `timeit`, and finally `pickletools`.

### 3. C# Launcher Bonus Point
The assignment mentions a C# launcher. In a Windows-centric environment, PyInstaller is significantly more stable. However, on Apple Silicon, the combination of ARM64 architecture, Hardened Runtime, and the weight of the OpenVINO/Torch stack creates a level of friction that risks the stability of the core application.

## Final Decision: Pivot to Manual Environment Setup
After several hours of iterative packaging, I have decided to pivot away from the Sidecar approach to ensure the **stability and reliability** of the AI Agents. 

**Why this is the right engineering choice:**
- **Reliability:** A manual environment (Conda/Miniforge) ensures that `importlib.metadata` and complex C-extensions for Torch/OpenVINO load correctly.
- **Performance:** Native environment execution avoids the overhead of the PyInstaller bootloader and temporary file extraction.
- **Submission Focus:** The core requirements—Agentic AI, MCP servers, and OpenVINO inference—are fully functional and performant in a standard Python runtime.

## Future Improvements (Given More Time)
1. **Conda-Pack**: Explore `conda-pack` to archive the entire environment as a sidecar instead of using PyInstaller.
2. **Dockerization**: For non-MacOS targets, a lightweight container would solve the dependency isolation.
3. **C++ Backend**: Moving the gRPC server logic to C++ to utilize the OpenVINO C++ API directly, removing the Python packaging overhead entirely.