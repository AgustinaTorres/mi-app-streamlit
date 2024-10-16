#Import libraries
import fitz 
import os
import re
import pdfplumber
import streamlit as st
import requests
from langdetect import detect
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from IPython.display import Markdown, display
import requests
from bs4 import BeautifulSoup
import html
import html5lib

#------------------------------------------------- PDF FUNCTIONS------------------------------------------
#Save pdf file
def save_pdf_file(pdf_file, input_path):
    with open(input_path, "wb") as f:
        f.write(pdf_file.getbuffer())
   

#Function to read pdf
def extract_text_from_pdf(pdf_path):

    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Initialize an empty string to hold the extracted text
    text = []

    # Iterate over all the pages in the PDF
    for page_num in range(doc.page_count):
        # Load the current page
        page = doc.load_page(page_num)

        # Extract the text from the page
        page_text = page.get_text("text")

        # Append the text of the current page to the list
        text.append(page_text)

    # Close the PDF document
    doc.close()

    raw_text = ''.join(text)

    # Join the list into a single string and return the extracted text
    return raw_text


# Read pdf with PDFPlumber
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

#-------------------------------------- VIDEO FUNCTIONS ------------------------------------------
# Extract the video code from the URL
def get_video_code(url):
    return url.split("?v=")[-1]

# Fetch the transcript from YouTube
def fetch_transcript(video_code, languages=['es', 'en']):
    try:
        # Attempt to retrieve manually created transcript
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_code)
        transcript = transcript_list.find_manually_created_transcript(languages)
    except (NoTranscriptFound, TranscriptsDisabled):
        try:
            # If no manual transcript, try to fetch auto-generated transcript
            transcript = transcript_list.find_generated_transcript(languages)
        except Exception as e:
            raise Exception(f"No transcripts available for this video. Error: {str(e)}")
    
    return transcript


# Transcribe the video by fetching the text from the transcript
def transcribe_youtube(transcript):
    try:
        transcript_data = transcript.fetch()
        raw_text = " ".join([item['text'] for item in transcript_data])
        return raw_text
    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")
    

# Detect the language of the given text
def detect_language(text):
    """
    Detects the language of the provided text.
    
    :param text: Text to analyze
    :return: Detected language as a string
    """
    try:
        return detect(text)
    except:
        return "Language detection failed"

#-------------------------------------- SCRAPPING FUNCTIONS----------------------------------------

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




#-------------------------------------CLEANING TEXT ------------------------------------------------------------

def remove_line_breaks(text):
    # Remover saltos de línea excesivos
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text

def remove_non_alphanumeric(text):
    # Eliminar caracteres no alfanuméricos si es necesario
    #text = re.sub(r'[^A-Za-z0-9\s.,;:?!]', '', text)
    text = re.sub(r'[^A-Za-z0-9áéíóúñüÁÉÍÓÚÑÜ.,;:\s]', '', text)
    return text


def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)  # Elimina espacios extra
    text = text.strip()  # Elimina espacios en los extremos
    return text


#---------------------------SAVING TEXT (TRANSCRIPTIONS ANS SUMMARIES)------------------------------------------------------------

#Save the transcription
def save_text(text,path):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)


# ----------------------------- PRINTING RESULT --------------------------------------------
# Show the transcribed text
def show_full_text(text):
    display(Markdown(text))






import fitz  # PyMuPDF

def extract_text_from_pdf_with_columns_and_footer_filter(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Initialize an empty string to hold the extracted text
    full_text = []

    # Iterate over all the pages in the PDF
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        # Get the dimensions of the page
        page_width = page.rect.width
        page_height = page.rect.height

        # Define the footer area height to exclude
        footer_height = 100  # Adjust this value if needed

        # Define the rectangles for the left and right columns, excluding the footer area
        left_column = fitz.Rect(0, 0, page_width / 2, page_height - footer_height)  # Left column
        right_column = fitz.Rect(page_width / 2, 0, page_width, page_height - footer_height)  # Right column

        # Extract text from the left and right columns
        left_text = page.get_text("text", clip=left_column)
        right_text = page.get_text("text", clip=right_column)

        # Combine the text from both columns
        combined_text = left_text + "\n" + right_text

        # Append the text of the current page to the list
        full_text.append(combined_text)

    # Close the PDF document
    doc.close()

    # Join the list into a single string and return the extracted text
    return ''.join(full_text)
