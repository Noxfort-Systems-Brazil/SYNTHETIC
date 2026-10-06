# 🧪 Тестирование и обеспечение качества

В документе представлены сведения о наборе автоматизированных тестов, стратегиях мокирования и проверке физических инвариантов в **SYNTHETIC**.

⬅️ [Главный Хаб](README.md) | 🏛️ [Архитектура системы](architecture.md) | 🧠 [Генеративный ИИ и физика](generative_ai_and_physics.md) | ⚡ [Справочник API](api_reference.md)

---

## 1. Обеспечение качества

Система содержит **набор из 50 модульных тестов со 100% успешным прохождением**:
* `test_environment.py`: Проверка расчетной точки Ground Zero (Понедельник 00:00:00) и марковской матрицы вероятностей.
* `test_pinn_hybrid.py`: Валидация многообразия VAE-TCN, ограничение скорости $[20, 110]\text{ км/ч}$ и запуск Optuna.
* `test_map_provider.py`: Чтение `.osm` и проекция координат на дорогу.
* `test_generators.py`: Форматы Waze, TomTom, Камер и Индуктивных петель.
* `test_translator.py`: Проверка загрузки всех 6 словарей локализации.

Запуск набора тестов:
```bash
.venv/bin/python -m unittest discover -s tests
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
