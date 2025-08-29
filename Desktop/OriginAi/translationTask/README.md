# OriginAI Translation Service

A production-ready REST API service for text translation using HelsinkiNLP MarianMT models from HuggingFace. This service provides translation capabilities for Hebrew-Russian and English-Hebrew language pairs.

## Features

- **Multiple Language Pairs**: Hebrew ↔ Russian, English ↔ Hebrew
- **REST API**: Clean, well-documented API endpoints
- **Batch Translation**: Support for translating multiple texts in a single request
- **Model Caching**: Efficient model loading and caching
- **Error Handling**: Comprehensive error handling and validation
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Production Ready**: Logging, health checks, and proper error responses
- **Testing**: Comprehensive unit and integration tests

## Supported Language Pairs

| Source Language | Target Language | Model |
|----------------|----------------|-------|
| Hebrew (he) | Russian (ru) | Helsinki-NLP/opus-mt-he-ru |
| Russian (ru) | Hebrew (he) | Helsinki-NLP/opus-mt-ru-he |
| English (en) | Hebrew (he) | Helsinki-NLP/opus-mt-en-he |
| Hebrew (he) | English (en) | Helsinki-NLP/opus-mt-he-en |

## Quick Start

### Using Docker (Recommended)

1. **Clone and navigate to the project directory**:
   ```bash
   cd translationTask
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **The API will be available at**: `http://localhost:8000`

4. **View API documentation**: `http://localhost:8000/docs`

### Local Development

1. **Install Python 3.11+** (if not already installed)

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### 1. Health Check
```http
GET /health
```
Returns service status and information about loaded models.

### 2. Single Translation
```http
POST /translate
```

**Request Body**:
```json
{
    "text": "Hello world",
    "source_lang": "en",
    "target_lang": "he"
}
```

**Note**: Text is limited to a maximum of 10 words. Longer texts will be rejected with a validation error.

**Response**:
```json
{
    "translated_text": "שלום עולם",
    "source_lang": "en",
    "target_lang": "he",
    "original_text": "Hello world"
}
```

### 3. Batch Translation
```http
POST /translate/batch
```

**Request Body**:
```json
{
    "texts": ["Hello", "Good morning"],
    "source_lang": "en",
    "target_lang": "he"
}
```

**Note**: Each text in the batch is limited to a maximum of 10 words. The batch can contain up to 100 texts.

**Response**:
```json
{
    "translations": [
        {
            "translated_text": "שלום",
            "source_lang": "en",
            "target_lang": "he",
            "original_text": "Hello"
        },
        {
            "translated_text": "בוקר טוב",
            "source_lang": "en",
            "target_lang": "he",
            "original_text": "Good morning"
        }
    ],
    "total_count": 2
}
```

### 4. Supported Languages
```http
GET /supported-languages
```
Returns information about supported language pairs and codes.

## Usage Examples

### Using curl

```bash
# Single translation
curl -X POST "http://localhost:8000/translate" \
     -H "Content-Type: application/json" \
     -d '{
         "text": "Hello world",
         "source_lang": "en",
         "target_lang": "he"
     }'

# Batch translation
curl -X POST "http://localhost:8000/translate/batch" \
     -H "Content-Type: application/json" \
     -d '{
         "texts": ["Hello", "Good morning"],
         "source_lang": "en",
         "target_lang": "he"
     }'

# Health check
curl http://localhost:8000/health
```

### Using Python requests

```python
import requests

# Single translation
response = requests.post("http://localhost:8000/translate", json={
    "text": "שלום עולם",
    "source_lang": "he",
    "target_lang": "en"
})
print(response.json())

# Batch translation
response = requests.post("http://localhost:8000/translate/batch", json={
    "texts": ["שלום", "בוקר טוב"],
    "source_lang": "he", 
    "target_lang": "ru"
})
print(response.json())
```

## Development

### Running Tests

```bash
# Install test dependencies (included in requirements.txt)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_translation_service.py -v
```

### Code Quality

The project follows Python best practices:
- **Type hints** for better code documentation
- **Pydantic models** for request/response validation
- **Comprehensive logging** for debugging and monitoring
- **Error handling** with proper HTTP status codes
- **Separation of concerns** with service layer pattern
- **Unit and integration tests** for reliability

### Project Structure

```
translationTask/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── translation_service.py  # Translation logic
├── tests/
│   ├── __init__.py
│   ├── test_api.py            # API integration tests
│   └── test_translation_service.py  # Service unit tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

## Performance Considerations

- **Model Caching**: Models are loaded once and cached in memory
- **GPU Support**: Automatically uses GPU if available (CUDA)
- **Batch Processing**: Efficient batch translation endpoint
- **Request Validation**: Input validation to prevent processing invalid requests

## Error Handling

The API provides clear error messages for common issues:
- **400 Bad Request**: Invalid input (empty text, unsupported languages, etc.)
- **422 Unprocessable Entity**: Request validation errors
- **500 Internal Server Error**: Translation model errors
- **503 Service Unavailable**: Service not initialized

## Security Considerations

- **Non-root user**: Docker container runs as non-root user
- **Input validation**: Strict validation of all inputs
- **Resource limits**: Text length limits to prevent abuse
- **CORS**: Configurable CORS settings (currently permissive for development)

## Monitoring and Health Checks

- **Health endpoint**: `/health` provides service status
- **Logging**: Comprehensive logging for debugging and monitoring
- **Docker health checks**: Built-in container health monitoring

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Configure settings via environment variables
2. **Resource Limits**: Set appropriate CPU and memory limits
3. **Load Balancing**: Use multiple instances behind a load balancer
4. **Monitoring**: Integrate with monitoring solutions (Prometheus, etc.)
5. **Security**: Update CORS settings, add authentication if needed
6. **Model Persistence**: Consider mounting model cache volume for faster startup

## License

This project is developed as a technical assessment for OriginAI.