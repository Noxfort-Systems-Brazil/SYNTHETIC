<div align="center">

<img src="../assets/synthetic-logo.png" alt="SYNTHETIC Logo" width="120" />

# SYNTHETIC — Suíte de Documentação Técnica
### Arquitetura de Sistemas, Modelos de IA Generativa e Geradores Multimodais
*Noxfort Systems — A State Of Art Company*

[![Status](https://img.shields.io/badge/Status-Ativo-brightgreen?style=flat&logo=github)](https://github.com/Noxfort-Systems-Brazil/SYNTHETIC)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.0%2B-76B900?style=flat&logo=nvidia&logoColor=white)](https://nvidia.com/)
[![Testes](https://img.shields.io/badge/Testes-50%20Aprovados-brightgreen?style=flat&logo=pytest)](testing.md)

---

🌐 **Idiomas:** **[🇺🇸 English](../en/README.md)** • **[🇧🇷 Português (Brasil)](README.md)** • **[🇫🇷 Français](../fr/README.md)** • **[🇪🇸 Español](../es/README.md)** • **[🇷🇺 Русский](../ru/README.md)** • **[🇨🇳 简体中文](../zh/README.md)** • **[📚 Central de Documentação](../README.md)**

---

</div>

## Bem-vindo à Documentação Técnica Oficial

Este diretório reúne toda a suíte de documentação técnica em **Português do Brasil** do ecossistema **SYNTHETIC** — o motor corporativo de síntese de cenários de tráfego multimodal orquestrado por Inteligência Artificial da Noxfort Systems.

## Índice de Guias Especializados

| Documento | Tema & Escopo | Principais Tópicos |
|---|---|---|
| 🏛️ **[Arquitetura do Sistema](architecture.md)** | Especificação de Arquitetura | Pipeline em 2 fases (Dreaming vs. Síntese Física), Lazy Loading sequencial, liberação explícita de VRAM e isolamento por SRP. |
| 🧠 **[IA Generativa e Física](generative_ai_and_physics.md)** | Formulações Neurais | Roteirista Phi-4-mini SLM, Guardião de Física VAE-TCN, Difusão Condicional CSDI e ajuste AutoML Just-In-Time com Optuna. |
| 📡 **[Geradores Multimodais](multimodal_generators.md)** | Síntese de Sensores | Feeds JSON do Waze, segmentos de fluxo TomTom, detecções visuais de Câmeras ANPR/LPR e CSVs de Laços Indutivos. |
| 🗺️ **[Topologia Espacial e Clima](spatial_and_environment.md)** | Topografia e Clima | Ingestão OpenStreetMap `.osm`, projeção Snap-to-Road via Haversine, grafos GATv2 e motor meteorológico de Markov. |
| 🖥️ **[Interface Desktop e i18n](ui_and_localization.md)** | Frontend e Internacionalização | Interface gráfica CustomTkinter, canvas interativo TkinterMapView, padrão Singleton no Translator e hot-swap dinâmico de idiomas. |
| ⚡ **[Referência de APIs](api_reference.md)** | Interfaces e Contratos | Assinaturas de classes para `SimulationOrchestrator`, `EnvironmentManager`, `ModelManager`, `DirectorAgent` e geradores. |
| 🧪 **[Diretrizes de Testes e QA](testing.md)** | Garantia de Qualidade | Suíte automatizada com 50 testes unitários aprovados, estratégias determinísticas de mocking e validação de invariantes físicos. |
| 🚀 **[Instalação e Hardware](deployment_and_setup.md)** | Operações e Infraestrutura | Pré-requisitos de sistema, ambiente virtual Python, aceleração NVIDIA CUDA 12, provisionamento do vault GGUF e execução. |

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i><br/>
  <i>Engenharia de Mobilidade Inteligente • SYNTHETIC Engine v1.0.0</i>
</div>
