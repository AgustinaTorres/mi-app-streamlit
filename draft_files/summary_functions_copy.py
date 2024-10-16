import re
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

class MultilingualSummarizer:
    def __init__(self, model_name='facebook/mbart-large-50-many-to-many-mmt'):
        self.tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
        self.model = MBartForConditionalGeneration.from_pretrained(model_name)

    def summarize(self, text, source_lang='es_XX', target_lang='es_XX', max_length=200, num_beams=5, length_penalty=1.5, no_repeat_ngram_size=2):
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
            early_stopping=True
        )

        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary


def split_text_into_sentences(text, max_chunk_length):
    # Dividimos el texto por oraciones
    sentences = re.split(r'(?<=[.!?]) +', text)  # Dividir en oraciones completas
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_length:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def is_sentence_complete(text):
    # Verificamos si el texto termina con un signo de puntuación adecuado.
    return bool(re.search(r'[.!?]$', text))

def postprocess_summary(summary):
    sentences = re.split(r'(?<=[.!?]) +', summary)
    if not is_sentence_complete(sentences[-1]):
        sentences = sentences[:-1]  # Eliminar la última oración si está incompleta
    return ' '.join(sentences)

def summarize_text(text, summarizer, max_length=200, chunk_size=950):
    chunks = split_text_into_sentences(text, chunk_size)
    summaries = []
    for chunk in chunks:
        summary = summarizer.summarize(chunk, max_length=max_length)
        summary = postprocess_summary(summary)  # Revisar si la última oración está completa
        summaries.append(summary)
    return ' '.join(summaries)
