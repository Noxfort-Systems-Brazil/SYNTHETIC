# 🧪 Directrices de Pruebas y Control de Calidad

Este documento detalla el entorno de pruebas, la cobertura automatizada y las estrategias de mocking determinista de **SYNTHETIC**.

⬅️ [Centro de Documentación](README.md) | 🏛️ [Arquitectura del Sistema](architecture.md) | 🧠 [IA Generativa y Física](generative_ai_and_physics.md) | ⚡ [Referencia de APIs](api_reference.md)

---

## 1. Filosofía de Calidad

SYNTHETIC cuenta con una **suite automatizada de 50 pruebas con un 100% de tasa de aprobación**:
* `test_environment.py`: Comprobación del ancla Ground Zero (Lunes 00:00:00) y cadena de Markov meteorológica.
* `test_pinn_hybrid.py`: Validación del VAE-TCN, clamping de velocidad en $[20, 110]\text{ km/h}$ y ajuste con Optuna.
* `test_map_provider.py`: Ingesta de archivos `.osm` y proyección Haversine sobre el asfalto.
* `test_generators.py`: Esquemas JSON de Waze, TomTom, Cámaras y CSV de Espiras inductivas.
* `test_translator.py`: Carga de los 6 diccionarios de idiomas e interpolación dinámica.

Para ejecutar las pruebas:
```bash
.venv/bin/python -m unittest discover -s tests
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
