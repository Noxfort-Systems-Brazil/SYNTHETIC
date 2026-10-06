# ⚡ Referencia de APIs y Arquitectura de Servicios

Este documento proporciona la referencia técnica para desarrolladores de las principales clases, orquestadores y contratos de datos de **SYNTHETIC**.

⬅️ [Centro de Documentación](README.md) | 🏛️ [Arquitectura del Sistema](architecture.md) | 🧠 [IA Generativa y Física](generative_ai_and_physics.md) | 🧪 [Pruebas y QA](testing.md)

---

## 1. Orquestador Central (`src/core/simulation_logic.py`)

### `class SimulationOrchestrator`
* `__init__(self, config: SimulationConfig, progress_callback: Optional[Callable] = None)`: Inicializa la configuración y las funciones de retorno para la interfaz.
* `run(self) -> GenerationReport`: Ejecuta la validación, la Fase 1 (Sueño cognitivo), el purgado de VRAM, la Fase 2 (Síntesis y difusión) y la generación de archivos multimodales.
* `cancel(self) -> None`: Cancela la ejecución de forma segura y libera recursos GPU.

---

## 2. Gestor Secuencial de Modelos (`src/services/model_manager.py`)

Garantiza la carga bajo demanda y la purga inmediata de memoria de vídeo:
* `load_screenwriter() / release_screenwriter()`
* `load_vae_tcn() / release_vae_tcn()`
* `load_csdi() / release_csdi()`
* `load_gatv2() / release_gatv2()`

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
