
from functions import get_video_code, fetch_transcript, transcribe_youtube, detect_language, show_full_text, remove_non_alphanumeric,remove_line_breaks,extract_text_from_pdf, save_text ,save_pdf_file,extract_text_from_pdf_plumber,extract_text_from_pdf_with_columns_and_footer_filter
from summary_transformers import MultilingualSummarizer,T5Summarizer, summarize_text, split_text, summarize_text_tokenizer, split_text_tokenizer
from summary_llms import summarize_with_gptneo, summarize_with_distilgpt2
import os


# Define folders to save uploaded files and the final transcriptions
input_folder = "raw_data"
transcription_folder = "processed_data"
summary_folder = "output_data"

pdf_file_name = "uploaded_pdf.pdf"
pdf_transcription_name = "pdf_text.txt"
video_transcription_name = "video_text.txt"
scrapping_transcription_name = "scrapping_text.txt"

input_path = os.path.join(input_folder, pdf_file_name)

output_path_pdf = os.path.join(transcription_folder, pdf_transcription_name)
output_path_video = os.path.join(transcription_folder, video_transcription_name)
output_path_scrapping = os.path.join(transcription_folder, scrapping_transcription_name)

summary_path_pdf = os.path.join(summary_folder, pdf_file_name)
summary_path_video =  os.path.join(summary_folder, video_transcription_name)
summary_path_scrapping =  os.path.join(summary_folder, scrapping_transcription_name)


CHUNK_SIZE = 950
MODEL = MultilingualSummarizer()


def pdf_pipeline(pdf_file, summary_length):
 
    os.makedirs(input_folder, exist_ok=True)
    save_pdf_file(pdf_file, input_path)

    raw_text = extract_text_from_pdf_with_columns_and_footer_filter(input_path)
    #text_no_line_breaks = remove_line_breaks(raw_text)
    #clean_text = remove_non_alphanumeric(text_no_line_breaks)

    #os.makedirs(transcription_folder, exist_ok=True)
    #save_text(clean_text, output_path_pdf)

    #summarizer = MODEL 
    #summarized_text = summarize_text(raw_text, summarizer, max_length=summary_length, chunk_size=CHUNK_SIZE)
    summarized_text = summarize_with_gptneo(raw_text)

    #os.makedirs(summary_folder, exist_ok=True)
    #save_text(summarized_text, summary_path_pdf)

    return summarized_text


def video_pipeline(video_url, summary_length):

    video_code = get_video_code(video_url)
    transcript = fetch_transcript(video_code, languages=['es', 'en'])
    raw_text = transcribe_youtube(transcript)

    #os.makedirs(transcription_folder, exist_ok=True)
    #save_text(raw_text, output_path_video)

    #summarizer = MODEL  # Carga el modelo de resumen
    #summarized_text = summarize_text(raw_text, summarizer, max_length=summary_length, chunk_size=CHUNK_SIZE)
    summarized_text = summarize_with_distilgpt2(raw_text)

    os.makedirs(summary_folder, exist_ok=True)
    save_text(summarized_text, summary_path_video)

    return summarized_text


def scrapping_pipeline(raw_text, summary_length):

    #summarizer = MODEL  # Carga el modelo de resumen
    #summarized_text = summarize_text(raw_text, summarizer, max_length=summary_length, chunk_size=CHUNK_SIZE)
    summarized_text = summarize_with_gptneo(raw_text)

    os.makedirs(summary_folder, exist_ok=True)
    save_text(summarized_text, summary_path_scrapping)

    return summarized_text