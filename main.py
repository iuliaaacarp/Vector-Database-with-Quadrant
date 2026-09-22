from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient, models
import re

load_dotenv()

client = QdrantClient(host="localhost", port=6333, timeout=60.0)
COLLECTION_NAME = 'arxiv_papers'

openai_client = OpenAI()

def get_author_name(query: str):
    pattern = r"by\s+([A-Za-z\s\-]+)"
    match = re.search(pattern, query)
    if match:
        return match.group(1).strip()
    return None

def get_embedding(query: str) -> list[float]:
    clean_query = query.replace("\n", " ")

    response = openai_client.embeddings.create(
        input=clean_query,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def find_top_similar_entries(query: str, top_k=5):
    author = get_author_name(query)
    embedding_vector = get_embedding(query)

    qdrant_filter = None
    if author:
        qdrant_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="authors",
                    match=models.MatchText(text=author)
                )
            ]
        )
    else:
        print("No author found...")

    raw_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding_vector,
        query_filter=qdrant_filter,
        limit=top_k * 5,
        with_payload=True,
        with_vectors=False
    ).points

    final_results = []
    for r in raw_results:
        if author and author not in r.payload.get("authors", ""):
            continue

        final_results.append(r)

        if len(final_results) == top_k:
            break

    return final_results

from fastapi import FastAPI

app = FastAPI()

from typing import Optional, List, Dict
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_n: Optional[int] = 5


class SearchResult(BaseModel):
    id: str
    payload: Dict
    score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]

@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    raw_results = find_top_similar_entries(request.query, request.top_n)
    formatted_results = []
    for result in raw_results:
        formatted_results.append(SearchResult(id=str(result.id), payload=result.payload, score=result.score))

    return SearchResponse(results=formatted_results)

if __name__ == "__main__":
    search_text = "Mentions of point clouds by Tian-Xing Xu"

    paper_ids = []
    results = find_top_similar_entries(search_text, top_k=5)
    for result in results:
        paper_ids.append(result.payload["id"])

    print(paper_ids)