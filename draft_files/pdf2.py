import fitz  # PyMuPDF
import io

def extract_text_from_pdf(pdf_file_stream):
    """
    Extrae el texto de un archivo PDF cargado en un flujo de bytes.

    :param pdf_file_stream: Flujo de bytes del archivo PDF cargado por Streamlit.
    :return: Texto extraído del PDF.
    """
    # Leer el archivo PDF en un flujo de bytes
    pdf_bytes = pdf_file_stream.read()
    
    # Abrir el archivo PDF desde el flujo de bytes
    doc = fitz.open(stream=pdf_bytes, filetype='pdf')

    # Guardar el texto en una variable
    text = ""

    # Iterar a través de todas las páginas del PDF
    for page_num in range(doc.page_count):
        # Obtener la página actual
        page = doc.load_page(page_num)

        # Obtener el texto de la página
        text += page.get_text("text")

    # Cerrar el documento PDF
    doc.close()
    return text
