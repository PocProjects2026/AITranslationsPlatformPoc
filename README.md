# Asset Management API

This is a Django REST Framework backend for generating Asset Management reports in PDF format using WeasyPrint.
It supports generating the PDF in English, French, and German using Django's native internationalization (`gettext`, `.po`, `.mo`).

## Prerequisites

- Python 3.11+
- [WeasyPrint dependencies](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) (GTK3, Pango, Cairo, etc.)
- Docker (optional, but recommended for avoiding native dependency issues)

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `.\venv\Scripts\activate` on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   ```

## Translation Compilation

Django's native translations use `.po` source files located in the `locale/` directory.
Before running the server, or after updating translations, compile the `.mo` files:

```bash
python manage.py compilemessages
```
*(Note: This requires GNU gettext installed on your system. It is automatically handled in the Docker build.)*

## Run Locally

Start the development server:
```bash
python manage.py runserver
```

## Generate Report (API Endpoints)

### Health Check

```bash
curl http://localhost:8000/health
```
**Response:**
```json
{
  "status": "ok"
}
```

### PDF Generation

Use `POST /reports/assets` with a `language` parameter. Supported languages are `en`, `fr`, and `de`.

**English:**
```bash
curl -X POST http://localhost:8000/reports/assets \
     -H "Content-Type: application/json" \
     -d '{"language":"en"}' \
     --output asset-report-en.pdf
```

**French:**
```bash
curl -X POST http://localhost:8000/reports/assets \
     -H "Content-Type: application/json" \
     -d '{"language":"fr"}' \
     --output asset-report-fr.pdf
```

**German:**
```bash
curl -X POST http://localhost:8000/reports/assets \
     -H "Content-Type: application/json" \
     -d '{"language":"de"}' \
     --output asset-report-de.pdf
```

If an unsupported language (e.g., `es`) is provided, you will receive a 400 Bad Request error:
```json
{
  "error": "Unsupported language",
  "supported_languages": ["en", "fr", "de"]
}
```

## Tests

Run the test suite using Django's test runner:
```bash
python manage.py test
```

## Docker

Build the image:
```bash
docker build -t asset_manager .
```

Run the container:
```bash
docker run -p 8000:8000 asset_manager
```

## CI/CD

This project uses GitHub Actions for CI and CD.
- **CI Workflow:** Runs on pushes and pull requests to `main`. It installs dependencies, compiles translations (`compilemessages`), runs the test suite, checks Django config, and performs a Docker build to verify the container image builds correctly.
- **CD Workflow:** Runs on pushes to `main`. It builds and pushes the Docker image to GitHub Container Registry, and simulates deployment using GitHub Secrets (`PROD_SSH_KEY`, `PROD_HOST`, `PROD_USER`). No credentials are hardcoded.
