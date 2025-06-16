from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import send2trash
from pathlib import Path
import re
import flet as ft

# Leer los datos de los archivos
archivo_login = open("login.txt", "r")
usuario = archivo_login.readline().strip()
contraseana = archivo_login.readline().strip()
archivo_login.close()

archivo_enlaces = open("enlaces.txt", "r")
enlace_sesion = archivo_enlaces.readline().strip()
enlace_clase = archivo_enlaces.readline().strip()
archivo_enlaces.close()

# Configurar opciones del navegador
chrome_options = Options()
chrome_options.add_argument(
    "--headless"
)  # Ejecutar en modo headless (sin interfaz gráfica)


def main(page: ft.Page):
    page.width = 300
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
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Navegar a la página deseada
        driver.get(enlace_clase)

        # Esperar a que la página cargue completamente
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//*[contains(@class, 'cat_343470')]")
            )
        )

        # Dar tiempo adicional para cargar elementos dinámicos
        import time

        time.sleep(3)

        rowtitles = []
        # Encontrar todos los elementos con la clase cat_343470
        for y in driver.find_elements(By.XPATH, "//*[contains(@class, 'cat_343470')]"):
            if y.text.startswith("HOTPOT") or y.text.startswith("CUESTIONARIO"):
                rowtitles.append(y)

        # Patrones regulares
        patron_vacio = re.compile(r"Vacío")
        patron_nombre = re.compile(r"HOTPOT\s*(.*)")
        patron_nombre_cuestionario = re.compile(r"CUESTIONARIO\s*(.*)")
        patron_nota = re.compile(r"%\s*([-]|\d+)")
        sin_hacer = []
        cuestionario = False

        for elemento in rowtitles:
            elemento_texto = elemento.text
            elemento_html = elemento.get_attribute("outerHTML")
            print(f"Elemento encontrado: {elemento_texto[:50]}...")

            # Buscar todos los enlaces dentro del elemento completo
            enlaces_a = elemento.find_elements(By.XPATH, ".//a")

            # Si no encuentra enlaces directamente, intentar otra estrategia
            if not enlaces_a:
                # Usar JavaScript para extraer todos los enlaces
                enlaces_a = driver.execute_script(
                    """
                    var element = arguments[0];
                    return element.querySelectorAll('a');
                """,
                    elemento,
                )

            if patron_vacio.search(elemento_texto):
                if patron_nombre.search(elemento_texto):
                    nombre = patron_nombre.search(elemento_texto).group(1)
                else:
                    nombre = patron_nombre_cuestionario.search(elemento_texto).group(1)

                texto = nombre + " por hacer: "

                # Intentar obtener el enlace
                if enlaces_a:
                    for enlace in enlaces_a:
                        href = enlace.get_attribute("href")
                        if href and ("hotpot" in href or "quiz" in href):
                            texto += href
                            break

                sin_hacer.append(texto)
            else:
                if patron_nota.search(elemento_texto):
                    try:
                        nota = int(patron_nota.search(elemento_texto).group(1))
                    except ValueError:
                        nota = 0

                    if patron_nombre.search(elemento_texto):
                        nombre = patron_nombre.search(elemento_texto).group(1)
                        cuestionario = False
                    else:
                        nombre = patron_nombre_cuestionario.search(
                            elemento_texto
                        ).group(1)
                        cuestionario = True

                    if (nota < 90 and not cuestionario) or nota == 0:
                        search_result = None

                        # Buscar todos los enlaces que contengan hotpot o quiz
                        for enlace in enlaces_a:
                            href = enlace.get_attribute("href")
                            if href and ("hotpot" in href or "quiz" in href):
                                search_result = href
                                break

                        if nota < 90 and not cuestionario:
                            texto = (
                                nombre
                                + " nota baja: "
                                + (search_result or "Enlace no encontrado")
                            )
                        else:
                            texto = (
                                nombre
                                + " por hacer: "
                                + (search_result or "Enlace no encontrado")
                            )

                        sin_hacer.append(texto)

        for texto in sin_hacer:
            print(texto)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Cerrar el navegador
        driver.quit()
        # Crear archivo
        if Path("resultado.txt").exists():
            send2trash.send2trash("resultado.txt")
            time.sleep(1)
        archivo = open("resultado.txt", "w")
        for mensaje in sin_hacer:
            archivo.write(mensaje + "\n")
            print(mensaje)
        archivo.close()
        print("¡Listo!")


# Iniciar el proceso de extracción
if __name__ == "__main__":
    ft.app(target=main)
