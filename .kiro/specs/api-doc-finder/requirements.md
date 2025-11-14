# Requirements Document

## Introduction

Этот документ описывает требования к Python-агенту для автоматического поиска документации API. Агент обрабатывает списки API методов из CSV или JSON файлов, находит OpenAPI/Swagger документацию через прямые запросы и множественные поисковые запросы через SerpAPI (google_lite и google_ai), и сохраняет результаты в CSV и JSON форматах. Агент работает асинхронно для высокой производительности.

## Glossary

- **Agent**: Python-приложение для автоматического поиска документации API
- **API Method**: Запись с информацией об API методе, содержащая name, method и method_link
- **Method Link**: URL-адрес конкретного API метода (например, `https://api.bitrix24.com/rest/user.add`)
- **OpenAPI Link**: Ссылка на OpenAPI/Swagger документацию
- **SerpAPI**: Сервис для программного доступа к результатам поиска Google
- **Google Lite Engine**: Быстрый поисковый движок SerpAPI для базовых запросов
- **Google AI Engine**: AI-powered поисковый движок SerpAPI для более точных результатов
- **Standard OpenAPI Paths**: Типичные пути OpenAPI документации (`/openapi.json`, `/openapi.yaml`, `/swagger.json`, `/swagger.yaml`, `/api-docs`, `/redoc`)
- **CLI**: Command Line Interface - интерфейс командной строки

## Requirements

### Requirement 1

**User Story:** Как инженер данных, я хочу загружать список API методов из CSV или JSON файла, чтобы обработать большое количество методов автоматически

#### Acceptance Criteria

1. WHEN the user provides an input file path via `--input` argument, THE Agent SHALL detect the file format by extension (.csv or .json)
2. WHEN the input file is CSV, THE Agent SHALL parse it expecting columns: name, method, method_link
3. WHEN the input file is JSON, THE Agent SHALL parse it as an array of objects with fields: name, method, method_link
4. IF the input file does not exist or cannot be read, THEN THE Agent SHALL log an error message and terminate with a non-zero exit code
5. THE Agent SHALL validate that each record contains required fields (name, method, method_link) before processing
6. THE Agent SHALL skip records with missing required fields and log a warning

### Requirement 2

**User Story:** Как инженер данных, я хочу, чтобы агент сначала проверял стандартные пути OpenAPI документации, чтобы минимизировать использование платного API поиска

#### Acceptance Criteria

1. WHEN processing an API method, THE Agent SHALL extract the base domain from the method_link URL
2. THE Agent SHALL check the following standard OpenAPI paths in priority order: `/openapi.json`, `/openapi.yaml`, `/swagger.json`, `/swagger.yaml`, `/api-docs`, `/redoc`
3. WHEN checking a standard path, THE Agent SHALL send an HTTP HEAD request first, and if status is 200, then send GET request
4. IF a standard path returns status 200, THEN THE Agent SHALL record this URL in the openapi_link field
5. IF OpenAPI documentation is found via direct check, THEN THE Agent SHALL skip SerpAPI search for this record
6. THE Agent SHALL use asynchronous HTTP requests via aiohttp for all standard path checks

### Requirement 3

**User Story:** Как инженер данных, я хочу использовать множественные поисковые запросы через SerpAPI, когда прямой поиск не дает результатов, чтобы найти документацию через разные поисковые стратегии

#### Acceptance Criteria

1. IF no OpenAPI documentation is found via standard paths, THEN THE Agent SHALL execute 4 different SerpAPI search queries
2. THE Agent SHALL execute search query with engine=google_lite and q="{name} {method} api documentation link" and store result in search_method_name field
3. THE Agent SHALL execute search query with engine=google_lite and q="{name} {method_link} api documentation" and store result in search_method_link field
4. THE Agent SHALL execute search query with engine=google_ai and q="{name} {method} api documentation link" and store result in ai_method_name field
5. THE Agent SHALL execute search query with engine=google_ai and q="{name} {method_link} api documentation" and store result in ai_method_link field
6. WHEN SerpAPI returns results, THE Agent SHALL extract the first organic search result URL (or link field for AI results)
7. IF SerpAPI returns an error or no results for a query, THEN THE Agent SHALL store "error" in the corresponding field

