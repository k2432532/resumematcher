import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "resume-matcher"

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_index_if_not_exists():
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=384,
            metric='cosine',
            spec=ServerlessSpec(
                cloud=os.getenv("PINECONE_CLOUD", "aws"),
                region=os.getenv("PINECONE_REGION", "us-west-2")
            )
        )

def get_embedding(text):
    return model.encode(text).tolist()

def upsert_resume(candidate_id, resume_text):
    index = pc.Index(index_name)
    embedding = get_embedding(resume_text)
    index.upsert(vectors=[(str(candidate_id), embedding)])

def search_similar_resumes(job_description, top_k=10):
    index = pc.Index(index_name)
    query_embedding = get_embedding(job_description)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return results

def delete_resume(candidate_id):
    index = pc.Index(index_name)
    index.delete(ids=[str(candidate_id)])