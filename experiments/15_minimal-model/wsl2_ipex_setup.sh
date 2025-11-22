#!/bin/bash
#
# WSL2 Intel Arc GPU Setup for V6 Experiments
# Run this in WSL2 Ubuntu to set up IPEX + GPU compute
#

set -e  # Exit on error

echo "========================================================================"
echo "WSL2 Intel Arc GPU Setup for V6 Dimensional Experiments"
echo "========================================================================"
echo ""

# Step 1: System update
echo "[1/8] Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install Python 3.10
echo ""
echo "[2/8] Installing Python 3.10..."
sudo apt install -y python3.10 python3.10-venv python3.10-dev
sudo apt install -y build-essential git wget curl

# Step 3: Install Intel GPU compute runtime
echo ""
echo "[3/8] Installing Intel GPU compute stack..."
wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | \
  sudo gpg --dearmor --output /usr/share/keyrings/intel-graphics.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu jammy client" | \
  sudo tee /etc/apt/sources.list.d/intel-gpu-jammy.list

sudo apt update

# Install Level Zero and OpenCL runtime
sudo apt install -y \
  intel-opencl-icd \
  intel-level-zero-gpu \
  level-zero \
  level-zero-dev

# Step 4: Create Python virtual environment
echo ""
echo "[4/8] Creating Python 3.10 virtual environment..."
cd ~
python3.10 -m venv ipex-gpu-env
source ipex-gpu-env/bin/activate

# Step 5: Install PyTorch 2.3.0 (compatible with IPEX)
echo ""
echo "[5/8] Installing PyTorch 2.3.0..."
pip install --upgrade pip
pip install torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/cpu

# Step 6: Install Intel Extension for PyTorch
echo ""
echo "[6/8] Installing Intel Extension for PyTorch..."
pip install intel-extension-for-pytorch==2.3.0
pip install oneccl_bind_pt==2.3.0 --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/cpu/us/

# Step 7: Install additional dependencies
echo ""
echo "[7/8] Installing additional Python packages..."
pip install numpy scipy matplotlib pandas

# Step 8: Copy code from Windows
echo ""
echo "[8/8] Copying code from Windows..."
mkdir -p ~/foundation/v6-gpu
cp -r /mnt/w/foundation/"15 experiment"/v6-gpu/* ~/foundation/v6-gpu/ 2>/dev/null || \
  echo "Note: Manually copy files if path differs"

# Test GPU availability
echo ""
echo "========================================================================"
echo "Testing GPU setup..."
echo "========================================================================"
python << 'EOF'
import torch
print(f"PyTorch version: {torch.__version__}")

try:
    import intel_extension_for_pytorch as ipex
    print(f"IPEX version: {ipex.__version__}")
    print(f"IPEX available: True")
except ImportError:
    print("IPEX available: False")

# Check XPU
if hasattr(torch, 'xpu') and torch.xpu.is_available():
    print(f"XPU available: True")
    print(f"XPU device count: {torch.xpu.device_count()}")
    print(f"XPU device name: {torch.xpu.get_device_name(0)}")
else:
    print(f"XPU available: False")
    print("Note: GPU may not be accessible in WSL2. Will fall back to CPU.")
EOF

echo ""
echo "========================================================================"
echo "Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "1. Activate environment: source ~/ipex-gpu-env/bin/activate"
echo "2. Navigate to code: cd ~/foundation/v6-gpu"
echo "3. Run experiments: python run_verification.py"
echo ""
echo "To check GPU status later:"
echo "  python -c 'import torch; print(torch.xpu.is_available())'"
echo ""
echo "Environment location: ~/ipex-gpu-env"
echo "Code location: ~/foundation/v6-gpu"
echo "========================================================================"
