# ⚡ Справочник API и архитектура сервисов

Документ содержит описание основных классов, сервисов и интерфейсов ядра **SYNTHETIC** для разработчиков.

⬅️ [Главный Хаб](README.md) | 🏛️ [Архитектура системы](architecture.md) | 🧠 [Генеративный ИИ и физика](generative_ai_and_physics.md) | 🧪 [Тестирование и QA](testing.md)

---

## 1. Главный оркестратор (`src/core/simulation_logic.py`)

### `class SimulationOrchestrator`
* `__init__(self, config: SimulationConfig, progress_callback: Optional[Callable] = None)`: Инициализация параметров генерации и функций обратного вызова телеметрии.
* `run(self) -> GenerationReport`: Выполняет полный цикл генерации: валидацию, Фазу 1 (когнитивный сценарий), очистку VRAM, Фазу 2 (диффузионный синтез) и запись файлов.
* `cancel(self) -> None`: Корректная отмена генерации и освобождение тензоров из видеопамяти.

---

## 2. Менеджер моделей (`src/services/model_manager.py`)

Управляет последовательной загрузкой и принудительной выгрузкой нейросетей:
* `load_screenwriter() / release_screenwriter()`
* `load_vae_tcn() / release_vae_tcn()`
* `load_csdi() / release_csdi()`
* `load_gatv2() / release_gatv2()`

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
