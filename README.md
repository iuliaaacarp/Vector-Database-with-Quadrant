# Semantic ArXiv Search API: Vector Database with Qdrant

A high-performance REST API that performs semantic and hybrid searches over a dataset of arXiv research papers. 

Unlike traditional keyword-based search engines, this application uses AI embeddings to understand the contextual meaning of a user's query. It translates natural language into vector space to find relevant academic papers, and supports strict metadata filtering by combining Regular Expressions with Qdrant's payload conditions.

## 🚀 Key Features

*   **Semantic Vector Search:** Integrates with OpenAI's `text-embedding-ada-002` model to convert natural language queries into 1536-dimensional vectors for deep semantic matching.
*   **Hybrid Search & Metadata Filtering:** Uses Regex parsing to dynamically extract author names from raw natural language queries (e.g., *"papers on clustering by Andrew Ng"*) and applies strict payload filtering in the vector database before calculating vector proximity.
*   **RESTful API Interface:** Built with FastAPI for high performance, featuring automated request validation and response serialization using strict Pydantic models.
*   **Containerized Infrastructure:** Utilizes a local Qdrant instance hosted via Docker with persistent volume storage for instant database querying without memory overhead.

## 🛠️ Technology Stack

*   **Language:** Python 3.14
*   **Web Framework:** FastAPI, Uvicorn
*   **Data Validation:** Pydantic
*   **Vector Database:** Qdrant (Local Docker Container)
*   **AI / Embeddings:** OpenAI API (`text-embedding-ada-002`)
*   **Other Tools:** Regex (`re`), Python `dotenv`

## 🏗️ System Architecture 

1.  **Request Handling:** The user submits a JSON payload to the `/search` POST endpoint. FastAPI and Pydantic validate the input schema (`query`, `top_n`).
2.  **Query Parsing:** A Regex pipeline intercepts the string to extract conditional metadata (e.g., identifying authors following the keyword "by").
3.  **Embedding Generation:** The cleaned text query is sent to OpenAI's API to generate a high-dimensional vector representation.
4.  **Vector Search:** The vector (and any extracted metadata filters) is queried against the local Qdrant database using cosine similarity. A custom Python safety net ensures absolute strict-match validation for author names.
5.  **Response Delivery:** The raw Qdrant point objects are parsed, reformatted into the `SearchResponse` Pydantic model, and returned to the client as clean JSON.

## 💻 Local Setup & Installation

### 1. Prerequisites
*   Docker Desktop running on your machine.
*   Python 3.9+
*   An active OpenAI API Key.

### 2. Start the Qdrant Database
Spin up the Qdrant vector database via Docker, mapping a local volume to persist the dataset:
```bash
docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)"/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```
### 3. Configure the Environment

Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```
Create a .env file in the root directory and add your API key:
```
OPENAI_API_KEY=sk-your-api-key-here
```
4. Run the API Server
Start the Uvicorn ASGI server:
```
uvicorn main:app --reload
```
The API will be available at http://127.0.0.1:8000. You can view the interactive Swagger documentation at http://127.0.0.1:8000/docs.
📡 API Usage Example
Endpoint: POST /search
Request:
```
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "the attention mechanism in deep learning by Ashish Vaswani",
           "top_n": 3
         }'
```
Response:
```
JSON
{
  "results": [
    {
      "id": "c1b2a3...",
      "payload": {
        "title": "Attention Is All You Need",
        "authors": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin"
      },
      "score": 0.92341
    }
  ]
}
