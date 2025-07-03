# 🧠 GenAI Labs Research Assistant

An AI-powered backend system that performs real-time document ingestion, similarity search, and intent-based AI responses using FastAPI, Celery, Qdrant, and Redis.

## 🖼️ Architecture Overview

![Architecture Diagram](docs/fastapi-celery-flow.png)

This architecture shows how Celery handles background tasks. A client uploads a file, which is queued for background processing. Celery workers then chunk, embed, and store results in Qdrant. Clients can query the status or results later asynchronously.

The diagram illustrates the ingestion pipeline:

-   The client triggers journal file processing via FastAPI.
-   FastAPI enqueues chunking and embedding tasks to Redis (broker).
-   Celery workers process the content asynchronously.
-   Metadata and embeddings are saved to Qdrant.
-   Client can query task status or search enriched results.

This decoupled, asynchronous approach ensures scalability and efficient resource utilization.

## Setup Instructions

### 📁 Environment Variables

Before starting, create a `.env` file at the root of the project with the following:

```
MONGO_URI=mongodb://admin:password@mongodb:27017/genailabs_db?authSource=admin
MONGO_DB_NAME=genailabs_db
ANTHROPIC_API_KEY="your api key here"
```

### 🔧 Build the Docker Image

```bash
docker build -t genailabs .
```

⚠️ This may take 7–10 minutes on the first build due to dependency installation.

### 🐳 Start the Containers

```bash
docker-compose up -d
```

This starts the FastAPI server and Celery worker. You are good to go now!

### 🌐 Access the API

Once the containers are running, visit the Swagger docs:  
[http://localhost:8001/docs](http://localhost:8001/docs)

You’ll see the following available endpoints:

#### 🧠 Embeddings

| Method | Endpoint                    | Description                       |
| ------ | --------------------------- | --------------------------------- |
| PUT    | `/api/upload/`              | Upload JSON file or URL           |
| GET    | `/api/{job_id}`             | Get embedding task status/results |
| GET    | `/api/journal/{journal_id}` | Get journal chunks                |

#### ⚠️ Important Notes for Uploading Files

-   The `id` field must be a valid UUID. It is mandatory for embedding creation.
-   The `publish_year` should follow the YYYY format.
-   Each chunk must include metadata fields like `source_doc_id`, `journal`, `usage_count`, `attributes`, and `text`.

#### ✅ Example Upload Payload:

```json
[
    {
        "id": "00a72a58-a447-43ae-a36d-bd8397f3e224",
        "source_doc_id": "updated_farming_guide_mucuna.pdf",
        "chunk_index": 4,
        "section_heading": "Cultivation Guidelines",
        "journal": "Farming Guide",
        "publish_year": 2019,
        "usage_count": 23,
        "attributes": ["Cultivation", "Planting techniques"],
        "link": "https://example.org/bitstream/content2",
        "text": "Proper cultivation of mucuna involves land preparation, spacing, and seasonal monitoring for best yield..."
    },
    {
        "id": "836e175e-f277-48b2-a257-ead22e8ca5e9",
        "source_doc_id": "updated_plant_health_mucuna.pdf",
        "chunk_index": 5,
        "section_heading": "Common Diseases",
        "journal": "Plant Health Reports",
        "publish_year": 2020,
        "usage_count": 18,
        "attributes": ["Diseases", "Pest management"],
        "link": "https://example.org/bitstream/content3",
        "text": "Mucuna is susceptible to fungal infections and pest attacks. Integrated pest management practices are recommended..."
    },
    {
        "id": "b2af23c8-231b-4e61-88aa-1a54d61cd02a",
        "source_doc_id": "updated_market_trends_mucuna.pdf",
        "chunk_index": 6,
        "section_heading": "Market Opportunities",
        "journal": "AgriBusiness Journal",
        "publish_year": 2021,
        "usage_count": 51,
        "attributes": ["Market", "Export potential"],
        "link": "https://example.org/bitstream/content4",
        "text": "Mucuna has seen a rise in market demand due to its value in biofertilizers and livestock feed markets..."
    }
]
```

#### 🔍 Similarity Search

| Method | Endpoint                   | Description                   |
| ------ | -------------------------- | ----------------------------- |
| POST   | `/api/similarity/`         | Start similarity search       |
| GET    | `/api/similarity/{job_id}` | Get similarity search results |

#### 💬 Ask AI

| Method | Endpoint      | Description                                                   |
| ------ | ------------- | ------------------------------------------------------------- |
| POST   | `/api/askai/` | Start AI query based on intent and retrieved document context |

### 🧠 AI Agent Capabilities

The `/api/askai/` endpoint is powered by an AI agent that can:

-   🔍 Analyze user intent from the question
-   📖 Route queries to:
    -   Q&A using relevant chunks via similarity search (Qdrant)
    -   Summarization of a document based on `source_doc_id`
    -   Comparison between two documents side-by-side based on source id

Powered by Celery + FastAPI + Qdrant. Scalable. Modular. Intelligent.
