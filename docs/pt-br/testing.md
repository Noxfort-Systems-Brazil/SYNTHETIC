# 🧪 Diretrizes de Testes, Cobertura e Garantia de Qualidade

Este documento detalha o ambiente de testes, a cobertura automatizada (86%), as estratégias de simulação determinística (mocking), a execução headless da interface gráfica e a validação de invariantes físicos do **SYNTHETIC**.

⬅️ [Central de Documentação](README.md) | 🏛️ [Arquitetura do Sistema](architecture.md) | 🧠 [IA Generativa e Física](generative_ai_and_physics.md) | 🔄 [Esteira de CI/CD](ci_cd.md) | ⚡ [Referência de APIs](api_reference.md)

---

## 1. Filosofia de Garantia de Qualidade

O SYNTHETIC lida simultaneamente com redes neurais profundas estocásticas, modelos físicos acoplados, resolvedores numéricos de EDPs hidrodinâmicas e uma interface gráfica desktop interativa. Para assegurar integridade numérica absoluta, estabilidade da UI e impedir regressões, o sistema mantém uma **suíte de testes automatizados com 100% de aprovação (99 testes automatizados) e 86% de cobertura de código**.

```text
============================= VISÃO GERAL DA SUÍTE =============================
Diretório:          tests/
Ferramentas:        pytest / unittest / coverage
Total de Testes:    99 Aprovados (0 Falhas, 0 Erros)
Cobertura Global:   86% das Declarações Cobertas (3.236 / 3.765 stmts)
Tempo de Execução:  ~16.3 segundos
Taxa de Sucesso:    100%
================================================================================
```

---

## 2. Cobertura da Suíte de Testes (`tests/`)

A tabela abaixo descreve as 18 suítes de teste disponíveis no diretório `tests/`:

| Camada | Arquivo de Teste | Escopo Principal | Funcionalidades Validadas |
|---|---|---|---|
| **Interface / UI** | `test_ui_views.py` | Telas e Widgets | Execução headless das 7 seções `ttk.LabelFrame`, fachada `MainView`, colocação de sensores no `MapSelectorWindow` e ciclo de vida do `DataGeneratorApp`. |
| **Interface / UI** | `test_ui_components.py` | Builders e Auxiliares | `SimulationConfigBuilder`, isolamento modal com `MockDialogService` e mock de traduções. |
| **Interface / UI** | `test_translator.py` | Internacionalização (i18n) | Carregamento dos 6 dicionários de idiomas (`en`, `pt-br`, `fr`, `es`, `ru`, `zh-cn`) e interpolação dinâmica. |
| **Cognitiva / IA** | `test_screenwriter_and_slm.py` | Roteirista e SLM | Mapeamento macro de cidades, persistência de clima, limpeza de tags `<think>` e vetor latente de 2048 dimensões. |
| **Grafos Neurais** | `test_gatv2.py` | Redes GATv2 | Convoluções `GATv2Conv`, pooling global e extração de contexto topológico com fallback de mapa vazio. |
| **Grafos Neurais** | `test_st_gatv2.py` | Atenção Espaço-Temporal | Atenção dinâmica ST-GATv2, embeddings periódicos contínuos Time2Vec, passagem de mensagens por arestas e viés direcional de maré pendular. |
| **Física Hidrodinâmica**| `test_physics_godunov.py`| EDPs e Leis de Conservação | Resolvedor de Riemann Godunov para a EDP LWR, diagrama fundamental de Greenshields, choque Rankine-Hugoniot, semáforos atuados e queda de capacidade por incidentes. |
| **Física / AutoML** | `test_pinn_hybrid.py` | Física Neural e Tuning | Projeção no manifold do VAE-TCN, penalidade de perda de Greenshields/jerk e otimizador Optuna. |
| **Otimização** | `test_optimizer_callbacks.py` | Callbacks de Treino | `EarlyStopping`, parada antecipada de estudos do Optuna e `PruningCallback`. |
| **Hardware** | `test_telemetry.py` | Telemetria | Thread daemon de monitoramento de RAM (`psutil`) e VRAM (`nvidia-smi`). |
| **Orquestração** | `test_orchestrator_integration.py` | Integração Ponta a Ponta | Ciclo bifásico do `SimulationOrchestrator` e execução não bloqueante em background no `main.py`. |
| **Tráfego** | `test_traffic_simulator.py` | Núcleo de Tráfego | Validação das estratégias viárias (`Small`, `Medium`, `Large`, `Chaotic`, `GodunovNetworkFlowStrategy`) e propagação de veículos. |
| **Tráfego** | `test_flow_schedule.py` | Agendamento Diurno | Curvas de densidade em 48 slots e transições de horário de pico. |
| **Invariantes** | `test_flow_components.py` | Invariantes Físicos | Checagens contra velocidades negativas ou densidades matematicamente impossíveis. |
| **Topologia** | `test_map_provider.py` | Topologia Viária | Leitura de `.osm`, `.osm.gz` e `.net.xml`; projeção Snap-to-Road no asfalto com Haversine. |
| **Ambiente** | `test_environment.py` | Ambiente e Clima | Cálculo do Ground Zero (segunda-feira 00:00:00) e cadeia estocástica de Markov. |
| **Saídas** | `test_generators.py` | Geradores Multimodais | Geração de arquivos estruturados do Waze, TomTom, Câmeras LPR e Laços Indutivos. |
| **Sistema** | `test_dependency_checker.py` | Dependências | Detecção do PyTorch CUDA, Optuna, `llama-cpp-python` e bibliotecas gráficas. |

---

## 3. Execução dos Testes e Relatório de Cobertura

### 3.1 Instalar Dependências de Teste
```bash
pip install -r requirements-dev.txt
```

### 3.2 Executar Todos os Testes com Cobertura
```bash
.venv/bin/pytest --cov=src --cov=ui --cov=main tests/
```

### 3.3 Executar Camadas Específicas
```bash
# Testes da interface visual
.venv/bin/pytest -v tests/test_ui_views.py tests/test_ui_components.py

# Testes de IA e física espaço-temporal
.venv/bin/pytest -v tests/test_screenwriter_and_slm.py tests/test_gatv2.py tests/test_st_gatv2.py tests/test_pinn_hybrid.py

# Testes de hidrodinâmica e resolvedor de Riemann
.venv/bin/pytest -v tests/test_physics_godunov.py

# Teste de integração do orquestrador
.venv/bin/pytest -v tests/test_orchestrator_integration.py
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
