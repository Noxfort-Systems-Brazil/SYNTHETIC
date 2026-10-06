# 🖥️ Interfaz Desktop y Arquitectura de Localización Dinámica (i18n)

Este documento describe la arquitectura frontend de **SYNTHETIC**, construida con CustomTkinter y TkinterMapView, junto con su motor de internacionalización en tiempo de ejecución.

⬅️ [Centro de Documentación](README.md) | 🏛️ [Arquitectura del Sistema](architecture.md) | 🗺️ [Topología Espacial](spatial_and_environment.md) | ⚡ [Referencia de APIs](api_reference.md)

---

## 1. Arquitectura Modular Frontend

La interfaz desktop está desarrollada en **CustomTkinter** y se estructura en componentes aislados (`ui/components/`): selección de mapas, activación de fuentes de datos, configuración de duración y densidad, y selector dinámico de idioma.

---

## 2. Canvas Interactivo de Mapa (`ui/map_selector.py`)

* **Encuadre Automático:** Centra la vista según los límites del archivo `.osm`.
* **Colocación de Sensores:** Pines rojos para Cámaras LPR y azules para Espiras Inductivas.
* **Control de Cupos:** Indicador en tiempo real de los sensores restantes antes de confirmar.

---

## 3. Motor de Internacionalización Dinámica (i18n)

Permite alternar idiomas en caliente **sin reiniciar el proceso Python**.
* **Singleton `Translator` (`ui/translator.py`):** Carga los diccionarios JSON en `ui/locale/` (`en`, `pt-br`, `es`, `fr`, `ru`, `zh-cn`).
* La función `SyntheticApp.update_ui_texts()` actualiza de forma síncrona todas las etiquetas, botones y ventanas emergentes.

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
