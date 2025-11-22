# WSL2 Quick Start Guide for V6 Experiments

## When to Switch to WSL2

**Switch if Windows experiments take > 2 hours**

Current status after 1.5 hours: Still running, no output yet.

## Quick Decision Tree

```
Is 1D-2D done? → Check: ls "W:\foundation\15 experiment\v6-gpu\*.csv"
  ├─ YES (< 2 hours) → Continue on Windows, run 3D-5D overnight
  └─ NO (> 2 hours)  → Switch to WSL2 now for better performance
```

## Setup Steps (1-2 hours)

### Step 1: Open WSL2 Ubuntu

```bash
# From Windows PowerShell or Command Prompt:
wsl

# You should now see Ubuntu prompt: user@hostname:~$
```

### Step 2: Run Automated Setup

```bash
# Copy setup script to WSL2 home directory
cp /mnt/w/foundation/"15 experiment"/wsl2_ipex_setup.sh ~/
chmod +x ~/wsl2_ipex_setup.sh

# Run setup (takes ~30-60 minutes)
~/wsl2_ipex_setup.sh
```

### Step 3: Activate Environment and Run

```bash
# Activate Python environment
source ~/ipex-gpu-env/bin/activate

# Navigate to code
cd ~/foundation/v6-gpu

# Run 1D-2D verification
python run_verification.py

# Or create scripts for all dimensions (see below)
```

## Running All Dimensions in WSL2

After setup completes, create 3D-5D scripts:

```bash
# Still in ~/foundation/v6-gpu directory
# Create 3D script
cat > v6_gpu_3d.py << 'EOF'
# Copy content from v6_gpu_2d.py
# Change: DIMENSION = 3, GRID_SIZE = (48, 48, 48)
EOF

# Similar for 4D and 5D...
# Then run them sequentially or in background
```

## Monitoring Progress

### In WSL2:

```bash
# Check if processes running
ps aux | grep python

# Monitor output (if running in background)
tail -f ~/foundation/v6-gpu/output.log

# Check for results
ls -lh ~/foundation/v6-gpu/*.csv
```

### Expected Timings (WSL2 with CPU):

- 1D: ~30-60 minutes
- 2D: ~1-2 hours
- 3D: ~4-6 hours (would be ~1 hour with GPU)
- 4D: ~2-4 hours (would be ~30 min with GPU)
- 5D: ~3-5 hours (would be ~30 min with GPU)

## Copy Results Back to Windows

```bash
# From within WSL2:
cp ~/foundation/v6-gpu/*.csv /mnt/w/foundation/"15 experiment"/v6-gpu/
cp ~/foundation/v6-gpu/*.json /mnt/w/foundation/"15 experiment"/v6-gpu/
```

## Troubleshooting

### GPU Not Detected in WSL2

If `torch.xpu.is_available()` returns False:

**This is OK!** The code will fall back to CPU, which still benefits from:
- Better Linux Python performance (~10-20% faster)
- Native multiprocessing (no Windows overhead)
- More stable parallel execution

### Setup Script Fails

Common issues:
1. **Network error**: Retry the command that failed
2. **Permission denied**: Use `sudo` for system packages
3. **Python 3.10 not found**: `sudo apt install software-properties-common`, then `sudo add-apt-repository ppa:deadsnakes/ppa`

### Performance Still Slow

If WSL2 isn't faster:
1. Check CPU usage: `top` (should show multiple python processes at 100%)
2. Check RAM: `free -h` (should have plenty available)
3. Consider OVH cloud instance instead

## Next Steps After 1D-2D Completes

### Option A: Continue in WSL2
- Create 3D-5D scripts
- Run overnight
- Results tomorrow

### Option B: Rent OVH GPU Instance
- For 3D-5D only
- ~€8-16 for 4-8 hours
- Professional GPU (faster than Arc)

## Current Windows Experiments

**Don't kill** current Windows experiments unless:
- They exceed 3 hours with no output
- You want to start fresh in WSL2

Can run both in parallel (Windows + WSL2) if desired.
