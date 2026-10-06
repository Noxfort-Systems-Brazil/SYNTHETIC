# ⚡ API 接口与底层服务架构参考

本文档提供面向二次开发者的 **SYNTHETIC** 核心 Python 类、服务调度器与数据接口技术规范。

⬅️ [文档中心](README.md) | 🏛️ [系统架构规范](architecture.md) | 🧠 [生成式 AI 与物理护卫](generative_ai_and_physics.md) | 🧪 [测试套件](testing.md)

---

## 1. 仿真总调度器 (`src/core/simulation_logic.py`)

### `class SimulationOrchestrator`
* `__init__(self, config: SimulationConfig, progress_callback: Optional[Callable] = None)`：初始化参数与进度回调。
* `run(self) -> GenerationReport`：执行两阶段流水线：验证依赖、第一阶段认知构想、显存释放、第二阶段扩散合成与文件落地。
* `cancel(self) -> None`：安全中断计算并清理 GPU 显存。

---

## 2. 顺序模型内存管理器 (`src/services/model_manager.py`)

管理大型神经网络的按需激活与显存即时回收：
* `load_screenwriter() / release_screenwriter()`
* `load_vae_tcn() / release_vae_tcn()`
* `load_csdi() / release_csdi()`
* `load_gatv2() / release_gatv2()`

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
