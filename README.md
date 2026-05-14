Product Review Classifier with LLM API

Скрипт читает отзывы из CSV-файла, отправляет каждый в LLM через API и сохраняет структурированный результат (тональность, тема, уверенность) в JSON.

### Задача

Автоматическая классификация отзывов на продукты:
- **Тональность** (`sentiment`): `positive` / `negative` / `neutral`
- **Тема** (`topic`): основная тема отзыва, 1–3 слова
- **Уверенность** (`confidence`): число от 0.0 до 1.0

## Как устроена отправка данных через API

Скрипт использует **Xiaomi MiMo** — локальную LLM, запущенную через [Ollama](https://ollama.com).

Ollama поднимает REST API на `http://localhost:11434`. Для каждого отзыва скрипт отправляет HTTP POST-запрос:

```
POST http://localhost:11434/api/chat
Content-Type: application/json

{
  "model": "alibayram/mimo-7b-rl:latest",
  "messages": [
    {"role": "system", "content": "<инструкция классификатора>"},
    {"role": "user",   "content": "Review: <текст отзыва>"}
  ],
  "stream": false,
  "format": "json"
}
```

## Требования

Сторонние библиотеки не используются — только стандартная библиотека Python (`urllib`, `csv`, `json`).

Для запуска нужно:
- Python 3.8+
- Ollama [ollama.com/download](https://ollama.com/download)
- Модель MiMo (скачивается командой ниже, ~4.7 ГБ)

## Установка и запуск

### 1. Установить Ollama

Скачать и установить с [ollama.com/download](https://ollama.com/download).  
После установки Ollama запускается автоматически как фоновый сервис.

### 2. Скачать модель MiMo

```bash
ollama pull alibayram/mimo-7b-rl:latest
```

Дождаться завершения загрузки (~4.7 ГБ).

### 3. Клонировать репозиторий

```bash
git clone <url-репозитория>
cd <папка>
```

### 4. Запустить скрипт

```bash
python analyze_reviews.py
```

Скрипт автоматически:
- берёт случайную выборку 100 отзывов из `product_reviews_mock_data.csv` (seed=42, воспроизводимо)
- сохраняет выборку в `sample_input.csv`
- отправляет каждый отзыв в MiMo через Ollama API
- сохраняет результаты в `results.json`

> **Время выполнения:** +-15–30 минут на CPU, +-3–5 минут с GPU.

## Файлы

| Файл | Описание |
|---|---|
| `analyze_reviews.py` | основной скрипт |
| `product_reviews_mock_data.csv` | полный датасет (1000 отзывов) |
| `sample_input.csv` | входные данные, на которых получен результат (100 отзывов, seed=42) |
| `results.json` | результаты работы скрипта |

## Пример входных данных (`sample_input.csv`)

```
ReviewID,ProductID,UserID,Rating,ReviewText,ReviewDate
REV2654,Product_E,User_190,3,neither good nor bad. highly recommend.,2023-07-11
REV2114,Product_A,User_155,5,fantastic. love this product.,2024-03-02
REV2025,Product_A,User_123,4,it's okay. five stars.,2023-05-18
```

## Пример выходных данных (`results.json`)

```json
[
  {
    "review_id": "REV2654",
    "product_id": "Product_E",
    "rating": "3",
    "review_text": "neither good nor bad. highly recommend.",
    "sentiment": "positive",
    "topic": "general feedback",
    "confidence": 0.75
  },
  {
    "review_id": "REV2114",
    "product_id": "Product_A",
    "rating": "5",
    "review_text": "fantastic. love this product.",
    "sentiment": "positive",
    "topic": "product quality",
    "confidence": 1.0
  }
]
```
