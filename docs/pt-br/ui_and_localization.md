# 🖥️ Interface Desktop e Arquitetura de Internacionalização (i18n)

Este documento descreve a arquitetura da interface gráfica do **SYNTHETIC**, construída em CustomTkinter e TkinterMapView, abordando o isolamento de componentes, a concorrência assíncrona por threads e o motor de troca dinâmica de idiomas em tempo de execução.

⬅️ [Central de Documentação](README.md) | 🏛️ [Arquitetura do Sistema](architecture.md) | 🗺️ [Topologia Espacial](spatial_and_environment.md) | ⚡ [Referência de APIs](api_reference.md)

---

## 1. Arquitetura Modular da Interface Gráfica

A interface desktop é baseada em **CustomTkinter** com suporte a alta densidade de pixels (High-DPI) e temas escuro/claro. A organização segue separação estrita de componentes:
* `ui/components/map_section.py`: Carregamento do arquivo de malha viária e acionamento da janela de mapa.
* `ui/components/sources_section.py`: Seleção dos tipos de sensores (Waze, TomTom, Câmeras, Laços).
* `ui/components/settings_section.py`: Configurações de duração (dias), intervalo (minutos) e densidade de tráfego.
* `ui/components/problems_section.py`: Percentuais de falha de sensores e ruído físico.
* `ui/components/language_section.py`: Seletor de idioma dinâmico.

---

## 2. Canvas Interativo de Mapa (`ui/map_selector.py`)

A classe **`MapSelectorWindow`** incorpora a biblioteca **`tkintermapview`**:
1. **Centralização Automática:** Enquadra o mapa com base nos limites geográficos do arquivo `.osm`.
2. **Posicionamento Visual de Sensores:** Permite ao usuário clicar diretamente nas ruas:
   - Marcadores Vermelhos: Câmeras ópticas LPR/ANPR.
   - Marcadores Azuis: Laços indutivos eletromagnéticos.
3. **Controle de Cotas em Tempo Real:** Exibe um contador dinâmico de sensores restantes a serem posicionados antes de liberar a confirmação.

---

## 3. Concorrência Assíncrona e Telemetria

Para evitar que a interface gráfica congele durante o processamento pesado dos modelos de IA:
* O pipeline de geração executa em uma thread em background (`threading.Thread`).
* Eventos de progresso da simulação (sonho do SLM, difusão diária CSDI) são encaminhados para a fila principal da interface via chamadas seguras `root.after(0, ...)`.

---

## 4. Motor de Internacionalização Dinâmica (i18n)

O sistema de localização permite alternar o idioma de toda a aplicação **sem reiniciar o processo Python**.

### 4.1 Padrão Singleton: `Translator` (`ui/translator.py`)
```python
from ui.translator import translator

# Busca direta de chave traduzida
titulo = translator.t("app_title")

# Busca formatada com interpolação dinâmica
msg = translator.t("cameras_remaining", count=3)
```

### 4.2 Dicionários de Idiomas (`ui/locale/`)
* `pt-br.json` — Português (Brasil)
* `en.json` — Inglês (Canônico)
* `fr.json` — Francês
* `es.json` — Espanhol
* `ru.json` — Russo
* `zh-cn.json` — Mandarim Simplificado

Ao selecionar um novo idioma no combobox, a interface aciona `SyntheticApp.update_ui_texts()`, atualizando instantaneamente todas as legendas, botões e instruções ativas.

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
