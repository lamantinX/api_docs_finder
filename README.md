# API Documentation Finder

Автоматический поиск документации для API методов с использованием прямой проверки OpenAPI и поисковых запросов через SerpAPI.

## Установка

```bash
pip install -r requirements.txt
```

Требования: Python 3.7+, зависимости: `aiohttp>=3.9.0`, `tqdm>=4.66.0`

## Использование

```bash
python main.py --input input.csv [--output results]
```

## Формат входных файлов

CSV или JSON с полями: `name`, `method`, `method_link`

Пример CSV:
```csv
name,method,method_link
Slack,Send message,https://slack.com/api/chat.postMessage
```

Пример JSON:
```json
[{"name": "Slack", "method": "Send message", "method_link": "https://slack.com/api/chat.postMessage"}]
```

## Формат выходных файлов

Создаются `results.csv` и `results.json` с полями:
- `name`, `method`, `method_link` - из входного файла
- `openapi_link` - найденная OpenAPI документация
- `search_method_name`, `search_method_link` - результаты Google Lite поиска
- `ai_method_name`, `ai_method_link` - результаты Google AI поиска

## Как работает

1. Прямая проверка OpenAPI/Swagger на стандартных путях (`/openapi.json`, `/swagger.json`, `/api-docs`, `/redoc`)
2. Если OpenAPI не найден - 4 поисковых запроса через SerpAPI (Google Lite и Google AI)
3. Асинхронная обработка до 20 методов параллельно
