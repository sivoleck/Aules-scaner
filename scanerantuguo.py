from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import re

# Leer los datos de los archivos
try:
    archivo_login = open("login.txt", "r")
    usuario = archivo_login.readline().strip()
    contraseana = archivo_login.readline().strip()
    archivo_login.close()
except IOError:
    print("No se encuentra")
try:
    archivo_enlaces = open("enlaces.txt", "r")
    enlace_sesion = archivo_enlaces.readline().strip()
    enlace_clase = archivo_enlaces.readline().strip()
    archivo_enlaces.close()
except IOError:
    print("Debe poner los enlaces en el archivo enlaces.txt")

# Configurar opciones del navegador
chrome_options = Options()
chrome_options.add_argument(
    "--headless"
)  # Ejecutar en modo headless (sin interfaz gráfica)


# Función para extraer los datos de la página web
def extractor():
    # Inicializar el navegador
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    try:
        # Navegar a la página de inicio de sesión
        driver.get(enlace_sesion)

        # Encontrar los campos de usuario y contraseña e iniciar sesión
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        username.send_keys(usuario)
        password.send_keys(contraseana)
        driver.find_element(By.ID, "loginbtn").click()

        print("Iniciando sesión...")

        # Esperar a que la página de destino esté completamente cargada
        WebDriverWait(driver, 10)

        # Navegar a la página deseada
        driver.get(enlace_clase)

        # Esperar a que la página de destino esté completamente cargada

        # Encontrar todos los elementos con la clase cat_343470
        rowtitles = driver.find_elements(
            By.XPATH, "//*[contains(@class, 'cat_343470')]"
        )

        # Imprimir las clases y el contenido de los elementos encontrados
        patron_vacio = re.compile(r"Vacío")
        patron_nombre = re.compile(r"HOTPOT\s*(.*)")
        patron_nota = re.compile(r"%\s*(\d+)")
        patron_link = re.compile(r'href="([^"]+)"')
        enlaces = []
        for rowtitle_element in rowtitles:
            content = rowtitle_element.get_attribute("innerHTML")
            enlaces.append(content)
        datos = []
        for elemento in rowtitles:
            elemento = elemento.text
            datos.append(elemento)
        sin_hacer = []
        contador = 0

        for ejercicio in datos:
            if ejercicio.startswith("HOTPOT"):
                print(ejercicio)
                if patron_vacio.search(ejercicio):
                    nombre = patron_nombre.search(ejercicio).group(1)
                    search_result = patron_link.search(enlaces[contador - 1])
                    if search_result:
                        enlace = search_result.group(1)
                    else:
                        enlace = None  # or handle the case where the link is not found
                    texto = nombre + " por hacer: " + enlace
                    sin_hacer.append(texto)
                else:
                    if patron_nota.search(ejercicio):
                        nota = int(patron_nota.search(ejercicio).group(1))
                        if nota < 90:
                            nombre = patron_nombre.search(ejercicio).group(1)
                            search_result = patron_link.search(enlaces[contador - 1])
                            if search_result:
                                enlace = search_result.group(1)
                                texto = nombre + " nota baja: " + enlace
                                sin_hacer.append(texto)

                        elif nota == 0:
                            nombre = patron_nombre.search(ejercicio).group(1)
                            search_result = patron_link.search(enlaces[contador - 1])
                            if search_result:
                                enlace = search_result.group(1)
                                texto = nombre + " por hacer: " + enlace
                                sin_hacer.append(texto)

        for texto in sin_hacer:
            print(texto)
    except TimeoutException:
        print(
            "TimeoutException: Elemento no encontrado dentro del tiempo especificado."
        )
    finally:
        # Cerrar el navegador
        driver.quit()


# Iniciar el proceso de extracción
extractor()
