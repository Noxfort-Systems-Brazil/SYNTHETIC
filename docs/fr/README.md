<div align="center">

<img src="../assets/synthetic-logo.png" alt="SYNTHETIC Logo" width="120" />

# SYNTHETIC — Suite de Documentation Technique
### Architecture Système, Modèles d'IA Générative et Générateurs Multimodaux
*Noxfort Systems — A State Of Art Company*

[![Status](https://img.shields.io/badge/Status-Actif-brightgreen?style=flat&logo=github)](https://github.com/Noxfort-Systems-Brazil/SYNTHETIC)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.0%2B-76B900?style=flat&logo=nvidia&logoColor=white)](https://nvidia.com/)

---

🌐 **Langues :** **[🇺🇸 English](../en/README.md)** • **[🇧🇷 Português (Brasil)](../pt-br/README.md)** • **[🇫🇷 Français](README.md)** • **[🇪🇸 Español](../es/README.md)** • **[🇷🇺 Русский](../ru/README.md)** • **[🇨🇳 简体中文](../zh/README.md)** • **[📚 Hub Central](../README.md)**

---

</div>

## Bienvenue dans la Documentation Technique Officielle

Ce répertoire rassemble la documentation technique complète en **Français** du moteur **SYNTHETIC** — le système d'orchestration par IA pour la synthèse de scénarios de trafic multimodal de haute fidélité développé par Noxfort Systems.

## Index des Guides Techniques

| Document | Domaine & Portée | Sujets Principaux |
|---|---|---|
| 🏛️ **[Architecture Système](architecture.md)** | Spécification d'Architecture | Pipeline en 2 phases (Rêve cognitif vs. Synthèse physique), Lazy Loading séquentiel, libération explicite de VRAM et principe SRP. |
| 🧠 **[IA Générative et Physique](generative_ai_and_physics.md)** | Formulations Neuronales | Scénariste SLM Phi-4-mini, Gardien de Physique VAE-TCN, Modèle de Diffusion CSDI et optimisation AutoML avec Optuna. |
| 📡 **[Générateurs Multimodaux](multimodal_generators.md)** | Synthèse de Capteurs | Flux JSON Waze, segments de flux TomTom, détection visuelle de Caméras ANPR/LPR et fichiers CSV de Boucles Inductives. |
| 🗺️ **[Topologie Spatiale et Climat](spatial_and_environment.md)** | Topographie et Météo | Intégration OpenStreetMap `.osm`, projection Snap-to-Road via Haversine, tenseurs spatiaux GATv2 et chaîne de Markov météo. |
| 🖥️ **[Interface Desktop et i18n](ui_and_localization.md)** | Frontend et Traduction | Interface graphique CustomTkinter, canvas interactif TkinterMapView, Singleton Translator et changement dynamique de langue. |
| ⚡ **[Référence des API](api_reference.md)** | Interfaces et Contrats | Signatures des classes pour `SimulationOrchestrator`, `EnvironmentManager`, `ModelManager`, `DirectorAgent` et générateurs. |
| 🧪 **[Directives de Tests et QA](testing.md)** | Assurance Qualité | Suite de tests automatisés (50 tests réussis), stratégies de simulation déterministe (mocking) et validation des limites physiques. |
| 🚀 **[Déploiement et Matériel](deployment_and_setup.md)** | Exploitation et Matériel | Prérequis système, environnement virtuel Python, accélération NVIDIA CUDA 12, coffre de modèles GGUF et exécution. |

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i><br/>
  <i>Systèmes de Transport Intelligents • SYNTHETIC Engine v1.0.0</i>
</div>
