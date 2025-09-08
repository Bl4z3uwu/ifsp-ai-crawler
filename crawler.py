import requests
from bs4 import BeautifulSoup
import embedding
import time

# Main function to extract news articles from the IFSP Votuporanga website
def extract_news():
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
                
                # Since all the news paragraphs are justified, we can filter by style
                all_paragraphs = content_div.find_all('p', attrs={'style': 'text-align: justify;'})
                
                # An index to create unique IDs for each paragraph, better to upsert
                doc_index = 0

                for content in all_paragraphs:
                    # Making sure to skip empty paragraphs
                    text = content.get_text(strip=True)      
                    if not text:
                        continue
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
            print(f"  [ERROR] Failure acessing {link}: {e}")
            continue
        
        # Sleep to avoid overwhelming the server
        time.sleep(1)

    print("Extraction completed.")
    print(final_data_list)
    embedding.update_database(final_data_list)

if __name__ == "__main__":
    print("Starting news extraction from IFSP site...")
    extract_news()