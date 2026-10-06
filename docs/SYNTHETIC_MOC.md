---
tags: [moc, map-of-content, synthetic, architecture, obsidian]
aliases: [SYNTHETIC MOC, Master Map of Content]
---

# 🗺️ SYNTHETIC — Master Map of Content (MOC)

This Map of Content organizes the entire architectural, neural, spatial, and multi-modal knowledge base of the **SYNTHETIC** ecosystem for navigation within Obsidian and documentation browsers.

---

## 🏛️ 1. Architecture & Execution Lifecycle
- [[architecture|System Blueprint & Two-Phase Lifecycle]]
  - *Phase 1: The "Dreaming" Phase* (SLM Phi-4 Screenwriter Agent)
  - *Phase 2: Physics & Synthesis Phase* (Director Agent, VAE-TCN, CSDI, GATv2)
  - *Sequential Lazy Loading & Memory Purging* (`gc.collect` pattern)
  - *Maestro Orchestrator* (`src/core/simulation_logic.py`)

## 🧠 2. Generative AI, Physics Guardian & Diffusion
- [[generative_ai_and_physics|Generative AI & Physics Framework]]
  - *Phi-4-mini Screenwriter:* Deep reasoning `<think>` tokens & 2048-dim latent vector
  - *VAE-TCN Physics Guardian:* Traffic manifold validation & physical clamping (20–110 km/h)
  - *Hydrodynamic Godunov Solver:* Exact numerical Riemann flux solver for LWR conservation laws
  - *Greenshields Model & Shockwaves:* Rankine-Hugoniot jump condition (\(u_s = \Delta q / \Delta \rho\))
  - *ST-GATv2 Architecture:* Spatio-temporal dynamic attention with continuous Time2Vec & tidal flow bias
  - *TrafficDeepONet & PINN:* Neural Operator prior and physics-informed residual loss
  - *CSDI Engine:* Conditional Score-based Diffusion Models for continuous time-series synthesis
  - *Optuna HyperTuner:* JIT automated hyperparameter tuning

## 📡 3. Multi-Modal Generators & Sensor Corruption
- [[multimodal_generators|Multi-Modal Generators & Corruption]]
  - *Waze Generator:* Crowdsourced GPS alerts, jams, and delay events (`JSON`)
  - *TomTom Generator:* Commercial flow segments, FRC classifications, and speed models (`JSON`)
  - *Camera Generator:* Visual LPR/ANPR recognition, synthetic license plates (`JSON`)
  - *Inductive Loop Generator:* Electromagnetic vehicle counts and lane occupancy (`CSV`)
  - *Perception Corruption Layer:* 3–15% sensor dropouts, gap bursts, and Gaussian noise

## 🗺️ 4. Spatial Topology & Meteorological Physics
- [[spatial_and_environment|Spatial Topology & Environment Engine]]
  - *OSMMapProvider:* XML parsing, bounding boxes, and way filtering
  - *Snap-to-Road Mechanism:* Haversine mathematical pavement projection
  - *LightweightGATv2:* Graph Attention network extracting intersection node/edge tensors
  - *Markov Weather Machine:* Realistic state transitions via `config/weather_rules.json`
  - *Ground Zero Temporal Sync:* Standardization to Monday 00:00:00

## 🖥️ 5. Graphical Interface & Localization
- [[ui_and_localization|Desktop UI & Dynamic i18n]]
  - *CustomTkinter Architecture:* Modern dark/light interface (`ui/gui.py`)
  - *TkinterMapView:* Interactive street-level canvas for sensor placement
  - *Translator Singleton:* Thread-safe runtime i18n hot-swapping
  - *Supported Locales:* English, Português, Français, Español, Русский, 简体中文

## ⚡ 6. API Reference & Interfaces
- [[api_reference|Core API & Service Architecture]]
  - `SimulationOrchestrator`
  - `EnvironmentManager`
  - `ModelManager`
  - `DirectorAgent` & `ScreenwriterAgent`
  - `OSMMapProvider` & SUMO Parser

## 🧪 7. Quality Assurance & Validation
- [[testing|Testing Suite & Benchmarks]]
  - 99 Unit & Regression Tests in `tests/` across 18 test suites (86% coverage)
  - Hydrodynamic Godunov & ST-GATv2 verification suites
  - Deterministic Mocking for neural and physical components
  - Ground Zero temporal assertions & PINN hybrid physics tests

## 🚀 8. Deployment & Hardware Acceleration
- [[deployment_and_setup|Deployment, CUDA & Environment]]
  - NVIDIA CUDA 12 & TensorCore configuration
  - PyTorch & PyTorch Geometric installation
  - Local Phi-4 GGUF vault setup (`src/models/vault/`)

---

<div align="center">
  <img src="assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
