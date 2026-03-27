import asyncio
from embedding import update_database
import json
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from google import genai
from dotenv import load_dotenv
import time
import requests
from bs4 import BeautifulSoup
# For now, using BeautifulSoup to parse the news page and extract links,
# planning to use Crawl4AI for this too in the future

# Configuring Gemini for crawling the site
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client()

# Crawl4AI Configuration with filters to clean the content and generate Markdown
config = CrawlerRunConfig(
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter()
    )
)

# Main function to extract news articles from the IFSP Votuporanga website
async def extract_news():
    url = "https://vtp.ifsp.edu.br/index.php/noticias.html?limit=10"
    print(f"Acessing URL: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error acessing the site. Status: {response.status_code}")
        return

    # First, parse the main news page to find individual news links
    soup = BeautifulSoup(response.content, 'html.parser')
    news_items = soup.find_all('div', class_='tileItem')

    final_data_list = []
    base_url = "https://vtp.ifsp.edu.br"

    for item in news_items:
        title = item.find('h2', class_='tileHeadline').get_text(strip=True)
        link = requests.compat.urljoin(base_url, item.find('a')['href'])
        
        print(f"Processing news: {title}")
        try:
            news_response = requests.get(link, timeout=10)
            if news_response.status_code != 200:
                continue
            
            # Now, parse the individual news page to extract content
            news_soup = BeautifulSoup(news_response.content, 'html.parser')
            content_div = news_soup.find('div', class_='item-page')

            if content_div:
                # Extract publication date if available
                date_span = content_div.find('span', class_='documentPublished')
                publish_date = date_span.get_text(strip=True) if date_span else "Date not found"

                processed_docs = []
                
                # Crawling with Crawl4AI
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url=link, config=config)
        
                if not result.success:
                    print(f"Error accessing news URL {link}: {result.error_message}")
                    return

                clean_markdown = result.markdown.fit_markdown 

                # Sending all the markdown content to Gemini to extract useful paragraphs for RAG context
                prompt = f"""
                Você é um extrator de dados focado em preparar contextos para um sistema de RAG.
                Leia o Markdown abaixo e divida-o em blocos de informação úteis.
                NUNCA omita nomes próprios, tabelas, ganhadores ou datas.

                FORMATO DE SAÍDA:
                Retorne APENAS um JSON válido contendo uma chave "content" que é uma lista de strings.

                CONTEÚDO DA NOTÍCIA (MARKDOWN):
                {clean_markdown}
                """

                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
    
                # Processing everything and preparing the data to be inserted into the database
                try:
                    dados_json = json.loads(response.text)
                    print(f"Success! {len(dados_json.get('content', []))} paragraphs extracted.")
                    # An index to create unique IDs for each paragraph, better to upsert
                    doc_index = 0

                    processed_docs = []

                    for content in dados_json.get("content", []):
                        doc = {
                            "conteudo": content.strip(),
                            "id": f"{link}-{doc_index}",
                            "metadados": {
                                "tipo": "Notícia", "fonte": link,
                                "titulo_noticia": title, "data_publicacao": publish_date
                            }
                        }
                        processed_docs.append(doc)
                        print(processed_docs[-1])  # Debug: print the last processed document
                        doc_index += 1
                               
                    final_data_list.extend(processed_docs)

                except json.JSONDecodeError:
                    print("Error decoding JSON from Gemini.")
                    return []

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Failure acessing {link}: {e}")
            continue
        
        # Sleep to avoid overwhelming the server
        time.sleep(1)

    print("Extraction completed.")
    print(final_data_list)
    update_database(final_data_list)

if __name__ == "__main__":
    print("Starting news extraction from IFSP site...")
    asyncio.run(extract_news())