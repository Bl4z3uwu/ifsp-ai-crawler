import requests
from bs4 import BeautifulSoup
import embedding
import time

def extract_news():
    url = "https://vtp.ifsp.edu.br/index.php/noticias.html?limit=1"
    print(f"Acessando URL: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Erro ao acessar o site. Status: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    news_items = soup.find_all('div', class_='tileItem')

    final_data_list = []
    base_url = "https://vtp.ifsp.edu.br"

    for item in news_items:
        title = item.find('h2', class_='tileHeadline').get_text(strip=True)
        link = requests.compat.urljoin(base_url, item.find('a')['href'])
        
        print(f"Processando notícia: {title}")
        try:
            news_response = requests.get(link, timeout=10)
            if news_response.status_code != 200:
                continue

            news_soup = BeautifulSoup(news_response.content, 'html.parser')
            content_div = news_soup.find('div', class_='item-page')

            if content_div:
                date_span = content_div.find('span', class_='documentPublished')
                publish_date = date_span.get_text(strip=True) if date_span else "Data não encontrada"

                processed_docs = []
                
                all_paragraphs = content_div.find_all('p', attrs={'style': 'text-align: justify;'})
                
                # Indice separado para os IDs para garantir que sejam únicos por página
                doc_index = 0

                for content in all_paragraphs:
                    text = content.get_text(strip=True)      
                    doc = {
                        "conteudo": text,
                        "id": f"{link}-{doc_index}",
                        "metadados": {
                            "tipo": "Notícia", "fonte": link,
                            "titulo_noticia": title, "data_publicacao": publish_date
                        }
                    }
                    processed_docs.append(doc)
                    doc_index += 1
                    
                final_data_list.extend(processed_docs)

        except requests.exceptions.RequestException as e:
            print(f"  [ERRO] Falha ao acessar {link}: {e}")
            continue
        
        time.sleep(1)

    print("Extração concluída.")
    print(final_data_list)
    embedding.update_database(final_data_list)

if __name__ == "__main__":
    print("Iniciando a extração de notícias do IFSP...")
    extract_news()