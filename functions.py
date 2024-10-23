# Importar librerias
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from IPython.display import Markdown, display
from transformers import MarianMTModel, MarianTokenizer
from bs4 import BeautifulSoup
#import pdfplumber
import fitz 
import streamlit as st
import requests
import html
import html5lib
import os
import re

#-------------------------------------- FUNCIONES PDF ------------------------------------------

def save_pdf_file(pdf_file, input_path):
    with open(input_path, "wb") as f:
        f.write(pdf_file.getbuffer())
   
def extract_text_from_pdf(pdf_path):

    # Abrir el fichero PDF.
    doc = fitz.open(pdf_path)

    # Definir una variable para guardar el texto extraido.
    text = []

    # Iterar sobre todas las paginas del PDF.
    for page_num in range(doc.page_count):
        # Cargar la pagina actual
        page = doc.load_page(page_num)

        # Extraer el texto.
        page_text = page.get_text("text")

        # Guardar el texto en la variable o concatenarlo al texto existente.
        text.append(page_text)

    # Cerrar el fichero PDF.
    doc.close()

    raw_text = ''.join(text)

    return raw_text

def extract_text_from_pdf_plumber(pdf_path):
    raw_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

             # Definir las coordenadas para la primera y segunda columna
            left_column = page.within_bbox((0, 0, page.width / 2, page.height))  # Primera columna (izquierda)
            right_column = page.within_bbox((page.width / 2, 0, page.width, page.height))  # Segunda columna (derecha)
            
            # Extraer el texto de cada columna
            left_text = left_column.extract_text()
            right_text = right_column.extract_text()
            
            # Combinar el texto en el orden correcto
            raw_text += left_text + "\n" + right_text + "\n"

            #raw_text += page.extract_text()
    return raw_text

def extract_text_from_pdf_with_columns_and_footer_filter(pdf_path):
    
    doc = fitz.open(pdf_path)

    full_text = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        page_width = page.rect.width
        page_height = page.rect.height

        footer_height = 100  

        left_column = fitz.Rect(0, 0, page_width / 2, page_height - footer_height)  
        right_column = fitz.Rect(page_width / 2, 0, page_width, page_height - footer_height) 

        left_text = page.get_text("text", clip=left_column)
        right_text = page.get_text("text", clip=right_column)

        combined_text = left_text + "\n" + right_text

        full_text.append(combined_text)

    doc.close()

    return ''.join(full_text)

#-------------------------------------- FUNCIONES VIDEO ------------------------------------------

def get_video_code(url):
    return url.split("?v=")[-1]

def fetch_transcript(video_code, languages=['es', 'en']):
    try:
        # Intento de recuperar transcripcion creada manualmente.
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_code)
        transcript = transcript_list.find_manually_created_transcript(languages)
    except (NoTranscriptFound, TranscriptsDisabled):
        try:
            # Si no hay transcripcion manual, recuperar transcripcion generada automaticamente.
            transcript = transcript_list.find_generated_transcript(languages)
        except Exception as e:
            raise Exception(f"No transcripts available for this video. Error: {str(e)}")
    
    return transcript

def transcribe_youtube(transcript):
    try:
        transcript_data = transcript.fetch()
        raw_text = " ".join([item['text'] for item in transcript_data])
        return raw_text
    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")
    
#--------------------------------------  DATA Y FUNCIONES WEB SCRAPPING ----------------------------------------

# Lista de periodicos web junto a sus caracteristicas individuales requeridas
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

#------------------------------------- FUNCIONES DE LIMPIEZA DE TEXTO ------------------------------------------------------------

def remove_line_breaks(text):
    # Remover saltos de línea excesivos
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text

def remove_non_alphanumeric(text):
    # Eliminar caracteres no alfanuméricos si es necesario
    text = re.sub(r'[^A-Za-z0-9áéíóúñüÁÉÍÓÚÑÜ.,;:\s]', '', text)
    return text

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)  # Elimina espacios extra
    text = text.strip()  # Elimina espacios en los extremos
    return text

def translate_to_spanish(text, max_length=512):
    # Cargar el modelo y tokenizer de traducción
    model_name = "Helsinki-NLP/opus-mt-en-es"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    
    # Dividir el texto en fragmentos si es muy largo
    text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    translated_chunks = []
    
    # Traducir cada fragmento por separado
    for chunk in text_chunks:
        translated = model.generate(**tokenizer(chunk, return_tensors="pt", padding=True, truncation=True))
        translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
        translated_chunks.append(translated_text)
    
    # Unir todos los fragmentos traducidos
    return " ".join(translated_chunks)

#------------------------------------- FUNCIONES DE GUARDADO (FICHEROS Y TEXTOS) ------------------------------------------------------------

def save_text(text,path):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)

# ----------------------------- FUNCION DE IMPRESION DE TEXTO --------------------------------------------

def show_full_text(text):
    display(Markdown(text))

def show_loading_message():
    with st.spinner("Cargando, por favor espera..."):
        yield  # Esta línea permite que el spinner se muestre hasta que se complete el bloque de código


