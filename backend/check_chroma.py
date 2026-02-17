
import chromadb
import os
from dotenv import load_dotenv

load_dotenv()
path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
print(f"Checking ChromaDB at: {path}")

client = chromadb.PersistentClient(path=path)
collections = client.list_collections()
print(f"Found {len(collections)} collections:")
for c in collections:
    print(f"- {c.name} (Count: {c.count()})")
