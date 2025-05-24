# Briefed - AI-Powered News Aggregation Platform

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green) ![License](https://img.shields.io/badge/license-MIT-green) ![Docker](https://img.shields.io/badge/docker-ready-blueviolet)

A high-performance news aggregation service that collects, processes, and summarizes articles using custom NLP pipelines and machine learning.

---

## 🌟 Key Features

- **Multi-Source Ingestion**: Scrapes 50+ news sources with intelligent deduplication  
- **AI Summarization**: Custom TextRank algorithm with NLP preprocessing  
- **Real-time Processing**: Handles 500+ articles/minute with Redis caching  
- **Production Ready**: Dockerized with health checks and Prometheus monitoring  
- **Extensible Architecture**: Modular design for easy source additions  

---

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+  
- Python 3.11 (for development)  
- Redis 7.0+  
- PostgreSQL 15+  

### Docker Deployment

    git clone https://github.com/pnung/briefed.git
    cd briefed
    docker-compose up -d --build

### Local Development

    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # .venv\Scripts\activate    # Windows

    pip install -r requirements-dev.txt
    uvicorn app.main:app --reload

---

## ⚙️ Configuration

Create a `.env` file in the project root:

    # Database
    DB_HOST=postgres
    DB_PORT=5432
    DB_NAME=briefed
    DB_USER=postgres
    DB_PASSWORD=your_secure_password

    # Redis
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0

    # Application
    SCRAPE_INTERVAL=300        # in seconds
    LOG_LEVEL=INFO             # DEBUG / INFO / WARNING / ERROR
    CACHE_TTL=3600             # Redis cache timeout in seconds

---

## 🌐 API Documentation

**Base URL:**  
`http://localhost:8000/api/v1`

### Endpoints

| Endpoint            | Method | Description                  | Parameters                   |
|---------------------|--------|------------------------------|------------------------------|
| `/articles`         | GET    | List articles                | `source`, `limit`, `offset`  |
| `/articles/{id}`    | GET    | Get specific article         | –                            |
| `/summaries/{url}`  | GET    | Get AI summary               | `length` (short/medium/long) |
| `/sources`          | GET    | List available news sources  | –                            |
| `/admin/scrape`     | POST   | Trigger manual scrape        | `sources` (optional)         |
| `/health`           | GET    | System health check          | –                            |
| `/metrics`          | GET    | Prometheus metrics           | –                            |

### Example Request

    curl "http://localhost:8000/api/v1/articles?source=bbc&limit=5"

---

## 📊 Monitoring

The service exposes Prometheus metrics at `/metrics`, including:

- `http_requests_total`  
- `http_request_duration_seconds`  
- `articles_processed_total`  
- `db_query_duration_seconds`

---

## 🤝 Contributing

1. Fork the repository  
2. Create your feature branch:

       git checkout -b feature/AmazingFeature

3. Commit your changes:

       git commit -m "Add some AmazingFeature"

4. Push to the branch:

       git push origin feature/AmazingFeature

5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.