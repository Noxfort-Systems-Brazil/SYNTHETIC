# 🖥️ Interface Graphique et Architecture de Localisation Dynamique (i18n)

Ce document décrit l'architecture frontend de **SYNTHETIC**, construite avec CustomTkinter et TkinterMapView, ainsi que son moteur de changement dynamique de langue en cours d'exécution.

⬅️ [Hub de Documentation](README.md) | 🏛️ [Architecture Système](architecture.md) | 🗺️ [Topologie Spatiale](spatial_and_environment.md) | ⚡ [Référence des API](api_reference.md)

---

## 1. Architecture Modulaire de l'Interface

L'interface de SYNTHETIC repose sur **CustomTkinter** et s'articule autour de composants découplés :
* `ui/components/map_section.py` : Sélection de carte routière et ouverture du canvas.
* `ui/components/sources_section.py` : Activation des capteurs (Waze, TomTom, Caméras, Boucles).
* `ui/components/settings_section.py` : Durée, pas d'échantillonnage et densité de flux.
* `ui/components/problems_section.py` : Taux de dropouts et de bruit des capteurs.
* `ui/components/language_section.py` : Menu déroulant de changement d'idiome.

---

## 2. Canvas Cartographique Interactif (`ui/map_selector.py`)

La fenêtre **`MapSelectorWindow`** intègre **`tkintermapview`** :
1. **Centrage Automatique :** Ajuste le zoom et la vue sur la boîte englobante du fichier `.osm`.
2. **Placement Interactif des Capteurs :** Les utilisateurs cliquent sur la chaussée :
   - Épingles Rouges : Caméras vidéo LPR/ANPR.
   - Épingles Bleues : Boucles inductives électromagnétiques.
3. **Comptage en Temps Réel :** Affichage interactif du quota de capteurs restants.

---

## 3. Moteur d'Internationalisation Dynamique (i18n)

Le système de traduction permet de changer de langue **à chaud sans redémarrer le processus Python**.

### 3.1 Singleton `Translator` (`ui/translator.py`)
```python
from ui.translator import translator

# Récupération directe de chaîne
titre = translator.t("app_title")

# Récupération avec interpolation de variables
texte = translator.t("cameras_remaining", count=2)
```

### 3.2 Dictionnaires Disponibles (`ui/locale/`)
* `en.json` (Anglais par défaut), `pt-br.json` (Portugais), `fr.json` (Français), `es.json` (Espagnol), `ru.json` (Russe), `zh-cn.json` (Chinois simplifié).

Lors d'un changement de sélection, `SyntheticApp.update_ui_texts()` est invoqué, réécrivant immédiatement les libellés de l'ensemble des composants actifs.

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
