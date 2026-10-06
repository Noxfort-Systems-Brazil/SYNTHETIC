# 🚀 部署配置、CUDA 算力加速与环境搭建

本文档规定 **SYNTHETIC** 的运行环境要求、Python 虚拟环境搭建、NVIDIA CUDA 12 显卡加速配置以及本地大模型权重库管理。

⬅️ [文档中心](README.md) | 🏛️ [系统架构规范](architecture.md) | 🧪 [测试套件](testing.md) | ⚡ [API 参考](api_reference.md)

---

## 1. 系统配置要求

| 硬件配置 | 最低配置 | 推荐配置 |
|---|---|---|
| **操作系统** | Linux (Ubuntu 22.04+), Windows 10/11 | Linux (Ubuntu 24.04 LTS) |
| **Python** | 3.10+ | 3.11 或 3.12 |
| **内存 (RAM)** | 8 GB | 16 GB 或 32 GB DDR4/DDR5 |
| **硬盘空间** | 10 GB 可用空间 | 50 GB+ NVMe 固态硬盘 |
| **显卡 / 显存** | 仅 CPU 运算（较慢） | NVIDIA RTX (6 GB+ 显存, CUDA 12.0+) |

---

## 2. 安装步骤

```bash
git clone https://github.com/Noxfort-Systems-Brazil/SYNTHETIC.git
cd SYNTHETIC

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 部署 Phi-4 权重文件
将量化后的 GGUF 模型放置于以下路径：
```text
src/models/vault/Phi-4-mini-reasoning-UD-Q6_K_XL.gguf
```

### 启动平台
```bash
python main.py
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
