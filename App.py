# Importar librerias
import streamlit as st
from streamlit_option_menu import option_menu
from pipelines import pdf_pipeline, video_pipeline, scrapping_pipeline
from functions import get_user_web_selection, scrape_web_header, scrape_news, news_sites
import re
import os


# Configurar el título principal y la disposición de la página
st.set_page_config(page_title="TRABAJO FINAL DE MASTER - Torres Moray, Agustina", layout="wide")

def show_loading_message():
    with st.spinner("Cargando, por favor espera..."):
        yield  # Esta línea permite que el spinner se muestre hasta que se complete el bloque de código


# --------------------------------------------- DISEÑO DE PAGINAS---------------------------------------------------------------------

# Estilo de fondo
page_bg_img = '''
<style>
.stApp {
    background-image: url("https://img.freepik.com/fotos-premium/fondo-negocio-abstracto-mundo_476363-2814.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

body::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.25); /* Oscurece el fondo (negro con 50% de opacidad) */
    z-index: -1; /* Asegúrate de que esté detrás del contenido */
}

/* CSS para las iniciales en la esquina superior derecha */
.initials {
    position: absolute;
    top: 20px; /* Ajusta este valor para cambiar la distancia desde la parte superior */
    right: 20px; /* Ajusta este valor para cambiar la distancia desde la derecha */
    color: white; /* Color del texto */
    font-size: 20px; /* Tamaño de la fuente */
    font-weight: bold; /* Negrita */
    z-index: 999; /* Asegúrate de que el texto esté en la parte superior */
}
</style>
'''

# Aplicar el estilo de fondo
st.markdown(page_bg_img, unsafe_allow_html=True)

# Mostrar iniciales en la esquina superior derecha
st.markdown('<div class="initials">ATM</div>', unsafe_allow_html=True)  # Cambia "AT" por tus iniciales

# Definir estilos comunes
menu_styles = {
    "container": {"padding": "10!important", "background-color": "#63a7cf"},
    "icon": {"color": "white", "font-size": "15px"},  # Estilo de los íconos
    "nav-link": {
        "font-size": "16px",
        "text-align": "left",
        "margin": "0px",
        "color": "white",
        "padding": "10px",
    },
    "nav-link-selected": {"background-color": "gray"},  # Color cuando está seleccionado
}

# --------------------------------------------- MENU DESPLEGABLE Y PAGINAS---------------------------------------------------------------------

# Menú vertical desplegable
with st.sidebar:
    selected = option_menu(
        menu_title="",  # Título del menú
        options=["Introducción", "Resume", "Conclusiones"],  # Opciones del menú
        icons=["house", "file-earmark-text", "book"],  # Íconos correspondientes a las opciones
        menu_icon="cast",  # Ícono del menú
        default_index=0,  # Opción seleccionada por defecto
        orientation="vertical",
        styles=menu_styles
    )
    
    # Agregar un separador o un título adicional
    st.markdown("---")  # Separador horizontal
    st.markdown("### Memoria del TFM")  # Título adicional

    # Botón de descarga para el PDF
    pdf_file_path = "raw_data/uploaded_pdf.pdf"  # Ruta al archivo PDF

    # Usar el botón de descarga
    with open(pdf_file_path, "rb") as pdf_file:
        st.download_button(
            label="Descarga pinchando",  # Texto del botón
            data=pdf_file,               # El contenido del archivo
            file_name="MEMORIA TFM - Torres Moray, Agustina.pdf", # Nombre del archivo que se descargará
            mime="application/pdf"        # Tipo MIME para PDF
        )
    
    # Agregar otro separador
    st.markdown("---")  # Separador horizontal
    st.markdown("### Soporte")
    st.write("Para preguntas, contacta a atmoray@gmail.com")


# Primera página: Introducción
if selected == "Introducción":
   # CSS para fondo semitransparente en todo el bloque de texto
    st.markdown('''
        <style>
        .transparente {
            background-color: rgba(255, 255, 255, 0.6); /* Fondo blanco con transparencia */
            padding: 20px;
            border-radius: 10px;
            font-family: Arial, sans-serif;
            color: black;
        }
         .transparente h1 {
        font-size: 40px; /* Tamaño ajustado del título */
        }
        </style>
        <div class="transparente">
        <h1>Bienvenido a nuestra App de Resumen Inteligente</h1>
        <p>¡Hola! Te damos la bienvenida a nuestra plataforma de resúmenes inteligentes, donde puedes transformar grandes cantidades de información en resúmenes concisos y fáciles de entender. Nuestra aplicación está diseñada para simplificar el procesamiento de contenido extenso, permitiéndote ahorrar tiempo y obtener lo más importante de forma rápida.</p>

        <h2>¿Cómo Funciona?</h2>
        <p><strong>Selecciona tu Fuente:</strong> Elige entre cargar un PDF, insertar el enlace de un video de YouTube, o generar un resumen de noticias a partir de una URL.</p>
        <p><strong>Procesamiento Inteligente:</strong> Utilizamos modelos de inteligencia artificial avanzados para extraer y resumir el contenido, presentándote solo la información más relevante.</p>
        <p><strong>Recibe tu Resumen:</strong> Una vez procesado el contenido, te proporcionamos un resumen claro y directo, que puedes leer y descargar.</p>

        <h2>¿Qué Puedes Resumir?</h2>
        <p><strong>Documentos PDF:</strong> Sube cualquier documento y obtén un resumen en segundos.</p>
        <p><strong>Videos de YouTube:</strong> Solo con el enlace, nuestro sistema transcribe y resume el contenido del video.</p>
        <p><strong>Noticias Online:</strong> Inserta la URL de tu artículo y recibe un resumen preciso.</p>

        <p>Empieza ahora y optimiza tu tiempo con nuestros resúmenes automáticos. ¡Fácil, rápido y eficiente!</p>
        </div>
        ''', unsafe_allow_html=True)


