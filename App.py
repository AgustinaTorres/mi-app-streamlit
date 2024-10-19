import streamlit as st
from streamlit_option_menu import option_menu
from pipelines import pdf_pipeline, video_pipeline, scrapping_pipeline
from functions import get_user_web_selection, scrape_web_header, scrape_news, news_sites
from scrapping_transcription_functions import get_user_web_selection, scrape_web_header, scrape_news, save_scrapping_transcription, news_sites
from summary_transformers import MultilingualSummarizer, summarize_text, split_text 
import re
import os


# Configurar el título principal y la disposición de la página
st.set_page_config(page_title="TRABAJO FINAL DE MASTER - Torres Moray, Agustina", layout="wide")

def show_loading_message():
    with st.spinner("Cargando, por favor espera..."):
        yield  # Esta línea permite que el spinner se muestre hasta que se complete el bloque de código


# --------------------------------------------- HEADER ---------------------------------------------------------------------

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
st.markdown('<div class="initials">By GUCHI</div>', unsafe_allow_html=True)  # Cambia "AT" por tus iniciales


# Cargar la imagen del logo desde la carpeta local
#logo_path = "assets/logo.jpg"  # Cambia la ruta según sea necesario
#st.markdown(f'<img src="{logo_path}" class="logo" style="width:100px;">', unsafe_allow_html=True)  # Ajusta el tamaño según necesites


# Crear un navbar en la parte superior de la página
import streamlit as st
from streamlit_option_menu import option_menu

# Define estilos comunes
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

# Menú principal
with st.sidebar:
    selected = option_menu(
        menu_title="",  # Título del menú
        options=["Introducción", "Desarrollo", "Conclusiones"],  # Opciones del menú
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
            file_name="memoria_TFM.pdf", # Nombre del archivo que se descargará
            mime="application/pdf"        # Tipo MIME para PDF
        )
    
    # Agregar otro separador
    st.markdown("---")  # Separador horizontal
    st.markdown("### Soporte")
    st.write("Para preguntas, contacta a atmoray@gmail.com")



# Primera página: Introducción
if selected == "Introducción":
    st.title("Bienvenido a tu resumen de noticias con I.A")
    st.header("Como funciona la app?")
    st.write("El siguiente diagrama de flujo te ayudará a entender lo facil que es resumir tus noticias con nuestra aplicacion de Streamlit.")

    # Cargar e insertar la imagen del diagrama de flujo
    st.image("assets/flujograma.png", caption="Diagrama de Flujo del Proyecto", use_column_width=True)

elif selected == "Desarrollo":

    # Títle
    st.title('RESUME TUS NOTICIAS CON IA')
    st.header("La forma rapida de ponerte al día", divider="gray")


    # Options
    option = st.selectbox("Que desear resumir?", 
                        ["Video de Youtube", "Articulo en PDF", "Mis periodico favorito"])


    # Options
    option_length = st.selectbox("Que largo largo deseas que tenga el resumen ?", 
                        ["LARGO: 200 tokens","MEDIO: 100 tokens", "CORTO: 50 tokens"])

    summary_length = int(option_length.split()[1])

    # ------------------------------------------------- OPTION 1 - PDF -------------------------------------------------
    if option == "Articulo en PDF" and summary_length:
        pdf_file = st.file_uploader("Sube tu articulo en PDF", type=["pdf"])
        if st.button("RESUMIR"): 
            if pdf_file:
                st.success("El articulo es correcto")
                try:
                    with st.spinner("Cargando, por favor espera..."):
                        summarized_text = pdf_pipeline(pdf_file, summary_length)
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
                st.write("Ingrese el articulo en PDF que desea resumir")


    # -------------------------------------Summary by youtube video ------------------------------------------------------
    if option == "Video de Youtube" and summary_length:
        video_url = st.text_input("Introduce la URL del video de YouTube")
        
        if st.button("RESUMIR"):
            if video_url:
                try:
                    with st.spinner("Cargando, por favor espera..."):
                        summarized_text = video_pipeline(video_url, summary_length)
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

    # ---------------------------------------Summary by web scrapping --------------------------------------------------------------
    # ---------------------------------------Summary by web scrapping --------------------------------------------------------------
    if option == "Mis periodico favorito" and summary_length:
        
        # news_options = [site["name"] for site in news_sites]
        news_options = ["El pais", "NBC", "elDiario.es"]
        selected_news_site = st.selectbox("Seleccione el Periódico", news_options)
        
        if selected_news_site:
            user_web_selection = get_user_web_selection(selected_news_site)  # Dictionary 

            if user_web_selection:
                web_sections = scrape_web_header(user_web_selection["url"], user_web_selection["header"]["tag"], user_web_selection["header"]["class"])
                
                section_options = [section["section"] for section in web_sections]  # Nombre de las secciones
                selected_section = st.selectbox("Seleccione la Sección", section_options)
                
                if selected_section:
                    user_section_selection = next((item for item in web_sections if item["section"].lower() == selected_section.lower()), None)
                    
                    if user_section_selection:
                        # Guardar el estado de la sección seleccionada
                        st.session_state.selected_section = user_section_selection

                        if st.button("Mostrar Noticias"):
                            with st.spinner("Obteniendo las noticias..."):
                                # Scrape noticias de la sección seleccionada y guardarlas en session_state
                                news_list = scrape_news(st.session_state.selected_section, user_web_selection)
                                st.session_state.news_list = news_list

                        # Mostrar la lista de noticias solo si hay noticias en session_state
                        if "news_list" in st.session_state and st.session_state.news_list:
                            news_titles = [news["title"] for news in st.session_state.news_list]
                            
                            # Guardar el título de la noticia seleccionada en session_state
                            selected_news_title = st.selectbox("Selecciona una noticia para ver:", news_titles)
                            st.session_state.selected_news_title = selected_news_title

                            # Encontrar la noticia seleccionada
                            selected_news = next((news for news in st.session_state.news_list if news["title"] == st.session_state.selected_news_title), None)

                            # Botones en la parte superior
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Botón para mostrar la noticia completa
                                mostrar_noticia = st.button("Mostrar Noticia Completa")
                                    
                            with col2:
                                # Botón para resumir la noticia
                                resumir_noticia = st.button("RESUMIR NOTICIA")

                            # Mostrar el contenido en toda la pantalla fuera de las columnas
                            if mostrar_noticia and selected_news:
                                st.markdown(f"## {selected_news['title']}")
                                st.write(selected_news["content"])
                            
                            if resumir_noticia and selected_news:
                                with st.spinner("Resumiendo la noticia..."):
                                    # summarizer = MultilingualSummarizer()
                                    summarized_text = scrapping_pipeline(selected_news['content'], summary_length)
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