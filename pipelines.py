# Importar librerias
from functions import get_video_code, fetch_transcript, transcribe_youtube, remove_non_alphanumeric,remove_line_breaks,extract_text_from_pdf, save_text ,save_pdf_file,extract_text_from_pdf_plumber,extract_text_from_pdf_with_columns_and_footer_filter, translate_to_spanish
from summary_llms import summarize_with_gptneo, summarize_with_distilgpt2
import streamlit as st
import os

# Carpetas donde se guardan los inputs y outputs.
input_folder = "raw_data"
transcription_folder = "processed_data"
summary_folder = "output_data"

# Fichero de pdf a adjuntar y textos obtenidos de las transcripciones/resumenes finales.
pdf_file_name = "uploaded_pdf.pdf"
pdf_transcription_name = "pdf_text.txt"
video_transcription_name = "video_text.txt"
scrapping_transcription_name = "scrapping_text.txt"

# Paths para guardar el pdf y textos transcriptos.
input_path = os.path.join(input_folder, pdf_file_name)
output_path_pdf = os.path.join(transcription_folder, pdf_transcription_name)
output_path_video = os.path.join(transcription_folder, video_transcription_name)
output_path_scrapping = os.path.join(transcription_folder, scrapping_transcription_name)

# Paths para guardar los textos resumidos.
summary_path_pdf = os.path.join(summary_folder, pdf_file_name)
summary_path_video =  os.path.join(summary_folder, video_transcription_name)
summary_path_scrapping =  os.path.join(summary_folder, scrapping_transcription_name)

def pdf_pipeline(pdf_file, model_name):
    """
    Procesa un ficher pdf, obtiene la transcripción y genera un resumen.

    Args:
        pdf_file (str): el fichero pdf cargado por el usuario .
        model_name (str) : nombre del modelo de resumen seleccionado por el usuario /definido por default.

    Returns:
        str: El texto resumido generado.
    """
 
    os.makedirs(input_folder, exist_ok=True)
    save_pdf_file(pdf_file, input_path)


    raw_text = extract_text_from_pdf(input_path)

    #Funciones de limpieza, no implementadas finalmente.
    #text_no_line_breaks = remove_line_breaks(raw_text)
    #clean_text = remove_non_alphanumeric(text_no_line_breaks)

    os.makedirs(transcription_folder, exist_ok=True)
    save_text(raw_text, output_path_pdf)
    
    if model_name == "EleutherAI/gpt-neo-125M":
        summarized_text = summarize_with_gptneo(raw_text)
    else:
        summarized_text = summarize_with_distilgpt2(raw_text)

    os.makedirs(summary_folder, exist_ok=True)
    save_text(summarized_text, summary_path_pdf)

    return summarized_text

def video_pipeline(video_url, model_name): 
    """
    Procesa un video de YouTube, obtiene la transcripción y genera un resumen.

    Args:
        video_url (str): URL del video de YouTube a procesar.
        model_name (str) : nombre del modelo de resumen seleccionado por el usuario /definido por default.


    Returns:
        str: El texto resumido generado.
    """

    video_code = get_video_code(video_url)
    transcript = fetch_transcript(video_code, languages=['es', 'en'])
    raw_text = transcribe_youtube(transcript)

    if not raw_text:
        raise ValueError("La transcripción está vacía o no se ha obtenido correctamente.")

    os.makedirs(transcription_folder, exist_ok=True)
    save_text(raw_text, output_path_video)

    if model_name == "EleutherAI/gpt-neo-125M":
        summarized_text = summarize_with_gptneo(raw_text)
    else:
        summarized_text = summarize_with_distilgpt2(raw_text)

    os.makedirs(summary_folder, exist_ok=True)
    save_text(summarized_text, summary_path_video)

    return summarized_text

def scrapping_pipeline(raw_text, model_name, new_site):

    os.makedirs(transcription_folder, exist_ok=True)
    save_text(raw_text, output_path_scrapping)

    if new_site == "NBC":
        translated_text = translate_to_spanish(raw_text)
    else:
        translated_text = raw_text
    """
    Procesa una noticia obtenida de periodico en linea, obtiene la transcripción y genera un resumen.

    Args::
        raw_text (str): el texto de la noticia obtenido a traves de web scrapping.
        model_name (str) : nombre del modelo de resumen seleccionado por el usuario /definido por default.


    Returns:
        str: El texto resumido generado.
    """
    
    if model_name == "EleutherAI/gpt-neo-125M":
        summarized_text = summarize_with_gptneo(translated_text)
    else:
        summarized_text = summarize_with_distilgpt2(translated_text)

    os.makedirs(summary_folder, exist_ok=True)
    save_text(summarized_text, summary_path_scrapping)

    return summarized_text

