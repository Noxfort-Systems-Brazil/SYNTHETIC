# ⚡ API & Services Architecture Reference

This document provides the developer API reference for the core Python classes, services, orchestrators, and data contracts that compose the **SYNTHETIC** engine.

⬅️ [Documentation Hub](README.md) | 🏛️ [System Architecture](architecture.md) | 🧠 [Generative AI & Physics](generative_ai_and_physics.md) | 🧪 [Testing Suite](testing.md)

---

## 1. Core Simulation Orchestrator (`src/core/simulation_logic.py`)

### `class SimulationOrchestrator`
The master orchestrator coordinating the Two-Phase lifecycle, thread telemetry, and disk I/O.

#### Methods
* `__init__(self, config: SimulationConfig, progress_callback: Optional[Callable] = None)`
  Initializes the orchestrator with generation configuration parameters and telemetry callbacks.
* `run(self) -> GenerationReport`
  Executes the simulation pipeline:
  1. Validates dependencies via `DependencyChecker`.
  2. Parses map topology via `OSMMapProvider`.
  3. Executes Phase 1 Dreaming with `ScreenwriterAgent`.
  4. Releases Screenwriter VRAM.
  5. Executes Phase 2 Synthesis with `DirectorAgent`.
  6. Dispatches generated multi-modal feeds through the fault corruption layer.
* `cancel(self) -> None`
  Safely aborts ongoing background generation and releases held GPU memory.

---

## 2. Environment & Meteorological Physics (`src/core/environment.py`)

### `class EnvironmentManager`
Manages calendar synchronization and the Markov-chain weather evolution.

#### Methods
* `get_next_monday_midnight(base_date: Optional[datetime] = None) -> datetime`
  Calculates the temporal Ground Zero anchor point for standardized weekly cycles.
* `get_dynamic_weather(self, current_weather: Optional[str] = None) -> Tuple[str, str, str]`
  Samples the Markov transition state machine in `config/weather_rules.json`. Returns:
  `(condition, intensity, characteristic)` (e.g., `("Rain", "Heavy", "with slick roads")`).

---

## 3. Cognitive & Executive Agents (`src/agents/`)

### `class ScreenwriterAgent` (`src/agents/screenwriter.py`)
Responsible for Phase 1 daily scenario scripting.
* `dream_day(self, day_index: int, weather_tuple: Tuple[str, str, str], flow_level: str) -> np.ndarray`
  Executes local Phi-4-mini inference in `<think>` mode and extracts the normalized 2048-dimensional latent vector $\mathbf{z}_{dream} \in \mathbb{R}^{2048}$.

### `class DirectorAgent` (`src/agents/director.py`)
Responsible for Phase 2 physical enforcement and diffusion synthesis.
* `synthesize_day(self, latent_vector: np.ndarray, graph_context: torch.Tensor, day_index: int) -> PhysicalTrafficArrays`
  Validates the latent vector against the `VAETCN` manifold, clamps velocity to $[20, 110]\text{ km/h}$, queries the `CSDIEngine` diffusion model, and returns ground truth velocity and flow matrices.

---

## 4. Sequential Memory Manager (`src/services/model_manager.py`)

### `class ModelManager`
Enforces sequential lazy loading and explicit garbage collection:
* `load_screenwriter() -> Llama`
* `release_screenwriter() -> None`
* `load_vae_tcn() -> VAETCN`
* `release_vae_tcn() -> None`
* `load_csdi() -> CSDIEngine`
* `release_csdi() -> None`
* `load_gatv2() -> LightweightGATv2`
* `release_gatv2() -> None`

All release methods explicitly execute:
```python
del model_instance
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
```

---

## 5. Map Providers & Parsers (`src/parsers/`)

### `class OSMMapProvider` (`src/core/map_provider.py`)
Parses `.osm` / `.osm.gz` OpenStreetMap XML feeds.
* `load_map(self, file_path: str) -> None`
  Parses nodes and highway ways.
* `snap_to_road(self, lat: float, lon: float) -> Tuple[float, float]`
  Performs Haversine perpendicular snapping to the closest valid pavement edge.
* `get_bounds(self) -> Tuple[float, float, float, float]`
  Returns `(min_lat, min_lon, max_lat, max_lon)`.

### `class SumoParser` (`src/parsers/sumo.py`)
Ingests SUMO network graphs (`.net.xml`) and translates Cartesian lane geometry to geographic coordinates.

---

## 6. Multi-Modal Generators (`src/globalf/`, `src/localf/`)

| Generator Class | Module | Method Signature | Output File |
|---|---|---|---|
| `WazeGenerator` | `src.globalf.waze_generator` | `generate(traffic_data, output_dir)` | `waze_feed_*.json` |
| `TomTomGenerator` | `src.globalf.tomtom_generator` | `generate(traffic_data, output_dir)` | `tomtom_flow_*.json` |
| `CameraGenerator` | `src.localf.camera_generator` | `generate(traffic_data, output_dir)` | `cam_*_*.json` |
| `LoopGenerator` | `src.localf.loop_generator` | `generate(traffic_data, output_dir)` | `loop_*_*.csv` |

---

<div align="center">
  <img src="assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
