from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from embedding import query_database
from typing import List

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client()

model = "gemini-3-flash-preview"

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
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

# Creating the API with Flask

template_dir = os.path.abspath('web')
app = Flask('app',template_folder=template_dir)
app.static_folder = 'static'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.get_json().get('query')
    results = query_database(user_input)
    response = get_gemini_response(user_input, results['documents'][0])
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
'''
Test in terminal
user_input = input("Digite sua pergunta: ")
results = query_database(user_input)
print(get_gemini_response(user_input, results['documents'][0]))
'''


''' Debug if needed
    print("\n--- Resposta ---")
    print(response)
    
    print("\n--- Contexto ---")
    print("\n".join(context_docs))

    print("\n--- Metadados ---")
    for metadata in metadata_docs:
        print(metadata)
'''