# SYNTHETIC Architecture Overview

The `SYNTHETIC` project is an AI-orchestrated engine designed for multi-modal traffic scenario synthesis. It employs a multi-agent, dynamically memory-managed architecture to generate physically coherent and contextually rich traffic data (e.g., vehicle flow and speed) based on natural language constraints (weather, day of the week, UI-defined flow levels).

This architecture strictly enforces **Sequential Resource Release** and **Lazy Loading**, ensuring that the system can run on consumer-grade hardware with limited GPU memory. Multiple heavy neural networks (LLM, VAE-TCN, CSDI) are utilized, but they are guaranteed to never coexist in memory.

---

## 🏗️ High-Level System Workflow

The generation pipeline is split into two distinct phases to optimize memory usage:

### Phase 1: The "Dreaming" Phase (LLM Active)
In this phase, the **Qwen LLM (Screenwriter Agent)** is loaded into memory (~1.7GB). It processes inputs based on dynamic weather and daily constraints to "dream" realistic daily traffic scenarios, converting its internal reasoning into high-dimensional latent vectors. 
*   **Sequential Action:** Once all scripts for the entire simulation duration are generated, the LLM is explicitly purged from memory (`del self.llm` + `gc.collect()`), freeing resources for Phase 2.

### Phase 2: The "Physics & Synthesis" Phase (Director Active)
This phase iterates through each pre-generated daily script. The **Director Agent** orchestrates two specialized neural networks in a precise sequence:
1.  **VAE-TCN (Physics Guardian):** Loaded lazily. Validates the LLM's dream vector against a learned continuous manifold of valid traffic physics. If a significant semantic shift is detected, an **AutoML Tuner (Optuna)** rebuilds the Guardian. Once the vector is cleaned and parameters extracted, the VAE-TCN is purged from memory.
2.  **CSDI Engine (Generator):** Loaded lazily. A Conditional Score-based Diffusion model that takes the cleaned vector and generates the actual time-series physics data. To maintain temporal coherence across days, a `seed_tail` (the last 120 steps of the previous day) is injected into the initial noise tensor. Once generation is complete, the CSDI engine is purged.

---

## 🧠 Core Components & Agents

### 1. `SimulationOrchestrator` (The Maestro)
**File:** `core/simulation_logic.py`
*   **Role:** The main controller of the ecosystem.
*   **Responsibilities:** 
    *   Generates dynamic weather streams.
    *   Manages the time loop (Monday midnight to end date).
    *   Executes the strict Two-Phase pipeline (Phase 1: Dreaming -> Phase 2: Processing).
    *   Handles sensor fault injection (anomalies and data gaps).
    *   Triggers memory cleanup between daily iterations.

### 2. `ScreenwriterAgent` & `QwenEngine`
**Files:** `agents/screenwriter.py`, `models/qwen_engine.py`
*   **Role:** The creative engine.
*   **Responsibilities:**
    *   Takes raw constraints (e.g., "Chaotic stormy Monday morning").
    *   Uses a **Thinking Mode** (`<think>...</think>`) to logically reason about traffic density and physical limits internally.
    *   Converts these thoughts into a 2048-dimensional **Latent Vector** via embeddings.
    *   Provides a safe `release()` method to unload the GGUF model from VRAM/RAM.

### 3. `DirectorAgent`
**File:** `agents/director.py`
*   **Role:** The tactical orchestrator and memory manager for Phase 2.
*   **Responsibilities:**
    *   **Temporal Inertia:** Blends the new day's vector with 30% of the previous day's vector to prevent strobe-light effects (e.g., sudden jumps from Summer to Winter scenarios).
    *   **Sequential Lazy Loading:** Ensures the `VAETCN` and `CSDI` models are only instantiated when strictly necessary and destroyed immediately after their specific sub-task.
    *   **Inter-Day Context:** Manages the `last_day_tail` tensor, keeping it on the CPU across days to act as a warm-start seed for the CSDI diffusion process.

### 4. `VAETCN` (Physics Guardian)
**File:** `models/vae_tcn.py`
*   **Role:** The reality check.
*   **Mechanism:** A Variational Autoencoder hooked to a Temporal Convolutional Network. It decodes the SLM's dream into a physical projection, then re-encodes it to find the nearest valid mathematical point on the learned traffic manifold. It acts as an anomaly corrector.

### 5. `CSDIEngine` (The Generator)
**File:** `models/csdi_engine.py`
*   **Role:** The time-series synthesist.
*   **Mechanism:** Deep conditional score-based diffusion model. Replaces legacy TimeGANs. It generates high-fidelity sequences of `vehicle_flow` and `current_speed` from pure noise, conditioned on the validated vector. It utilizes a `seed_tail` for smooth day-to-day transitions.

### 6. `HyperTuner`
**File:** `optimizer/tuner.py`
*   **Role:** The AutoML optimizer.
*   **Mechanism:** Uses Optuna with a MedianPruner. Triggered by the Director only when a "Semantic Shift" occurs (e.g., weather drastically changes). It runs trials to find the best TCN-VAE architecture for the new scenario. It includes robust fallbacks to safe default parameters if all optimization trials are pruned.

---

## 💾 Memory Lifecycle Diagram

```mermaid
graph TD
    A[Start Simulation] --> B(Load Qwen LLM)
    
    subgraph PHASE 1: DREAMING
        B --> C{More Days?}
        C -- Yes --> D[Screenwriter creates script & vector]
        D --> C
    end
    
    C -- No --> E(Release Qwen LLM)
    E --> F[Start Daily Processing]
    
    subgraph PHASE 2: PROCESSING (Loop per Day)
        F --> G(Load VAE-TCN)
        G --> H[Validate Vector & Extract Params]
        H --> I(Release VAE-TCN)
        
        I --> J(Load CSDI)
        J --> K[Generate Time-Series Data]
        K --> L[Save tail context to CPU]
        L --> M(Release CSDI)
        M --> N[Apply Noise/Anomalies]
        N --> O[Write Output Files]
    end
    
    O --> P{Next Day?}
    P -- Yes --> G
    P -- No --> Q([End Simulation])
```

## 🛠️ Design Principles Adhered To
*   **Single Responsibility Principle (SRP):** Agents are thin orchestrators. Neural logic, parsing, and optimization are separated into `models/`, `core/`, and `optimizer/`.
*   **Dependency Inversion Principle (DIP):** The orchestrator relies on the `IDataGenerator` interface for outputting files, allowing agnostic integration with Waze, local storage, or databases.
*   **Resource Efficiency over Speed:** By intentionally trading slightly slower execution times (due to model loading/unloading) for massive reductions in peak VRAM consumption, the architecture ensures stability on edge devices and consumer hardware.
