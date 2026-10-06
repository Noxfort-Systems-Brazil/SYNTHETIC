# 🧪 Directives de Tests et Assurance Qualité

Ce document décrit le banc d'essais, les suites de tests automatisés et les stratégies de simulation déterministe (mocking) de **SYNTHETIC**.

⬅️ [Hub de Documentation](README.md) | 🏛️ [Architecture Système](architecture.md) | 🧠 [IA Générative et Physique](generative_ai_and_physics.md) | ⚡ [Référence des API](api_reference.md)

---

## 1. Philosophie d'Assurance Qualité

SYNTHETIC combine des modèles neuronaux profonds et des règles de sécurité strictes. Pour garantir une stabilité absolue, le système dispose d'une **suite de 50 tests automatisés avec un taux de réussite de 100%**.

* `test_environment.py` : Calculs temporels au Ground Zero et chaîne de Markov météo.
* `test_pinn_hybrid.py` : Validation de variété VAE-TCN, verrouillage de vitesse $[20, 110]\text{ km/h}$ et retuning Optuna.
* `test_map_provider.py` : Ingestion des cartes `.osm` et projection Snap-to-Road via Haversine.
* `test_generators.py` : Schémas JSON Waze, TomTom, Caméras et CSV Boucles inductives.
* `test_translator.py` : Chargement des 6 fichiers de langues et interpolation dynamique.

Pour exécuter l'ensemble des tests :
```bash
.venv/bin/python -m unittest discover -s tests
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
