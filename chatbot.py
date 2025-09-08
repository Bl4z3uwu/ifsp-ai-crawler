import os
from dotenv import load_dotenv
import google.generativeai as genai
from embedding import query_database
from typing import List

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.5-pro")

def build_prompt(query: str, context: List[str]) -> str:
    # Join context pieces with separators for clarity
    context_str = "\n---\n".join(context)

    # Define system and user prompts
    system_prompt = (
        "Você é um assistente virtual do site do IFSP de Votuporanga. "
        "Sua única fonte de conhecimento é o contexto fornecido abaixo. "
        "Responda à pergunta do usuário de forma clara e objetiva, baseando-se exclusivamente neste contexto. "
        "Se a resposta não estiver no contexto, afirme que não possui a informação. "
        "Não mencione o contexto, o usuário pensa que você está ligado ao site. "
        "Não invente respostas. Se você fizer uma suposição, deixe explícito que é uma suposição baseada nos dados do site."
    )
    
    user_prompt = f"CONTEXTO:\n{context_str}\n\nPERGUNTA DO USUÁRIO: {query}"

    return f"{system_prompt}\n\n{user_prompt}"

def get_gemini_response(query: str, context: List[str]) -> str:
    prompt = build_prompt(query, context)
    response = model.generate_content(prompt)
    return response.text

# Discartable part, just for testing in terminal
while True:
    query = input("Pergunta: ")
    if query.lower() == 'sair':
        break
    
    print("\nPensando...\n")

    results = query_database(query)

    # Making sure we have results and documents
    if results and results["documents"]:
        context_docs = results["documents"][0]
        metadata_docs = results["metadatas"][0]
        
        response = get_gemini_response(query, context_docs)

        ''' Debug if needed
        print("\n--- Resposta ---")
        print(response)
        
        print("\n--- Contexto ---")
        print("\n".join(context_docs))

        print("\n--- Metadados ---")
        for metadata in metadata_docs:
            print(metadata)
        '''