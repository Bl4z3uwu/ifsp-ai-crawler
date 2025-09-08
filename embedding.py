import os
from dotenv import load_dotenv
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHROMA_DB_PATH = "./db/" 

embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=GOOGLE_API_KEY)

def update_database(data):  
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(
        name="vtp.ifsp_data",
        embedding_function=embedding_function
    )

    if not data:
        print("Nenhum dado para adicionar.")
        return

    ids = [item["id"] for item in data]
    contents = [item["conteudo"] for item in data]
    metadatas = [item["metadados"] for item in data]

    print(f"Enviando {len(contents)} documentos para a coleção (Upsert)...")
    
    collection.upsert(ids=ids, documents=contents, metadatas=metadatas)

    print("\n--- SUCESSO! ---")
    print(f"O banco de dados foi populado. Total de itens: {collection.count()}")

def query_database(query):
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name="vtp.ifsp_data", embedding_function=embedding_function)

    results = collection.query(query_texts=[query], n_results=5, include=["documents", "metadatas"])

    return results