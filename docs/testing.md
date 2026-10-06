# 🧪 Testing Suite, Code Coverage & Quality Assurance

This document details the test harness, automated test suites, code coverage benchmarks (86%), deterministic mocking strategies, and regression testing implemented in **SYNTHETIC**.

⬅️ [Documentation Hub](index.md) | 🏛️ [System Architecture](architecture.md) | 🧠 [Generative AI & Physics](generative_ai_and_physics.md) | 🔄 [CI/CD Pipeline](ci_cd.md) | ⚡ [API Reference](api_reference.md)

---

## 1. Quality Assurance Philosophy

SYNTHETIC incorporates deep neural networks alongside discrete heuristic systems, real-time map topology processing, hydrodynamic PDE solvers, and an interactive desktop graphical interface. To guarantee mathematical stability, prevent physical violations from bypassing the safety manifolds, and ensure flawless UI operation across platforms, the project enforces a **100% passing test suite across 99 automated tests with 86% consolidated code coverage**.

```text
============================= TEST SUITE OVERVIEW =============================
Directory:         tests/
Runner:            pytest / unittest
Total Tests:       99 Passed (0 Failures, 0 Errors)
Consolidated Cov:  86% Total Statements Covered (3,236 / 3,765 stmts)
Execution Time:    ~16.3 seconds (full pipeline including PINN, Diffusion, & UI)
Pass Rate:         100%
================================================================================
```

---

## 2. Comprehensive Test Module Breakdown

The table below describes all 18 test suites located in `tests/`:

| Layer | Test Module | Primary Scope | Validated Mechanisms |
|---|---|---|---|
| **Frontend / UI** | `test_ui_views.py` | Full GUI View Lifecycle | Headless instantiation of all 7 `ttk.LabelFrame` sections (`Settings`, `Sources`, `Problems`, `Output`, `Map`, `Language`, `Action`), `MainView` facade, `MapSelectorWindow` sensor placement, and `DataGeneratorApp` event handlers. |
| **Frontend / UI** | `test_ui_components.py` | UI Helpers & Builders | `SimulationConfigBuilder` dictionary generation, `MockDialogService` modal isolation, and decoupled translator mocking. |
| **Frontend / UI** | `test_translator.py` | Dynamic Localization (i18n) | Loading of all 6 language dictionaries (`en`, `pt-br`, `fr`, `es`, `ru`, `zh-cn`), dynamic key interpolation, and fallback mechanisms. |
| **Cognitive / AI** | `test_screenwriter_and_slm.py` | Screenwriter & SLM Engine | Prompt template creation, weather transition persistence vs. change, city-scale macro mapping, SLM `<think>` regex stripping, and 2048-dim latent vector extraction. |
| **Neural Topology** | `test_gatv2.py` | Graph Attention Networks | `LightweightGATv2` multi-head convolutions, graph connectivity (`edge_index`), `global_mean_pool`, and spatial context extraction from `MapProvider`. |
| **Neural Topology** | `test_st_gatv2.py` | Spatio-Temporal Graph Attention | `STGATv2` dynamic attention, Time2Vec continuous periodic embedding, edge-index spatial message passing, tidal directional bias, and spatial attention weights. |
| **Physics / Hydrodynamics** | `test_physics_godunov.py` | Hydrodynamic Traffic Flow | Godunov numerical Riemann flux solver for LWR PDE, Greenshields fundamental diagram, Rankine-Hugoniot shockwave jump condition, SignalController actuated gating, and IncidentManager capacity degradation. |
| **Physics / AutoML** | `test_pinn_hybrid.py` | Neural Physics & Tuning | VAE-TCN manifold validation, Greenshields violation penalty loss, DeepONet operator prior, and Optuna JIT retuning loop. |
| **Optimization** | `test_optimizer_callbacks.py` | Training Optimization | Custom `EarlyStopping` delta monitoring, `StudyEarlyStoppingCallback` for Optuna studies, and `PruningCallback` intermediate checks. |
| **Hardware** | `test_telemetry.py` | Resource Telemetry | `HardwareTelemetry` daemon thread, periodic RAM logging via `psutil`, and VRAM monitoring via `nvidia-smi` parser. |
| **Orchestration** | `test_orchestrator_integration.py` | End-to-End Orchestrator | `SimulationOrchestrator` Two-Phase execution (Phase 1 Dreaming + Phase 2 Diffusion & Synthesis) and `main.py` non-blocking thread runner. |
| **Simulation Core** | `test_traffic_simulator.py` | Traffic Dynamics | Integration of flow strategies (`Small`, `Medium`, `Large`, `Chaotic`, `GodunovNetworkFlowStrategy`) with simulated road segments and flow propagation. |
| **Simulation Core** | `test_flow_schedule.py` | Dynamic Flow Schedules | 48-slot diurnal flow schedules, rush hour transitions, and sinusoidal amplitude scaling. |
| **Simulation Core** | `test_flow_components.py` | Invariants & Rules | Hard mathematical checks against negative speeds, vehicle density bounds, and flow rates. |
| **Spatial / Maps** | `test_map_provider.py` | Spatial Parsing & Haversine | Ingestion of `.osm`, `.osm.gz`, and SUMO `.net.xml` networks; Haversine snap-to-road mathematical projection. |
| **Environment** | `test_environment.py` | Temporal & Weather Physics | Monday 00:00:00 Ground Zero calculations, Markov transition probability integrity, and weather state forecasting. |
| **Multi-Modal** | `test_generators.py` | Output Generators | Validation of Waze JSON alerts, TomTom flow data, ANPR Camera JSON payloads, and Inductive Loop CSV formatting. |
| **System** | `test_dependency_checker.py` | Hardware & Dependencies | Detection and validation of PyTorch CUDA, Optuna, `llama-cpp-python`, `torch_geometric`, and `tkintermapview`. |

