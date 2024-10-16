from transformers import BartTokenizer, BartForConditionalGeneration

class BARTSummarizer:
    def __init__(self, model_name='facebook/bart-large-cnn'):
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)

    def summarize(self, text, max_length=256, num_beams=5, length_penalty=2.0, no_repeat_ngram_size=3):
        # Tokenizar el texto
        inputs = self.tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)

        # Generar el resumen
        summary_ids = self.model.generate(
            inputs,
            max_length=max_length,
            num_beams=num_beams,
            length_penalty=length_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            early_stopping=True
        )

        # Decodificar el resumen
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
