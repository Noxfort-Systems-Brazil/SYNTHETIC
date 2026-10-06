# 🚀 Instalação, Aceleração CUDA e Configuração de Hardware

Este documento especifica os pré-requisitos de infraestrutura, a instalação do ambiente virtual Python, a configuração de aceleração por GPU com NVIDIA CUDA 12 e o provisionamento do modelo Phi-4 no cofre local de pesos do **SYNTHETIC**.

⬅️ [Central de Documentação](README.md) | 🏛️ [Arquitetura do Sistema](architecture.md) | 🧪 [Testes e QA](testing.md) | ⚡ [Referência de APIs](api_reference.md)

---

## 1. Requisitos de Sistema

| Componente | Requisito Mínimo | Configuração Recomendada |
|---|---|---|
| **Sistema Operacional** | Linux (Ubuntu 22.04+), Windows 10/11 | Linux (Ubuntu 24.04 LTS) |
| **Python** | Python 3.10+ | Python 3.11 ou 3.12 |
| **Memória RAM** | 8 GB | 16 GB ou 32 GB DDR4/DDR5 |
| **Armazenamento** | 10 GB livres | 50 GB+ SSD NVMe |
| **GPU / VRAM** | CPU (execução lenta) | NVIDIA RTX (6 GB+ VRAM, CUDA 12.0+) |

---

## 2. Passo a Passo de Instalação

### 2.1 Clonar o Repositório e Criar o Ambiente Virtual
```bash
git clone https://github.com/Noxfort-Systems-Brazil/SYNTHETIC.git
cd SYNTHETIC

python3 -m venv .venv
source .venv/bin/activate   # No Windows: .venv\Scripts\activate
```

### 2.2 Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Verificar Aceleração CUDA
```bash
python -c "import torch; print('CUDA Disponível:', torch.cuda.is_available()); print('Dispositivo:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

---

## 3. Provisionamento do Modelo Phi-4 no Cofre (`src/models/vault/`)

O Roteirista cognitivo utiliza o modelo **Phi-4-mini Reasoning** em formato GGUF quantizado.

1. Crie o diretório do cofre:
   ```bash
   mkdir -p src/models/vault
   ```
2. Salve o arquivo do modelo exatamente no caminho:
   ```text
   src/models/vault/Phi-4-mini-reasoning-UD-Q6_K_XL.gguf
   ```

---

## 4. Inicialização do SYNTHETIC

Inicie a aplicação executando:
```bash
python main.py
```

### Fluxo na Interface Gráfica:
1. Defina a pasta de saída dos dados gerados.
2. Selecione o arquivo de mapa viário (`.osm` ou `.osm.gz`).
3. Clique em **SELECIONAR NO MAPA** para posicionar Câmeras (vermelho) e Laços Indutivos (azul) nas vias de interesse.
4. Ajuste parâmetros de duração, intervalo, densidade e percentual de falha de sensores.
5. Clique em **GERAR DADOS SINTÉTICOS** para iniciar a síntese neural em duas fases.

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
