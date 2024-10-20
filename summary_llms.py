from transformers import GPTNeoForCausalLM, GPT2Tokenizer, AutoTokenizer, AutoModelForCausalLM
import torch


def summarize_with_gptneo(text):

    # Cargar el modelo y el tokenizer
    model_name = "EleutherAI/gpt-neo-125M"
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)

    # Establecer pad_token_id
    model.config.pad_token_id = model.config.eos_token_id

    # Texto de entrada
    prompt = (
        "Por favor, resume el siguiente texto en un parrafo y que termine con punto. "
        "El resumen debe ser claro y coherente en español, sin incluir información no solicitada ni texto en inglés. "
        f"{text}\n"
        "Resumen:"
        )

    # Tokenizar el texto de entrada
    input_ids = tokenizer.encode(prompt, return_tensors='pt',  max_length=1000)

    # Crear la atención mask
    attention_mask = (input_ids != model.config.pad_token_id).long()

    # Generar texto
    output = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=150,
        num_return_sequences=1,
        temperature=0.7,
        top_k=50,
        do_sample=True
    )

    # Decodificar y mostrar el resultado
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Limpiar el texto obtenido de manera que finalice en un punto.
    last_period_index = generated_text.rfind('.')
    if last_period_index != -1:
        generated_text = generated_text[:last_period_index + 1]  # Incluir el punto

    return generated_text


def summarize_with_distilgpt2(text):

    # Cargar el tokenizador y modelo DistilGPT-2
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    model = AutoModelForCausalLM.from_pretrained("distilgpt2")

    # Establecer el pad_token
    tokenizer.pad_token = tokenizer.eos_token  # Usar el token de fin de secuencia como el de relleno

    prompt =  (
        "Por favor, resume el siguiente texto en un parrafo que finalice en un punto"
        "El resumen debe ser claro y coherente en español, sin incluir información no solicitada ni texto en inglés. "
        f"{text}\n"
        "Resumen:"
        )

    # Tokenizar el prompt
    inputs = tokenizer(prompt, return_tensors="pt", max_length=1000, truncation=True, padding=True)
    
    # Crear la atención de la máscara
    attention_mask = (inputs['input_ids'] != tokenizer.pad_token_id).long()

    # Generar el resumen
    outputs = model.generate(
        inputs.input_ids,   
        attention_mask=attention_mask,  # Pasar la máscara de atención
        max_new_tokens=150,  # Cambia a max_new_tokens en lugar de max_length
        num_beams=5,
        no_repeat_ngram_size=2,
        early_stopping=False
    )
    
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Limpiar el texto obtenido de manera que finalice en un punto.
    last_period_index = summary.rfind('.')
    if last_period_index != -1:
        summary = summary[:last_period_index + 1]  # Incluir el punto

    return summary