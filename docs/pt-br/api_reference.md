# ⚡ Referência de APIs e Arquitetura de Serviços

Este documento fornece a referência técnica para desenvolvedores das principais classes, serviços, orquestradores e contratos de dados do **SYNTHETIC**.

⬅️ [Central de Documentação](README.md) | 🏛️ [Arquitetura do Sistema](architecture.md) | 🧠 [IA Generativa e Física](generative_ai_and_physics.md) | 🧪 [Testes e QA](testing.md)

---

## 1. Orquestrador Principal (`src/core/simulation_logic.py`)

### `class SimulationOrchestrator`
Gerencia o fluxo de trabalho em duas fases, a telemetria assíncrona e a escrita em disco.
* `__init__(self, config: SimulationConfig, progress_callback: Optional[Callable] = None)`: Inicializa parâmetros e funções de retorno para a interface.
* `run(self) -> GenerationReport`: Executa a validação de dependências, leitura de malha viária, Fase 1 (Sonho cognitivo), liberação de VRAM, Fase 2 (Síntese e difusão) e exportação dos feeds multimodais.
* `cancel(self) -> None`: Interrompe a geração com segurança e limpa tensores em GPU.

---

## 2. Física e Ambiente Meteorológico (`src/core/environment.py`)

### `class EnvironmentManager`
* `get_next_monday_midnight(base_date: Optional[datetime] = None) -> datetime`: Retorna a meia-noite da próxima segunda-feira como ponto de ancoragem temporal padrão.
* `get_dynamic_weather(self, current_weather: Optional[str] = None) -> Tuple[str, str, str]`: Amostra a matriz de transição de Markov em `config/weather_rules.json`, retornando a tupla `(condição, intensidade, característica)`.

---

## 3. Agentes Cognitivos e Executivos (`src/agents/`)

### `class ScreenwriterAgent` (`src/agents/screenwriter.py`)
* `dream_day(self, day_index: int, weather_tuple: Tuple[str, str, str], flow_level: str) -> np.ndarray`: Executa inferência local no modelo Phi-4-mini em modo `<think>` e extrai o vetor latente contínuo de 2048 dimensões.

### `class DirectorAgent` (`src/agents/director.py`)
* `synthesize_day(self, latent_vector: np.ndarray, graph_context: torch.Tensor, day_index: int) -> PhysicalTrafficArrays`: Valida o vetor no VAE-TCN, impõe limites físicos de velocidade $[20, 110]\text{ km/h}$, resolve a difusão no CSDI e retorna as matrizes de fluxo e velocidade.

---

## 4. Gerenciador Sequencial de Modelos (`src/services/model_manager.py`)

### `class ModelManager`
Garante carregamento sob demanda e purga imediata de memória de vídeo:
* `load_screenwriter() / release_screenwriter()`
* `load_vae_tcn() / release_vae_tcn()`
* `load_csdi() / release_csdi()`
* `load_gatv2() / release_gatv2()`

Todos os métodos de liberação executam explicitamente:
```python
del model_instance
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
```

---

## 5. Provedores de Malha e Parsers (`src/parsers/`)

* `OSMMapProvider` (`src/core/map_provider.py`): Leitura de arquivos `.osm`, cálculo de caixas delimitadoras e projeção de nós viários via Haversine.
* `SumoParser` (`src/parsers/sumo.py`): Conversão de geometria cartesiana do SUMO (`.net.xml`) para coordenadas geodésicas globais.

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
