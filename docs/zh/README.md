<div align="center">

<img src="../assets/synthetic-logo.png" alt="SYNTHETIC Logo" width="120" />

# SYNTHETIC — 技术文档套件
### 系统工程架构、生成式人工智能模型与多模态数据合成
*Noxfort Systems — A State Of Art Company*

[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat&logo=github)](https://github.com/Noxfort-Systems-Brazil/SYNTHETIC)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.0%2B-76B900?style=flat&logo=nvidia&logoColor=white)](https://nvidia.com/)

---

🌐 **语言导航：** **[🇺🇸 English](../en/README.md)** • **[🇧🇷 Português (Brasil)](../pt-br/README.md)** • **[🇫🇷 Français](../fr/README.md)** • **[🇪🇸 Español](../es/README.md)** • **[🇷🇺 Русский](../ru/README.md)** • **[🇨🇳 简体中文](README.md)** • **[📚 文档中心](../README.md)**

---

</div>

## 欢迎查阅官方技术文档

本目录汇集了 **SYNTHETIC** 生态系统的完整**简体中文**技术文档库。SYNTHETIC 是由 Noxfort Systems 研发的面向量导智能交通系统 (ITS) 的高保真多模态交通场景人工智能生成引擎。

## 专业技术指南索引

| 文档 | 领域与范围 | 核心内容 |
|---|---|---|
| 🏛️ **[系统架构核心蓝图](architecture.md)** | 系统架构规范 | 两阶段执行流水线（梦想认知 vs. 物理合成）、显式 VRAM 垃圾回收、顺序延迟加载与 SRP 隔离。 |
| 🧠 **[生成式 AI 与物理护卫](generative_ai_and_physics.md)** | 神经网络数学原理 | Phi-4-mini 编剧模型、VAE-TCN 物理流形守卫、基于分数的 CSDI 条件扩散模型及 Optuna 实时超参数优化。 |
| 📡 **[多模态数据生成器](multimodal_generators.md)** | 传感器仿真 | Waze JSON 众包事件、TomTom 道路速度切片、车牌识别 (LPR) 视觉相机及地感线圈 CSV。 |
| 🗺️ **[空间拓扑与马尔可夫气象](spatial_and_environment.md)** | 地理拓扑与环境物理 | OpenStreetMap `.osm` 解析、Haversine 大圆距离道路投影吸附、GATv2 图注意力及马尔可夫天气转移。 |
| 🖥️ **[桌面界面与动态多语言](ui_and_localization.md)** | 前端与 i18n 国际化 | CustomTkinter 框架、TkinterMapView 交互式地图布点、单例 Translator 及运行时无重启即时切换语言。 |
| ⚡ **[API 与服务架构参考](api_reference.md)** | 代码接口与数据契约 | `SimulationOrchestrator`、`EnvironmentManager`、`ModelManager`、`DirectorAgent` 类签名及生成器接口。 |
| 🧪 **[测试套件与质量保证](testing.md)** | 质量保证规范 | 50 个单元测试用例（100% 通过率）、确定性 Mock 策略及物理极限不变量校验。 |
| 🚀 **[硬件环境与部署配置](deployment_and_setup.md)** | 部署运维与运行环境 | 系统环境要求、Python 虚拟环境搭建、NVIDIA CUDA 12 算力配置、GGUF 权重金库管理与启动。 |

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i><br/>
  <i>智能交通工程 • SYNTHETIC 引擎 v1.0.0</i>
</div>