elif selected == "Resume":

    # Título
    st.title('RESUME TUS NOTICIAS CON IA')
    st.header("La forma rapida de ponerte al día", divider="gray")

    # Opcioes
    option = st.selectbox("Que desear resumir?", 
                        ["Video de Youtube", "Articulo en PDF", "Periódico en linea"])

    # Options --  opion desactivada para llms - utilizada en prueba de modelos de transformer.
    #option_length = st.selectbox("Que largo largo deseas que tenga el resumen ?", 
                        #["LARGO: 200 tokens","MEDIO: 100 tokens", "CORTO: 50 tokens"])

    #summary_length = int(option_length.split()[1])

    # ------------------------------------------------- Resumen de PDF -------------------------------------------------
    
    #if option == "Articulo en PDF" and summary_length:
    if option == "Articulo en PDF":
        pdf_file = st.file_uploader("Sube tu articulo en PDF", type=["pdf"], help="Arrastra y suelta el archivo aquí o haz clic para seleccionar uno.")
        if st.button("RESUMIR"): 
            if pdf_file:
                st.success("El articulo se cargo correctamente")
                try:
                    with st.spinner("Reumiendo, por favor espere..."):
                        #summarized_text = pdf_pipeline(pdf_file, summary_length)
                        summarized_text = pdf_pipeline(pdf_file)
                        # Estilo para el fondo blanco
                        st.markdown(
                                        """
                                        <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                                            <h3>Resumen de la Noticia:</h3>
                                            <p>{}</p>
                                        </div>
                                        """.format(summarized_text), unsafe_allow_html=True
                                    )

                except Exception as e:
                    st.error(f"Error al resumir el pdf: {str(e)}")
            else:
                st.write("Adjunte el PDF que desea resumir")

    # ------------------------------------- Resumen de video de Youtube ------------------------------------------------------
    
    #if option == "Video de Youtube" and summary_length:
    if option == "Video de Youtube":
        video_url = st.text_input("Ingrese la URL del video de YouTube")
        if st.button("RESUMIR"):
            if video_url:
                st.success("La url es correcta")
                try:
                    with st.spinner("Resumiendo, por favor espera..."):
                        #summarized_text = video_pipeline(video_url, summary_length)
                        summarized_text = video_pipeline(video_url)
                        # Estilo para el fondo blanco
                        st.markdown(
                            """
                            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                                <h3>Resumen de la Noticia:</h3>
                                <p>{}</p>
                            </div>
                            """.format(summarized_text), unsafe_allow_html=True
                        )               
                except Exception as e:
                    st.error(f"Error al resumir el video: {str(e)}")
            else:
                st.write("Ingrese la url del video que desea resumir")

    # --------------------------------------- Resumen de periódico en linea --------------------------------------------------------------
    
    #if option == "Periódico en linea" and summary_length:
    if option == "Periódico en linea":
        news_options = ["El pais", "NBC", "elDiario.es"]
        selected_news_site = st.selectbox("Seleccione el Periódico", news_options)
        
        if selected_news_site:
            user_web_selection = get_user_web_selection(selected_news_site)   

            if user_web_selection:
                web_sections = scrape_web_header(user_web_selection["url"], user_web_selection["header"]["tag"], user_web_selection["header"]["class"])
                
                section_options = [section["section"] for section in web_sections]  # Nombre de las secciones
                selected_section = st.selectbox("Seleccione la Sección", section_options)
                
                if selected_section:
                    user_section_selection = next((item for item in web_sections if item["section"].lower() == selected_section.lower()), None)
                    
                    if user_section_selection:
                        st.session_state.selected_section = user_section_selection

                        if st.button("Mostrar Noticias"):
                            with st.spinner("Buscando los titulares, por favor espere..."):
                                news_list = scrape_news(st.session_state.selected_section, user_web_selection)
                                st.session_state.news_list = news_list

                        if "news_list" in st.session_state and st.session_state.news_list:
                            news_titles = [news["title"] for news in st.session_state.news_list]
                            selected_news_title = st.selectbox("Selecciona una noticia para resumir:", news_titles)
                            st.session_state.selected_news_title = selected_news_title
                            selected_news = next((news for news in st.session_state.news_list if news["title"] == st.session_state.selected_news_title), None)

                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Botón para mostrar la noticia completa
                                mostrar_noticia = st.button("LEER NOTICIA COMPLETA")
                                    
                            with col2:
                                # Botón para resumir la noticia
                                resumir_noticia = st.button("RESUMIR NOTICIA")

                            if mostrar_noticia and selected_news:
                                 # Estilo para el fondo blanco
                                st.markdown(
                                    """
                                    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                                        <h3>{}</h3>
                                        <p>{}</p>
                                    </div>
                                    """.format(selected_news['title'],selected_news["content"]), unsafe_allow_html=True
                                    
                                )
                                #st.markdown(f"## {selected_news['title']}")
                                #st.write(selected_news["content"])
                                
                            if resumir_noticia and selected_news:
                                with st.spinner("Resumiendo la noticia, por favor espere..."):
                                    # summarizer = MultilingualSummarizer()
                                    summarized_text = scrapping_pipeline(selected_news['content'])
                                     # Estilo para el fondo blanco
                                    st.markdown(
                                        """
                                        <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                                            <h3>Resumen de la Noticia:</h3>
                                            <p>{}</p>
                                        </div>
                                        """.format(summarized_text), unsafe_allow_html=True
                                    )
                                    

elif selected == "Conclusiones":
    st.title("Conclusiones")
    st.header("Conclusiones del Proyecto")