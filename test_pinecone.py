import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

load_dotenv()

def main():
    print("Initializing Pinecone...")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    print("Pinecone initialized successfully.")

    print("Initializing SentenceTransformer...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("SentenceTransformer initialized successfully.")

    print("Creating a test embedding...")
    test_text = "This is a test sentence."
    embedding = model.encode(test_text).tolist()
    print("Embedding created successfully.")

    print("Test completed without errors.")

if __name__ == "__main__":
    main()