---

## 3. Running the Test Suite

### 3.1 Install Testing Dependencies
Testing dependencies are separated in `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
```

### 3.2 Execute Complete Test Suite with Coverage
Run all 99 tests and print the consolidated statement coverage table:

```bash
.venv/bin/pytest --cov=src --cov=ui --cov=main tests/
```

### 3.3 Running Isolated Layers
Run specific layers based on the component being modified:

```bash
# 1. Frontend & UI Tests (Headless)
.venv/bin/pytest -v tests/test_ui_views.py tests/test_ui_components.py tests/test_translator.py

# 2. Cognitive & Neural Physics Tests
.venv/bin/pytest -v tests/test_screenwriter_and_slm.py tests/test_gatv2.py tests/test_st_gatv2.py tests/test_pinn_hybrid.py

# 3. Hydrodynamic Physics & PDE Solvers
.venv/bin/pytest -v tests/test_physics_godunov.py

# 4. Optimization & Telemetry Tests
.venv/bin/pytest -v tests/test_optimizer_callbacks.py tests/test_telemetry.py

# 5. End-to-End Orchestrator Integration
.venv/bin/pytest -v tests/test_orchestrator_integration.py
```

---

## 4. Headless UI Testing Strategy

SYNTHETIC features a full desktop GUI powered by `tkinter`, `ttk`, and `tkintermapview`. Testing graphical widgets in continuous integration or headless server environments presents a challenge because an active display server (`$DISPLAY`) is typically absent.

SYNTHETIC overcomes this through a **dual-mode testing strategy**:
1. **Hidden Root Instantiation (`root.withdraw()`):** In environments with a virtual or physical display, all GUI components are instantiated with hidden window decorations, executing real widget layout passes and event bindings without popping up windows.
2. **Decoupled Architecture with Injected Services:**
   * Dialogs are abstracted behind `IDialogService`, allowing `MockDialogService` to verify modal alerts without blocking execution.
   * Translations are abstracted behind `ITranslator`, allowing `MockTranslator` to verify key propagation without reading disk assets.
   * Generation triggers execute non-blocking callbacks, enabling headless assertions of configuration compilation.

---

## 5. Deterministic Mocking Strategies

To enable fast, reproducible execution without downloading multi-gigabyte models or requiring GPU clusters during testing:
1. **Mocked SLM Inference:** `test_screenwriter_and_slm.py` and `test_orchestrator_integration.py` mock the `Llama` completion and embedding methods, verifying reasoning tag extraction and latent vector padding in milliseconds.
2. **Transient Map XML:** Spatial unit tests generate minimal XML structures in `/tmp` containing strictly defined `<node>` and `<way>` elements, eliminating external map dependencies.
3. **Deterministic Seeds:** Tests involving diffusion and Markov state transitions use deterministic seeds to guarantee numerical reproducibility.
4. **Hardware Fallback Validation:** Tests automatically verify that if CUDA is absent, execution falls back gracefully to CPU Tensor operations without raising uncaught exceptions.

---

<div align="center">
  <img src="assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
