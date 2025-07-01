from fastapi import FastAPI
from app.api import embeddings, similarity_search, askai
from app.core.mongodb import create_chunk_indexes, test_mongo_connection


app = FastAPI(title="GenAI Labs Research Assistant", version="1.0.0")

app.include_router(embeddings.router, prefix="/api", tags=["Embeddings"])
app.include_router(
    similarity_search.router, prefix="/api/similarity", tags=["Similarity Search"]
)
app.include_router(askai.router, prefix="/api/askai", tags=["Ask AI"])


@app.get("/")
async def root():
    return {"message": "Welcome to genai labs  research assistant!"}


@app.on_event("startup")
def startup_event():
    test_mongo_connection()
    create_chunk_indexes()
