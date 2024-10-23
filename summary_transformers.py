# Importar librerias
import re
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast, pipeline, AutoTokenizer,T5Tokenizer, T5ForConditionalGeneration
import os
from IPython.display import display, Markdown


class MultilingualSummarizer:
    def __init__(self, model_name='facebook/mbart-large-50-many-to-many-mmt'):
        self.tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
        self.model = MBartForConditionalGeneration.from_pretrained(model_name)

    def summarize(self, text, source_lang='es_XX', target_lang='es_XX', max_length= 150, num_beams=5, length_penalty=2, no_repeat_ngram_size=3):
        self.tokenizer.src_lang = source_lang
        forced_bos_token_id = self.tokenizer.lang_code_to_id[target_lang]

        inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)

        summary_ids = self.model.generate(
            **inputs,
            max_length=max_length,
            forced_bos_token_id=forced_bos_token_id,
            num_beams=num_beams,
            length_penalty=length_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            early_stopping=False
        )

        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

class T5Summarizer:
    def __init__(self, model_name='t5-base'):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    def summarize(self, text, max_length=150, num_beams=5, length_penalty=2, no_repeat_ngram_size=3):
        inputs = self.tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = self.model.generate(
            inputs,
            max_length=max_length,
            #min_length=min_length,
            num_beams=num_beams,
            length_penalty=length_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            early_stopping=False
        )
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

def split_text(text, max_length):
    sentences = text.split('. ')  # Use period as delimiter
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += ('. ' if current_chunk else '') + sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def split_text_tokenizer(text, tokenizer, chunk_size):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    input_ids = inputs['input_ids'][0]
    
    chunks = []
    for i in range(0, len(input_ids), chunk_size):
        chunk_ids = input_ids[i:i+chunk_size]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        chunks.append(chunk_text)
    
    return chunks

def summarize_text(text, summarizer, max_length, chunk_size):
    chunks = split_text(text, chunk_size)
    summaries = []
    for chunk in chunks:
        summary = summarizer.summarize(chunk, max_length=max_length)
        summaries.append(summary)
    return ' '.join(summaries)













# Modificamos la función principal de resumen para ajustar max_length basado en la longitud del chunk
def summarize_text_tokenizer(text, summarizer, chunk_size):
    max_length_ratio=0.3
    chunks = split_text_tokenizer(text, summarizer.tokenizer, chunk_size)
    summaries = []
    
    for chunk in chunks:
        # Calcula max_length basado en la proporción del tamaño del chunk
        max_length = int(len(chunk) * max_length_ratio)
        summary = summarizer.summarize(
            chunk, 
            max_length=max_length, 
            num_beams=7,  # Ajustamos num_beams para mejorar la calidad
            length_penalty=1.5,  # Penalización ajustada para permitir algo más de longitud
            early_stopping=True  # Detenemos la generación tempranamente si es necesario
        )
        summaries.append(summary)
    
    return ' '.join(summaries)