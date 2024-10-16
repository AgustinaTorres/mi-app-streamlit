from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Configuración del navegador (sin interfaz gráfica)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Para ejecutar en segundo plano sin abrir ventana

# Inicia el navegador
service = Service('/chromedriver.exe')  # Cambia por la ruta correcta de tu chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navega a la página
driver.get("https://elpais.com/")

# Espera a que el contenido cargue, puedes ajustar el tiempo de espera
driver.implicitly_wait(10)  # Espera hasta 10 segundos

# Extrae el contenido que necesitas
noticias = driver.find_elements(By.TAG_NAME, "article")

# Imprime los títulos de las noticias
for noticia in noticias:
    titulo = noticia.find_element(By.TAG_NAME, "h2").text
    print(titulo)

# Cierra el navegador
driver.quit()
