
# Clone repo
gh repo clone mahmadza/Intel-VDA-OpenVINO

cd Intel-VDA-OpenVINO/

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
