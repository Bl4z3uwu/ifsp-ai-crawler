import os
from dotenv import load_dotenv
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHROMA_DB_PATH = "./db/" 

# Google Generative AI Embedding Function, but aparently gemini doesn't like me :(
# embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=GOOGLE_API_KEY)

def update_database(data):  
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name="vtp.ifsp_data")

    if not data:
        print("No data to insert into the database.")
        return
    
    # Assigning IDs, contents, and metadatas from data
    ids = [item["id"] for item in data]
    contents = [item["conteudo"] for item in data]
    metadatas = [item["metadados"] for item in data]

    print(f"Sending {len(contents)} documents to collection (Upsert)...")
    
    collection.upsert(ids=ids, documents=contents, metadatas=metadatas)

    print("\n--- SUCESS! ---")
    print(f"The database has been populated. Total of itens: {collection.count()}")

def query_database(query):
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name="vtp.ifsp_data")

    # Querying the database for relevant documents, 5 results is enough for context
    results = collection.query(query_texts=[query], n_results=5, include=["documents", "metadatas"])

    return results