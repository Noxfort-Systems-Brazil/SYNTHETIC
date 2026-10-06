# 🔄 Pipeline de CI/CD e Automação no GitHub Actions

Este documento descreve a arquitetura de Integração Contínua (CI) e Entrega Contínua (CD) do **SYNTHETIC**, incluindo fluxos automatizados de testes headless, checagem de cobertura (qualidade mínima de 80%), compilação estrita da documentação e deploy no GitHub Pages.

⬅️ [Central de Documentação](README.md) | 🏛️ [Arquitetura do Sistema](architecture.md) | 🧪 [Suíte de Testes](testing.md) | ⚡ [Referência de APIs](api_reference.md)

---

## 1. Visão Geral da Esteira de CI/CD

A pipeline do SYNTHETIC foi concebida para validar cada commit e Pull Request enviado ao branch `main`, garantindo:
1. **Ambiente Reprodutível:** Configuração automatizada em runners Ubuntu com Python 3.12 e cache de dependências.
2. **Execução Headless da Interface Gráfica:** Uso do `xvfb-run` para executar testes do CustomTkinter e Tkinter sem display físico.
3. **Quality Gate de Cobertura:** Rejeição automática de PRs que fiquem abaixo de 80% de cobertura (atualmente em 86%).
4. **Build Estrito da Documentação:** Verificação de links quebrados ou erros de formatação no MkDocs com `--strict`.
5. **Deploy Automático:** Publicação contínua do portal estático no GitHub Pages a cada merge na `main`.

---

## 2. Configuração do Workflow (`.github/workflows/ci.yml`)

```yaml
name: SYNTHETIC CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-and-verify:
    name: Testes, Cobertura e Validação de Docs
    runs-on: ubuntu-latest

    steps:
      - name: Checkout do Código
        uses: actions/checkout@v4

      - name: Configurar Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Instalar Dependências do Sistema para GUI Headless
        run: |
          sudo apt-get update
          sudo apt-get install -y xvfb python3-tk

      - name: Instalar Dependências do Projeto
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pip install mkdocs mkdocs-material

      - name: Executar Testes com Quality Gate (>= 80%)
        run: |
          xvfb-run -a pytest -v --cov=src --cov=ui --cov=main --cov-fail-under=80 tests/

      - name: Validar Build da Documentação (Modo Estrito)
        run: |
          mkdocs build --strict

  deploy-docs:
    name: Publicar Documentação no GitHub Pages
    needs: test-and-verify
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout do Código
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Instalar MkDocs e Tema Material
        run: |
          pip install mkdocs mkdocs-material

      - name: Publicar Documentação
        run: |
          mkdocs gh-deploy --force
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
