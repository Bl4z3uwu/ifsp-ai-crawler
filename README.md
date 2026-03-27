# IFSP AI Crawler  

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)  
[![Status](https://img.shields.io/badge/status-Active-success.svg)]()  

## Description  

The IFSP AI Crawler is a Web Scraping application that scans the IFSP Votuporanga website, extracts and organizes raw data, converts it into an embeddings database, and applies the RAG (Retrieval-Augmented Generation) process to answer user queries.  

This project is part of my final research paper and aims to demonstrate the integration of data collection, processing, and artificial intelligence techniques to build an intelligent search system.

---

## Technologies and Libraries  

- **Python**  
- **Requests**  
- **BeautifulSoup**
- **Crawl4AI**
- **ChromaDB**  
- **Google Gemini API**  

---

## Installation and Usage  

1. Clone this repository:  
   ```
   git clone https://github.com/your-username/ifsp-ai-crawler.git
   cd ifsp-ai-crawler
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Set up environment variables in the .env file (e.g., Gemini API key).
6. Run the project:
   ```
   python main.py
   ```
   

