# 🚀 Развертывание, ускорение CUDA и настройка оборудования

В документе содержатся инструкции по развертыванию, системным требованиям, настройке виртуального окружения Python и конфигурации GPU NVIDIA с CUDA 12 для **SYNTHETIC**.

⬅️ [Главный Хаб](README.md) | 🏛️ [Архитектура системы](architecture.md) | 🧪 [Тестирование и QA](testing.md) | ⚡ [Справочник API](api_reference.md)

---

## 1. Системные требования

| Компонент | Минимальные требования | Рекомендуемая конфигурация |
|---|---|---|
| **Операционная система** | Linux (Ubuntu 22.04+), Windows 10/11 | Linux (Ubuntu 24.04 LTS) |
| **Python** | 3.10+ | 3.11 или 3.12 |
| **ОЗУ** | 8 ГБ | 16 ГБ или 32 ГБ DDR4/DDR5 |
| **Накопитель** | 10 ГБ свободного места | 50 ГБ+ NVMe SSD |
| **GPU / VRAM** | Только ЦП (медленно) | NVIDIA RTX (6 ГБ+ VRAM, CUDA 12.0+) |

---

## 2. Установка

```bash
git clone https://github.com/Noxfort-Systems-Brazil/SYNTHETIC.git
cd SYNTHETIC

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Размещение модели Phi-4
Поместите файл квантованной модели в:
```text
src/models/vault/Phi-4-mini-reasoning-UD-Q6_K_XL.gguf
```

### Запуск
```bash
python main.py
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
