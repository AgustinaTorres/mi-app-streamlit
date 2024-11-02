# Importar librerias
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, AutoTokenizer, AutoModelForCausalLM
import streamlit as st


def summarize_with_gptneo(text):
    # Cargar el modelo y el tokenizer
    model_name = st.session_state["ajustes"]["model_name"]
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
   

    # Establecer pad_token_id
    model.config.pad_token_id = model.config.eos_token_id

    # Texto de entrada
    prompt = (
        "Por favor, resume el siguiente texto **EN ESPAÑOL**. "
        "El resumen no debe incluir indices ni avisos de suscripciones."
        "El resumen debe ser claro y coherente, sin incluir información no solicitada ni texto en inglés. "
        f"{text}\n"
        "Resumen:"
    )

    # Tokenizar el texto de entrada
    input_ids = tokenizer.encode(prompt, return_tensors='pt', max_length=1500, truncation= True)

    # Crear la atención mask
    attention_mask = (input_ids != model.config.pad_token_id).long()

    # Parámetros de generación
    max_new_tokens = int(st.session_state["ajustes"]["summary_length"])  # Convertir a entero
    temperature = float(st.session_state["ajustes"]["temperature"])  # Convertir a float si es necesario
    mode = st.session_state["ajustes"]["mode"]

    if mode == "sampling":
        output = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            num_return_sequences=1,
            temperature=temperature,
            top_k=50,
            do_sample=True
        )
    elif mode == "beam search":
        output = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            num_beams=5,  # Define el número de beams
            no_repeat_ngram_size=2,
            early_stopping=True  # Aplica en beam search
        )

    # Decodificar y mostrar el resultado
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Encontrar el índice donde comienza el resumen
    start_index = generated_text.lower().find("inglés.") + len("inglés.")

    # Comprobar si se encontró "inglés." y recortar el texto
    if start_index != -1:
        summary = generated_text[start_index:].strip()  # Extraer el resumen y quitar espacios
    else:
        summary = generated_text  # Si no se encuentra, usar todo el texto

    # Limpiar el texto obtenido para que finalice en un punto.
    last_period_index = summary.rfind('.')
    if last_period_index != -1:
        summary = summary[:last_period_index + 1]  # Incluir el punto

    return summary

def summarize_with_distilgpt2(text):

    # Cargar el tokenizador y modelo DistilGPT-2
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    model = AutoModelForCausalLM.from_pretrained("distilgpt2")

    # Establecer el pad_token
    tokenizer.pad_token = tokenizer.eos_token  # Usar el token de fin de secuencia como el de relleno

    prompt = (
        "Por favor, resume el siguiente texto en un párrafo que finalice en un punto. "
        "El resumen debe ser claro y coherente en español, sin incluir información no solicitada ni texto en inglés. "
        f"{text}\n"
        "Resumen:"
    )

    # Tokenizar el prompt
    inputs = tokenizer(prompt, return_tensors="pt", max_length=1000, truncation=True, padding=True)

    # Crear la atención de la máscara
    attention_mask = (inputs['input_ids'] != tokenizer.pad_token_id).long()

    # Parámetros de generación
    max_new_tokens = st.session_state["ajustes"]["summary_length"]
    temperature = st.session_state["ajustes"]["temperature"]
    mode = st.session_state["ajustes"]["mode"]

    if mode == "sampling":
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            num_return_sequences=1,
            temperature=temperature,
            top_k=50,
            do_sample=True
        )
    elif mode == "beam search":
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            num_beams=5,
            no_repeat_ngram_size=2,
            early_stopping=True  # Aplica en beam search
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

   # Encontrar el índice donde comienza el resumen
    start_index = generated_text.lower().find("inglés.") + len("inglés.")

    # Comprobar si se encontró "inglés." y recortar el texto
    if start_index != -1:
        summary = generated_text[start_index:].strip()  # Extraer el resumen y quitar espacios
    else:
        summary = generated_text  # Si no se encuentra, usar todo el texto

    # Limpiar el texto obtenido para que finalice en un punto.
    last_period_index = summary.rfind('.')
    if last_period_index != -1:
        summary = summary[:last_period_index + 1]  # Incluir el punto

    return summary



