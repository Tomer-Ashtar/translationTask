# OriginAI Translation Service

service for text translation using HelsinkiNLP MarianMT models from HuggingFace. This service provides translation capabilities for Hebrew-Russian and English-Hebrew language pairs.

## Quick Start

### Using Docker (Recommended)

**Prerequisites**: Docker and Docker Compose must be installed on your system.

1.  **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   
   This command will:
   - Build the Docker image
   - Download required Python packages and ML models
   - Start the translation service
   
3. **The API will be available at**: `http://localhost:8000`

4. **View API documentation**: `http://localhost:8000/docs`

5. **To stop the service**:
   ```bash
   # Press Ctrl+C in the terminal, or run in another terminal:
   docker-compose down
   ```

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

   The application supports two model loading strategies:
   
   - **Default (Eager Loading)**: All translation models are loaded at startup
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     ```

   - **Lazy Loading**: Models are loaded on first use
     ```bash
     TRANSLATION_LAZY_LOADING=true uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     ```

## API Endpoints

### 1. Translation
```http
POST translations/translate
```

**Request Body example**:
```json
{
    "text": "Hello world",
    "source_lang": "en",
    "target_lang": "he"
}
```

**Note**: Text is limited to a 1 - 500 characters and up to 10 words. Longer texts will be rejected with a validation error.


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
GET translations/supported_languages
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
```
## Running Tests

### Using Docker (Recommended)

Run tests in Docker containers to ensure consistency across environments:

#### **Method 1: Dedicated Test Container**
```bash
# Run all tests in a separate, clean container
docker-compose --profile test run --rm test

# Run tests with verbose output
docker-compose --profile test run --rm test python -m pytest -v

# Run specific test file
docker-compose --profile test run --rm test python -m pytest tests/test_api.py -v
```

### Local Development Testing

Before running the tests locally, make sure you have activated the virtual environment:

```bash
# Activate the virtual environment (IMPORTANT!)
source venv/bin/activate  # On Unix/macOS
# OR
venv\Scripts\activate     # On Windows
```

Run the tests using any of these commands:

```bash
# Run all tests (simple output)
python -m pytest

# Run all tests with verbose output (-v flag shows each test case)
python -m pytest -v

# Run specific test file (simple output)
python -m pytest tests/test_translation_service.py

# Run specific test file with verbose output
python -m pytest tests/test_translation_service.py -v
```

