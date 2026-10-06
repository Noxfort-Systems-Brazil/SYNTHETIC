# 🚀 Instalación, Aceleración CUDA y Configuración de Hardware

Este documento especifica los requisitos de infraestructura, la creación del entorno virtual Python, la configuración de aceleración con NVIDIA CUDA 12 y la provisión del modelo Phi-4 en el vault local de **SYNTHETIC**.

⬅️ [Centro de Documentación](README.md) | 🏛️ [Arquitectura del Sistema](architecture.md) | 🧪 [Pruebas y QA](testing.md) | ⚡ [Referencia de APIs](api_reference.md)

---

## 1. Requisitos del Sistema

| Componente | Requisito Mínimo | Configuración Recomendada |
|---|---|---|
| **Sistema Operativo** | Linux (Ubuntu 22.04+), Windows 10/11 | Linux (Ubuntu 24.04 LTS) |
| **Python** | 3.10+ | 3.11 o 3.12 |
| **Memoria RAM** | 8 GB | 16 GB o 32 GB DDR4/DDR5 |
| **Almacenamiento** | 10 GB libres | 50 GB+ SSD NVMe |
| **GPU / VRAM** | CPU (lento) | NVIDIA RTX (6 GB+ VRAM, CUDA 12.0+) |

---

## 2. Instalación Paso a Paso

```bash
git clone https://github.com/Noxfort-Systems-Brazil/SYNTHETIC.git
cd SYNTHETIC

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Provisión del Modelo Phi-4
Coloque el archivo GGUF en la ruta:
```text
src/models/vault/Phi-4-mini-reasoning-UD-Q6_K_XL.gguf
```

### Ejecución
```bash
python main.py
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
