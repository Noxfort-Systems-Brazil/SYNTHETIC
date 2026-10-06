# 🚀 Deployment, CUDA Acceleration & Hardware Setup

This document specifies the deployment prerequisites, hardware requirements, virtual environment setup, CUDA 12 acceleration configuration, and model vault provisioning for **SYNTHETIC**.

⬅️ [Documentation Hub](README.md) | 🏛️ [System Architecture](architecture.md) | 🧪 [Testing Suite](testing.md) | ⚡ [API Reference](api_reference.md)

---

## 1. System Requirements

| Component | Minimum Specification | Recommended Specification |
|---|---|---|
| **Operating System** | Linux (Ubuntu 22.04+), Windows 10/11 | Linux (Ubuntu 24.04 LTS) |
| **Python** | Python 3.10+ | Python 3.11 or 3.12 |
| **System RAM** | 8 GB | 16 GB or 32 GB DDR4/DDR5 |
| **Storage** | 10 GB Free Storage | 50 GB+ NVMe SSD |
| **GPU / VRAM** | CPU-only (execution will be slow) | NVIDIA RTX (6 GB+ VRAM, CUDA 12.0+) |

---

## 2. Step-by-Step Installation

### 2.1 Clone Repository & Prepare Virtual Environment
```bash
# Clone the repository
git clone https://github.com/Noxfort-Systems-Brazil/SYNTHETIC.git
cd SYNTHETIC

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 2.2 Install Core Dependencies
Install packages listed in `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Verify CUDA Acceleration & PyTorch Geometric
Ensure PyTorch correctly interfaces with your host GPU:

```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

---

## 3. Provisioning the Model Vault (`src/models/vault/`)

The cognitive Screenwriter Agent relies on the quantized **Phi-4-mini** reasoning model in GGUF format.

1. Ensure the directory exists:
   ```bash
   mkdir -p src/models/vault
   ```
2. Place the GGUF model file inside `src/models/vault/`:
   ```text
   src/models/vault/Phi-4-mini-reasoning-UD-Q6_K_XL.gguf
   ```
3. The internal `ModelManager` and `DependencyChecker` automatically scan this path upon launch.

---

## 4. Launching SYNTHETIC

Start the graphical interface with:

```bash
python main.py
```

### Workflow in the GUI:
1. **Output Directory:** Designate the target path where synthesized feeds will be written.
2. **Geographical Map:** Choose a valid OpenStreetMap file (`.osm` or `.osm.gz`).
3. **Sensor Placement:** Click **SELECIONAR NO MAPA** to open the TkinterMapView interface. Click on street pavement to place Cameras (red) and Inductive Loops (blue).
4. **Parameters:** Configure simulation duration (days), interval (minutes), flow intensity (`Pequeno`, `Médio`, `Grande`, `Caótico`), and sensor corruption percentages.
5. **Start Generation:** Click **GERAR DADOS SINTÉTICOS** to initiate the Two-Phase neural synthesis pipeline.

---

## 5. Troubleshooting & FAQ

### CUDA Out of Memory (OOM)
* **Symptom:** `torch.cuda.OutOfMemoryError` during Phase 2.
* **Resolution:** Ensure no other GPU-intensive tasks are active. SYNTHETIC sequentially releases models, but if VRAM is less than 4 GB, reduce the CSDI diffusion steps in the configuration or allow CPU fallback.

### Headless Linux Display Error (`_tkinter.TclError`)
* **Symptom:** `no display name and no $DISPLAY environment variable`.
* **Resolution:** SYNTHETIC features a graphical interface. Ensure an X11 server or Wayland session is active, or use `xvfb-run python main.py` when executing inside headless containerized environments.

---

<div align="center">
  <img src="assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