### Requirement 4

**User Story:** Как инженер данных, я хочу, чтобы агент работал асинхронно с ограничением параллельных запросов, чтобы эффективно обрабатывать множество API методов без перегрузки системы

#### Acceptance Criteria

1. THE Agent SHALL use asyncio for concurrent processing of multiple API methods
2. THE Agent SHALL limit concurrent HTTP requests to a maximum of 20 simultaneous connections
3. THE Agent SHALL use aiohttp.ClientSession with a connection pool for efficient resource management
4. THE Agent SHALL implement semaphore-based concurrency control to enforce the 20-request limit
5. WHEN all API methods are processed, THE Agent SHALL properly close all async resources before termination

### Requirement 5

**User Story:** Как инженер данных, я хочу видеть прогресс обработки в реальном времени, чтобы понимать, сколько API методов уже обработано

#### Acceptance Criteria

1. THE Agent SHALL display a progress bar using tqdm library showing the number of processed API methods
2. WHEN an API method is successfully processed, THE Agent SHALL log a message in format: `✅ найдено для {name} {method}`
3. WHEN an API method processing fails, THE Agent SHALL log a message in format: `❌ ошибка для {name} {method}: <error_message>`
4. THE Agent SHALL update the progress bar after each API method is processed
5. THE Agent SHALL display the total processing time when all API methods are completed

### Requirement 6

**User Story:** Как инженер данных, я хочу сохранять результаты в CSV и JSON файлы, чтобы использовать их в других системах и инструментах

#### Acceptance Criteria

1. THE Agent SHALL accept an output file path via `--output` argument with default value `results`
2. THE Agent SHALL create two output files: `{output}.csv` and `{output}.json`
3. THE Agent SHALL create CSV file with columns: name, method, method_link, openapi_link, search_method_name, search_method_link, ai_method_name, ai_method_link
4. THE Agent SHALL create JSON file as an array of objects with the same fields as CSV
5. WHEN OpenAPI documentation is found via direct check, THE Agent SHALL populate openapi_link field and leave search fields empty
6. WHEN OpenAPI documentation is not found, THE Agent SHALL leave openapi_link empty and populate all 4 search result fields
7. IF a search query returns no results or error, THEN THE Agent SHALL store "error" in the corresponding field
8. IF the output files cannot be written, THEN THE Agent SHALL log an error message and terminate with a non-zero exit code

### Requirement 7

**User Story:** Как инженер данных, я хочу использовать CLI аргументы для настройки агента, чтобы гибко управлять входными и выходными файлами

#### Acceptance Criteria

1. THE Agent SHALL use argparse library to define command-line arguments
2. THE Agent SHALL support `--input` argument (required) to specify the path to the input CSV or JSON file
3. THE Agent SHALL support `--output` argument (optional, default: `results`) to specify the output file base name (without extension)
4. THE Agent SHALL read SerpAPI key from hardcoded value: `dc2bf39c68168f9a35abdac1b265db678d4e97537344e7dee9848c46e7b43b72`
5. THE Agent SHALL display help information when invoked with `--help` or `-h` flag
6. IF required arguments are missing, THEN THE Agent SHALL display an error message and usage information

### Requirement 8

**User Story:** Как инженер данных, я хочу, чтобы агент корректно обрабатывал ошибки, чтобы один неудачный API метод не останавливал обработку всех остальных

#### Acceptance Criteria

1. WHEN an HTTP request fails with a network error, THE Agent SHALL catch the exception and store "error" in the corresponding field
2. WHEN an HTTP request times out after 10 seconds, THE Agent SHALL store "error" for that check
3. WHEN SerpAPI returns an error response or no results, THE Agent SHALL store "error" in the corresponding search field
4. THE Agent SHALL continue processing remaining API methods even when individual methods fail
5. THE Agent SHALL include all errors in the final CSV and JSON outputs with "error" value in failed fields
