# 🧪 Testing Suite & Quality Assurance

This document details the test harness, automated test suites, deterministic mocking strategies, and regression benchmarks implemented in **SYNTHETIC**.

⬅️ [Documentation Hub](README.md) | 🏛️ [System Architecture](architecture.md) | 🧠 [Generative AI & Physics](generative_ai_and_physics.md) | ⚡ [API Reference](api_reference.md)

---

## 1. Quality Assurance Philosophy

SYNTHETIC incorporates deep neural networks alongside discrete heuristic systems. To guarantee mathematical stability and ensure that physical invariant clamps cannot be accidentally bypassed, the system maintains a **100% passing test suite (50 automated unit tests)**.

```text
============================= TEST SUITE OVERVIEW =============================
Directory: tests/
Framework: unittest / pytest
Test Count: 50 Passed
Execution Time: ~8.8 seconds (with full GPU and AutoML optimization verification)
Pass Rate: 100%
================================================================================
```

---

## 2. Test Module Breakdown

The table below describes all test modules located in `tests/`:

| Test Module | Primary Scope | Validated Mechanisms |
|---|---|---|
| `test_environment.py` | Temporal & Weather Physics | Monday 00:00:00 Ground Zero calculations, Markov transition probability integrity, and weather tuple formatting. |
| `test_pinn_hybrid.py` | Neural Physics & AutoML | VAE-TCN manifold validation, speed clamping ($[20, 110]\text{ km/h}$), DeepONet prior loading, and Optuna JIT retuning loop. |
| `test_map_provider.py` | Spatial Parsing & Haversine | Ingestion of `.osm`, `.osm.gz`, and SUMO `.net.xml` networks; Haversine snap-to-road mathematical projection. |
| `test_generators.py` | Multi-Modal Output Specs | Validation of Waze JSON alerts, TomTom flow data, ANPR Camera JSON payloads, and Inductive Loop CSV formatting. |
| `test_flow_schedule.py` | Dynamic Flow Schedules | Traffic density transitions across diurnal time curves and amplitude scaling. |
| `test_flow_components.py` | Invariants & Rules | Hard mathematical checks against negative speeds, vehicle density bounds, and flow rates. |
| `test_traffic_simulator.py` | Simulation Core | Integration of flow strategies (`Small`, `Medium`, `Large`, `Chaotic`) with simulated road segments. |
| `test_translator.py` | Dynamic Localization (i18n) | Loading of all 6 language dictionaries (`en`, `pt-br`, `fr`, `es`, `ru`, `zh-cn`), dynamic key interpolation, and fallback mechanisms. |
| `test_dependency_checker.py` | Hardware & Dependencies | Detection and validation of PyTorch CUDA, Optuna, `llama-cpp-python`, `torch_geometric`, and `tkintermapview`. |
| `test_ui_components.py` | GUI Layout & Logic | CustomTkinter frame instantiation, input validation, and parameter serialization. |

---

## 3. Running the Test Suite

### 3.1 Standard Test Execution
Execute the entire test suite using Python's native test discovery:

```bash
.venv/bin/python -m unittest discover -s tests
```

### 3.2 Running Specific Test Modules
To run isolated neural or environment tests:

```bash
# Test neural physics guardian and AutoML
.venv/bin/python -m unittest tests/test_pinn_hybrid.py

# Test spatial OSM map provider
.venv/bin/python -m unittest tests/test_map_provider.py

# Test dynamic i18n localization
.venv/bin/python -m unittest tests/test_translator.py
```

---

## 4. Deterministic Mocking Strategies

To enable fast and reproducible CI/CD execution without requiring real-time downloads of multi-gigabyte models or physical GPS hardware:
1. **Mocked Map XML:** Synthetic unit tests generate transient, minimal XML files in `/tmp` containing strictly defined `<node>` and `<way>` elements, removing external file dependencies.
2. **Deterministic Random Seeds:** Tests involving diffusion and Markov state transitions pin `torch.manual_seed(42)` and `numpy.random.seed(42)` to verify exact numerical convergence.
3. **Hardware Fallback Validation:** Tests automatically assert that if CUDA is absent, execution falls back gracefully to CPU Tensor operations without raising uncaught exceptions.

---

<div align="center">
  <img src="assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
