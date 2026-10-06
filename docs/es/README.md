<div align="center">

<img src="../assets/synthetic-logo.png" alt="SYNTHETIC Logo" width="120" />

# SYNTHETIC — Suite de Documentación Técnica
### Arquitectura del Sistema, Modelos de IA Generativa y Generadores Multimodales
*Noxfort Systems — A State Of Art Company*

[![Status](https://img.shields.io/badge/Status-Activo-brightgreen?style=flat&logo=github)](https://github.com/Noxfort-Systems-Brazil/SYNTHETIC)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.0%2B-76B900?style=flat&logo=nvidia&logoColor=white)](https://nvidia.com/)

---

🌐 **Idiomas:** **[🇺🇸 English](../en/README.md)** • **[🇧🇷 Português (Brasil)](../pt-br/README.md)** • **[🇫🇷 Français](../fr/README.md)** • **[🇪🇸 Español](README.md)** • **[🇷🇺 Русский](../ru/README.md)** • **[🇨🇳 简体中文](../zh/README.md)** • **[📚 Centro de Documentación](../README.md)**

---

</div>

## Bienvenido a la Documentación Técnica Oficial

Este directorio reúne la suite completa de documentación técnica en **Español** del ecosistema **SYNTHETIC** — el motor corporativo de síntesis de escenarios de tráfico multimodal orquestado por Inteligencia Artificial de Noxfort Systems.

## Índice de Guías Técnicas Especializadas

| Documento | Enfoque & Alcance | Temas Principales |
|---|---|---|
| 🏛️ **[Arquitectura del Sistema](architecture.md)** | Especificación de Arquitectura | Pipeline en 2 fases (Dreaming vs. Síntesis Física), Lazy Loading secuencial, liberación explícita de VRAM y principio SRP. |
| 🧠 **[IA Generativa y Física](generative_ai_and_physics.md)** | Formulaciones Neuronales | Guionista SLM Phi-4-mini, Guardián de Física VAE-TCN, Difusión Condicional CSDI y ajuste AutoML con Optuna. |
| 📡 **[Generadores Multimodales](multimodal_generators.md)** | Síntesis de Sensores | Feeds JSON de Waze, segmentos de flujo TomTom, detección visual de Cámaras ANPR/LPR y CSVs de Espiras Inductivas. |
| 🗺️ **[Topología Espacial y Clima](spatial_and_environment.md)** | Topografía y Meteorología | Ingesta de OpenStreetMap `.osm`, proyección Snap-to-Road mediante Haversine, grafos GATv2 y motor de Markov. |
| 🖥️ **[Interfaz Desktop e i18n](ui_and_localization.md)** | Frontend y Localización | Interfaz gráfica CustomTkinter, canvas interactivo TkinterMapView, patrón Singleton en Translator y hot-swap de idiomas. |
| ⚡ **[Referencia de APIs](api_reference.md)** | Interfaces y Contratos | Firmas de clases para `SimulationOrchestrator`, `EnvironmentManager`, `ModelManager`, `DirectorAgent` y generadores. |
| 🧪 **[Directrices de Pruebas y QA](testing.md)** | Control de Calidad | Suite automatizada con 50 pruebas unitarias superadas, estrategias deterministas de mocking y límites físicos. |
| 🚀 **[Instalación y Hardware](deployment_and_setup.md)** | Operaciones e Infraestructura | Requisitos del sistema, entorno virtual Python, aceleración NVIDIA CUDA 12, provisión del vault GGUF y ejecución. |

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i><br/>
  <i>Sistemas Inteligentes de Transporte • SYNTHETIC Engine v1.0.0</i>
</div>
