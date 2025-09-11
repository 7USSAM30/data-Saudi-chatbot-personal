import weaviate
import numpy as np
import os
import json
from dotenv import load_dotenv
from weaviate.collections.classes.filters import Filter
from weaviate.collections.classes.batch import BatchObject
from weaviate.collections.classes.grpc import MetadataQuery

# Load environment variables
load_dotenv()

SCHEMA = {
    "classes": [
        {
            "class": "Chunk",
            "vectorizer": "none",
            "properties": [
                {"name": "text", "dataType": ["text"]},
                {"name": "source", "dataType": ["text"]},
                {"name": "year", "dataType": ["int"]},
                {"name": "language", "dataType": ["text"]},
                {"name": "type", "dataType": ["text"]},
                {"name": "score", "dataType": ["number"]},
            ]
        }
    ]
}

def get_weaviate_client():
    """Get Weaviate client - either cloud or local based on environment variables."""
    weaviate_url = os.getenv("WEAVIATE_URL")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    
    if weaviate_url and weaviate_api_key:
        # Use Weaviate Cloud
        return weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key),
            skip_init_checks=True
        )
    else:
        # Fallback to local Weaviate
        return weaviate.connect_to_local(skip_init_checks=True)

def create_schema():
    client = get_weaviate_client()
    try:
        existing = client.collections.list_all()
        if "Chunk" not in existing:
            client.collections.create_from_dict(SCHEMA["classes"][0])
    finally:
        client.close()

def upload_chunks_with_embeddings(json_path):
    client = get_weaviate_client()
    try:
        collection = client.collections.get("Chunk")
        with open(json_path, encoding="utf-8") as f:
            chunks = json.load(f)
        
        with collection.batch.dynamic() as batch:
            for chunk in chunks:
                if chunk.get("embedding") is None:
                    continue
                
                properties={
                    "text": chunk["text"],
                    "source": chunk.get("source"),
                    "year": chunk.get("year"),
                    "language": chunk.get("language"),
                    "type": chunk.get("type"),
                    "score": chunk.get("score", 1.0)
                }
                
                batch.add_object(
                    properties=properties,
                    vector=np.array(chunk["embedding"], dtype=np.float32)
                )
    finally:
        client.close()

def search_chunks(query_embedding, top_k=10, where=None):
    client = get_weaviate_client()
    try:
        collection = client.collections.get("Chunk")
        
        query_params = {
            "near_vector": query_embedding,
            "limit": top_k,
            "return_metadata": MetadataQuery(distance=True)
        }

        if where:
            if where["operator"] == "Equal":
                my_filter = Filter.by_property(where["path"][-1]).equal(where["valueText"])
                query_params["filters"] = my_filter
            else:
                raise NotImplementedError("Only 'Equal' operator is implemented in this example.")
        
        results = collection.query.near_vector(**query_params)
        
        out = [
            {"properties": obj.properties, "distance": obj.metadata.distance}
            for obj in results.objects
        ]
        return out
    finally:
        client.close()
