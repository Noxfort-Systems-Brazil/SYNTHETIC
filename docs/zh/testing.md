# 🧪 测试套件与质量保证指南

本文档介绍 **SYNTHETIC** 平台的自动化测试架构、确定性 Mock 策略与物理不变量约束验证。

⬅️ [文档中心](README.md) | 🏛️ [系统架构规范](architecture.md) | 🧠 [生成式 AI 与物理护卫](generative_ai_and_physics.md) | ⚡ [API 参考](api_reference.md)

---

## 1. 质量保证工程规范

系统内置 **50 个自动化单元测试用例，保持 100% 完美通过率**：
* `test_environment.py`：校验 Ground Zero 周期对准点与马尔可夫天气转移概率。
* `test_pinn_hybrid.py`：校验 VAE-TCN 物理流形、$[20, 110]\text{ km/h}$ 速度截断及 Optuna 调优。
* `test_map_provider.py`：校验 `.osm` XML 解析与 Haversine 道路路面投影。
* `test_generators.py`：校验 Waze、TomTom、相机及线圈数据结构。
* `test_translator.py`：校验 6 种语言本地化字典加载与动态插值。

执行全部测试：
```bash
.venv/bin/python -m unittest discover -s tests
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
