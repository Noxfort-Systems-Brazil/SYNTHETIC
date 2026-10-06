<div align="center">

<img src="../assets/synthetic-logo.png" alt="SYNTHETIC Logo" width="120" />

# SYNTHETIC — Комплект технической документации
### Архитектура системы, генеративные модели ИИ и мультимодальные генераторы
*Noxfort Systems — A State Of Art Company*

[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat&logo=github)](https://github.com/Noxfort-Systems-Brazil/SYNTHETIC)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.0%2B-76B900?style=flat&logo=nvidia&logoColor=white)](https://nvidia.com/)

---

🌐 **Языки:** **[🇺🇸 English](../en/README.md)** • **[🇧🇷 Português (Brasil)](../pt-br/README.md)** • **[🇫🇷 Français](../fr/README.md)** • **[🇪🇸 Español](../es/README.md)** • **[🇷🇺 Русский](README.md)** • **[🇨🇳 简体中文](../zh/README.md)** • **[📚 Главный Хаб](../README.md)**

---

</div>

## Добро пожаловать в официальную техническую документацию

В данном каталоге собрана полная техническая документация на **русском языке** для системы **SYNTHETIC** — корпоративного движка синтеза мультимодальных сценариев дорожного движения на базе искусственного интеллекта от компании Noxfort Systems.

## Специализированные технические руководства

| Документ | Область и масштаб | Основные темы |
|---|---|---|
| 🏛️ **[Архитектура системы](architecture.md)** | Спецификация архитектуры | Двухфазный конвейер (Dreaming vs. Физический синтез), последовательная ленивая загрузка, очистка VRAM и SRP. |
| 🧠 **[Генеративный ИИ и физика](generative_ai_and_physics.md)** | Нейросетевые формулировки | Сценарист SLM Phi-4-mini, физический страж VAE-TCN, диффузионная модель CSDI и автонастройка гиперпараметров Optuna. |
| 📡 **[Мультимодальные генераторы](multimodal_generators.md)** | Синтез данных датчиков | Потоки Waze JSON, сегменты скорости TomTom, распознавание номеров камерами ANPR/LPR и CSV индуктивных петель. |
| 🗺️ **[Пространство и среда](spatial_and_environment.md)** | Топология и погода | Обработка OpenStreetMap `.osm`, привязка к дорожному полотну через формулу гаверсинусов, графовая сеть GATv2 и цепи Маркова. |
| 🖥️ **[Интерфейс и локализация](ui_and_localization.md)** | Графический интерфейс и i18n | Архитектура CustomTkinter, интерактивная карта TkinterMapView, синглтон Translator и горячая смена языка. |
| ⚡ **[Справочник API](api_reference.md)** | Интерфейсы и контракты | Сигнатуры классов для `SimulationOrchestrator`, `EnvironmentManager`, `ModelManager`, `DirectorAgent` и генераторов. |
| 🧪 **[Тестирование и QA](testing.md)** | Контроль качества | Автоматизированный набор из 50 успешно пройденных модульных тестов, детерминированные моки и физические границы. |
| 🚀 **[Развертывание и оборудование](deployment_and_setup.md)** | Эксплуатация и окружение | Системные требования, виртуальное окружение Python, ускорение NVIDIA CUDA 12, хранилище моделей GGUF и запуск. |

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i><br/>
  <i>Интеллектуальные транспортные системы • SYNTHETIC Engine v1.0.0</i>
</div>
