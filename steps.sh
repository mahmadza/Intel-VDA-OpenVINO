
# Clone repo
gh repo clone mahmadza/Intel-VDA-OpenVINO

cd Intel-VDA-OpenVINO/


#############################
# Phase 1: The Groundwork
#############################

# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env


#Create the app
npx create-tauri-app@latest
# Project name: app
# Identifier: com.intel.vda
# Language: TypeScript/JavaScript
# Package manager: npm
# UI template: React
# UI flavor: TypeScript

# Start the dev environment to ensure all hooks are ready
cd app/
npm install
npm run tauri dev


# Setup python backend
cd backend/
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install grpcio grpcio-tools
# Generate python code from the Proto
python -m grpc_tools.protoc -I../proto --python_out=. --grpc_python_out=. ../proto/vda.proto


# Install the client library
cd app/
npm install @grpc/grpc-js @grpc/proto-loader


# To start backend server:
cd backend/
source venv/bin/activate
python server.py 

# Then, to start tauri, in another Terminal:
cd app/
npm run tauri dev


#############################
# Phase 2: the Brain
#############################
cd backend/
source venv/bin/activate
# later will have problems because this is only python 3.8

# We need libraries that bridge Hugging Face models
# with OpenVino runtime.
pip install openvino-dev[onnx,pytorch]
pip install optimum[intel] # The "Hugging Face" way to use OpenVINO
pip install librosa moviepy opencv-python # For video and audio
pip install transformers accelerate # AI stack


# First, install Install Miniforge (Native ARM64 Conda)
# Then, create a fresh native environment
conda create -n vda_native python=3.10 -y
conda activate vda_native

#  Install the binary heavy-hitters via Conda-Forge first (Native ARM64)
conda install -c conda-forge numpy=1.26 numba llvmlite -y

# Install the Intel/OpenVINO stack
pip install openvino>=2025.4.0 optimum-intel transformers accelerate
# Install AI stack
pip install moviepy opencv-python Pillow librosa torch torchvision torchaudio
pip install num2words