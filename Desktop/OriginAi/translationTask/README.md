# OriginAI Translation Service

A production-ready REST API service for text translation using HelsinkiNLP MarianMT models from HuggingFace. This service provides translation capabilities for Hebrew-Russian and English-Hebrew language pairs.

## Quick Start

### Using Docker (Recommended)


1. **Build and run with Docker Compose**:
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

### 1. Translation
```http
POST translations/translate
```

**Request Body**:
```json
{
    "text": "Hello world",
    "source_lang": "en",
    "target_lang": "he"
}
```

**Note**: Text is limited to a maximum of 500 characters and up to 10 words. Longer texts will be rejected with a validation error.


**Response example**:
```json
{
    "translated_text": "שלום עולם",
    "source_lang": "en",
    "target_lang": "he",
    "original_text": "Hello world"
}
```

### 2. Supported_Languages
```http
GET translations/supported-languages
```
Returns information about supported language pairs and codes.
**Response example**:
```json
{
      "supported_language_pairs": {
        "he-ru": "Helsinki-NLP/opus-mt-he-ru",
        "en-he": "Helsinki-NLP/opus-mt-en-he",
    },
    "language_codes": {
        "he": "Hebrew",
        "ru": "Russian",
        "en": "English"
    }
}
### Running Tests

```bash
# Install test dependencies (included in requirements.txt) and activate env
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_translation_service.py -v
```

