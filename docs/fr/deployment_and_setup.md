# 🚀 Déploiement, Accélération CUDA et Configuration Matérielle

Ce document précise les prérequis système, la création de l'environnement virtuel Python, la configuration de l'accélération matérielle NVIDIA CUDA 12 et la mise en place du coffre de modèles GGUF pour **SYNTHETIC**.

⬅️ [Hub de Documentation](README.md) | 🏛️ [Architecture Système](architecture.md) | 🧪 [Tests et QA](testing.md) | ⚡ [Référence des API](api_reference.md)

---

## 1. Exigences Système

| Composant | Recommandation Minimale | Configuration Optimale |
|---|---|---|
| **Système d'Exploitation** | Linux (Ubuntu 22.04+), Windows 10/11 | Linux (Ubuntu 24.04 LTS) |
| **Python** | 3.10+ | 3.11 ou 3.12 |
| **Mémoire Vive (RAM)** | 8 Go | 16 Go ou 32 Go DDR4/DDR5 |
| **Stockage** | 10 Go disponibles | 50 Go+ SSD NVMe |
| **GPU / VRAM** | CPU uniquement (lent) | NVIDIA RTX (6 Go+ VRAM, CUDA 12.0+) |

---

## 2. Procédure d'Installation

```bash
git clone https://github.com/Noxfort-Systems-Brazil/SYNTHETIC.git
cd SYNTHETIC

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Modèle Phi-4 dans le Coffre
Assurez-vous que le modèle quantifié est présent :
```text
src/models/vault/Phi-4-mini-reasoning-UD-Q6_K_XL.gguf
```

### Lancement de l'Application
```bash
python main.py
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
