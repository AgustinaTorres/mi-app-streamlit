# scraping_functions.py

import requests
from bs4 import BeautifulSoup
import html
import html5lib
import re
import os

# Define a dictionary with all the news options
news_sites = [
    {
        "name": "El pais",
        "url": "https://elpais.com/",
        "header": {
            "tag": "div",
            "class": "sm _df"
        },
        "news_list": [
            {"tag": "h2", "class": "c_t", "title": "Titulares"},
            {"tag": "h2", "class": "c_t c_t-i", "title": "Opiniones"},
            {"tag": "div", "class": "b-t_a _df", "title": "Lo mas visto"}
        ],
        "selected_new": {
            "tag": "h1",
            "class": ["a_t"]
        }
    },
    {
        "name": "NBC",
        "url": "https://www.nbcnews.com/",
        "header": {
            "tag": "div",
            "class": "menu-section menu-section-sections menu-section-main"
        },
        "news_list": [
            {"tag": "h2", "class": ["article-hero-headline__htag lh-none-print black-print article-hero-headline__htag--live-breaking", "multistoryline__headline founders-cond fw6 large noBottomSpace"], "title": "Header news"},
            {"tag": "h2", "class": "styles_headline__ice3t", "title": "Top stories and videos"}
        ],
        "selected_new": {
            "tag": "h1",
            "class": ["article-hero-headline__htag lh-none-print black-print"]
        }
    },
       {
        "name": "elDiario.es",
        "url": "https://www.eldiario.es/",
        "header": {
            "tag": "div",
            "class": "menu-cabecera-desktop"
        },
        "news_list": [
            {"tag": "h2", "class": "ni-title", "title": "Titulares"}
        ],
        "selected_new": {
            "tag": "h1",
            "class": ["title"]
        }
    }
]


def get_user_web_selection(selected_news_site):
    for new in news_sites:
        if new["name"].lower() == selected_news_site.lower():
            return new

def scrape_web_header(url, header_tag, header_class):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        header_div = soup.find(header_tag, class_=re.compile(r'\b' + re.escape(header_class) + r'\b'))
        if header_div:
            header_options = header_div.find_all("a")
            return [{"section": option.get_text(strip=True), "url": option.get("href"), "categories": []} for option in header_options]
        else:
            print("No se encontró el div con las opciones del encabezado.")
    else:
        print(f"Error al acceder a {url}")
    return []

def scrape_news(user_section_selection, user_web_selection):
    url = user_section_selection["url"]
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html5lib')
        news_list = []
        
        for dicc in user_web_selection["news_list"]:
            news_tags = soup.find_all(dicc["tag"], class_=dicc["class"])
            news_links = [link.a["href"] for link in news_tags]
            
            for news_url in news_links:
                news_response = requests.get(news_url)
                news_soup = BeautifulSoup(news_response.content, 'lxml')
                title = news_soup.find(user_web_selection["selected_new"]["tag"], class_=user_web_selection["selected_new"]["class"])
                paragraphs = news_soup.find_all('p')

                # Obtener el texto limpio de los párrafos
                article_text = ' '.join([html.unescape(p.get_text(strip=True)) for p in paragraphs])

                if title and article_text:
                    news_list.append({
                        "title": title.text.strip(),
                        "url": news_url,
                        "content": article_text  # Guardamos también el contenido
                    })
        
        return news_list
    else:
        print(f"Error al acceder a {url}")
        return []


def save_scrapping_transcription(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

 




