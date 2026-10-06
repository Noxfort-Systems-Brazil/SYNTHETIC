# ⚡ Référence des API et Architecture des Services

Ce document fournit la référence développeur des principales classes Python, orchestrateurs et contrats de données du moteur **SYNTHETIC**.

⬅️ [Hub de Documentation](README.md) | 🏛️ [Architecture Système](architecture.md) | 🧠 [IA Générative et Physique](generative_ai_and_physics.md) | 🧪 [Tests et QA](testing.md)

---

## 1. Orchestrateur Central (`src/core/simulation_logic.py`)

### `class SimulationOrchestrator`
* `__init__(self, config: SimulationConfig, progress_callback: Optional[Callable] = None)` : Initialise la configuration et les canaux de rappel télémétriques.
* `run(self) -> GenerationReport` : Coordonne la validation, la Phase 1 (Rêve cognitif), le nettoyage VRAM, la Phase 2 (Synthèse par diffusion) et l'injection de bruit.
* `cancel(self) -> None` : Interrompt le thread d'exécution en toute sécurité et vide les tenseurs GPU.

---

## 2. Physique Environnementale (`src/core/environment.py`)

### `class EnvironmentManager`
* `get_next_monday_midnight(base_date: Optional[datetime] = None) -> datetime` : Calcule le point d'ancrage temporel Ground Zero (Lundi 00:00:00).
* `get_dynamic_weather(self, current_weather: Optional[str] = None) -> Tuple[str, str, str]` : Échantillonne la chaîne de Markov atmosphérique.

---

## 3. Gestionnaire Séquentiel de Modèles (`src/services/model_manager.py`)

Garantit le chargement unitaire et la destruction immédiate des modèles d'IA :
* `load_screenwriter() / release_screenwriter()`
* `load_vae_tcn() / release_vae_tcn()`
* `load_csdi() / release_csdi()`
* `load_gatv2() / release_gatv2()`

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
