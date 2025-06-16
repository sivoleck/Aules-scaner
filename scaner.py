import flet as ft
from flet import Colors, Icons
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
import time

mi_path = Path.cwd()

chrome_options = Options()
chrome_options.add_argument("--headless")

archivo_login = open(mi_path / "build" / "login.txt", "r")
usuario = archivo_login.readline().strip()
contraseana = archivo_login.readline().strip()
archivo_login.close()

archivo_enlaces = open(mi_path / "build" / "enlaces.txt", "r")
enlace_sesion = archivo_enlaces.readline().strip()
enlace_clase = archivo_enlaces.readline().strip()
archivo_enlaces.close()

class Myscaner:
    def __init__(self):
        self.page = ft.Page
        self.user = usuario
        self.contraseana = contraseana
        self.enlace = enlace_clase
        self.texto_principal = ""
        self.color = Colors.GREEN
        self.texto_estado_ref = ft.Ref[ft.Text]()

    def actualizartxt(self):
        archivo_login = open(mi_path / "build" / "login.txt", "r")
        self.user = archivo_login.readline().strip()
        self.contraseana = archivo_login.readline().strip()
        archivo_login.close()

        archivo_enlaces = open(mi_path / "build" / "enlaces.txt", "r")
        enlace_sesion = archivo_enlaces.readline().strip()
        self.enlace = archivo_enlaces.readline().strip()
        archivo_enlaces.close()


    def actualizar_estado(self, mensaje, color=None):
        """Actualiza el texto de estado y refresca la UI"""
        self.texto_principal = mensaje
        if color:
            self.color = color

        if self.texto_estado_ref.current:
            self.texto_estado_ref.current.value = mensaje
            self.texto_estado_ref.current.color = self.color
            self.page.update()

    def extractor(self, e=None):
        # Verificar correctamente si e existe y tiene un atributo control
        boton = None

        if e is not None and hasattr(e, "control"):
            boton = e.control

        if boton:
            boton.disabled = True
            boton.color = Colors.GREY
            self.page.update()

        # Inicializar la variable al principio para que esté disponible en cualquier caso
        ejercicios_a_hacer = []

        # Inicializar el navegador
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        try:
            # Navegar a la página de inicio de sesión
            driver.get(enlace_sesion)

            print("Iniciando sesión...")
            self.actualizar_estado(
                "Iniciando sesion en aules con sus credenciales...", Colors.GREEN
            )

            max_intentos = 2
            for intento in range(max_intentos):
                try:
                    # Encontrar los campos de usuario y contraseña e iniciar sesión
                    username = driver.find_element(By.NAME, "username")
                    password = driver.find_element(By.NAME, "password")
                    username.send_keys(self.user)
                    password.send_keys(self.contraseana)
                    driver.find_element(By.ID, "loginbtn").click()

                    # Verificar si el inicio de sesión fue exitoso
                    wait = WebDriverWait(driver, 5)
                    try:
                        # Intentar encontrar algún elemento que confirme inicio exitoso
                        wait.until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        break  # Si llega aquí, el inicio fue exitoso
                    except Exception:
                        if intento < max_intentos - 1:
                            self.actualizar_estado(
                                f"Reintentando inicio de sesión ({intento + 1}/{max_intentos})...",
                                Colors.ORANGE,
                            )
                            driver.get(enlace_sesion)  # Volver a cargar la página
                        else:
                            raise Exception(
                                "No se pudo iniciar sesión después de varios intentos"
                            )
                except Exception as e:
                    if intento < max_intentos - 1:
                        self.actualizar_estado(
                            f"Reintentando inicio de sesión ({intento + 1}/{max_intentos})...",
                            Colors.ORANGE,
                        )
                        driver.get(enlace_sesion)  # Volver a cargar la página
                    else:
                        self.actualizar_estado(
                            "Error al iniciar sesion, por favor compruebe las credenciales...",
                            Colors.RED,
                        )
                        print(e)
                        return

            self.actualizar_estado("Cargando pagina", Colors.GREEN)

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
            time.sleep(3)

            rowtitles = []
            # Encontrar todos los elementos con la clase cat_343470
            self.actualizar_estado("Iniciando con el analisis...", Colors.GREEN)

            for y in driver.find_elements(
                By.XPATH, "//*[contains(@class, 'cat_343470')]"
            ):
                if y.text.startswith("HOTPOT") or y.text.startswith("CUESTIONARIO"):
                    rowtitles.append(y)

            # Patrones regulares
            patron_vacio = re.compile(r"Vacío")
            patron_nombre = re.compile(r"HOTPOT\s*(.*)")
            patron_nombre_cuestionario = re.compile(r"CUESTIONARIO\s*(.*)")
            patron_nota = re.compile(r"%\s*([-]|\d+)")
            cuestionario = False

            for elemento in rowtitles:
                elemento_texto = elemento.text
                print(f"Elemento encontrado: {elemento_texto[:50]}...")
                self.actualizar_estado(f"Analizando {elemento_texto[:50]}", Colors.BLUE)

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
                        nombre = patron_nombre_cuestionario.search(
                            elemento_texto
                        ).group(1)

                    texto = nombre + " por hacer: "

                    # Intentar obtener el enlace
                    if enlaces_a:
                        for enlace in enlaces_a:
                            href = enlace.get_attribute("href")
                            if href and ("hotpot" in href or "quiz" in href):
                                texto += href
                                break

                    ejercicios_a_hacer.append(texto)
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
                            ejercicios_a_hacer.append(texto)

            for texto in ejercicios_a_hacer:
                print(texto)

        except Exception as e:
            self.actualizar_estado(f"Error durante el análisis: {str(e)}", Colors.RED)
            print(f"Error: {str(e)}")
        finally:
            self.actualizar_estado("Finalizando análisis...", Colors.GREEN)

            # Cerrar el navegador
            driver.quit()

            # Crear archivo solo si hay resultados
            if ejercicios_a_hacer:
                if Path("resultado.txt").exists():
                    send2trash.send2trash("resultado.txt")
                    time.sleep(1)
                archivo = open("resultado.txt", "w")
                for mensaje in ejercicios_a_hacer:
                    archivo.write(mensaje + "\n")
                    print(mensaje)
                archivo.close()
                self.actualizar_estado("¡Archivo creado con éxito!", Colors.GREEN)
            else:
                self.actualizar_estado(
                    "Análisis completado. No se encontraron elementos pendientes.",
                    Colors.BLUE,
                )
            if boton:
                boton.disabled = False
                boton.color = Colors.WHITE
                self.page.update()
            print("¡Listo!")

    def principal(self):
        self.page.clean()
        self.page.window.width = 700
        self.page.window.height = 600
        self.page.window.center()
        self.texto_estado_ref = ft.Ref[ft.Text]()
        # Encabezado
        texto_bienvenida = ft.Text(
            value="Sesión iniciada correctamente",
            color=Colors.GREEN,
            size=25,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # Área de estado
        contenedor_estado = ft.Container(
            content=ft.Text(
                ref=self.texto_estado_ref,
                value=self.texto_principal
                if self.texto_principal
                else "Listo para comenzar el análisis",
                color=self.color,
                size=16,
                text_align=ft.TextAlign.CENTER,
            ),
            padding=10,
            border_radius=10,
            bgcolor=Colors.with_opacity(0.1, self.color),
            margin=ft.margin.only(top=10, bottom=20),
            height=50,
            width=500,
        )

        boton_cambiar = ft.IconButton(
            icon=Icons.ACCOUNT_CIRCLE_OUTLINED,
            icon_size=30,
            on_click=lambda e: self.loggin(),
            tooltip="Loggin",
        )

        # Botón para iniciar el análisis
        boton_analizar = ft.ElevatedButton(
            text="Iniciar análisis",
            icon=Icons.SEARCH,
            on_click=lambda e: self.extractor(e),
            style=ft.ButtonStyle(color=Colors.WHITE, bgcolor=Colors.BLUE),
            width=200,
        )

        # Tarjeta para mostrar resultados
        tarjeta_resultados = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(Icons.ASSIGNMENT, color=Colors.BLUE),
                            title=ft.Text("Resultados del análisis", size=18),
                            subtitle=ft.Text("Se guardará en 'resultado.txt'"),
                        ),
                        ft.Divider(),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "• En este archivo se mostrarán las actividades pendientes",
                                        color=Colors.RED,
                                    ),
                                    ft.Text(
                                        "• Y las actividades con notas bajas",
                                        color=Colors.ORANGE,
                                    ),
                                ]
                            ),
                            padding=15,
                        ),
                    ]
                ),
                padding=10,
            ),
            margin=ft.margin.only(top=20),
            width=500,
        )

        # Botón para abrir el archivo de resultados
        boton_abrir = ft.TextButton(
            text="Abrir archivo de resultados",
            icon=Icons.FOLDER_OPEN,
            on_click=lambda e: self.page.launch_url("resultado.txt"),
        )
        row_principal = ft.Row(
            controls=[texto_bienvenida, boton_cambiar],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
        # Columna principal
        columna_principal = ft.Column(
            controls=[
                row_principal,
                contenedor_estado,
                boton_analizar,
                tarjeta_resultados,
                boton_abrir,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        )

        # Contenedor principal
        contenedor_principal = ft.Container(
            content=columna_principal,
            alignment=ft.alignment.top_center,
            padding=20,
            expand=True,
        )

        self.page.add(contenedor_principal)
        self.page.update()

    def loggin(self):
        self.page.clean()
        self.page.window.width = 400
        self.page.window.height = 350
        self.page.window.resizable = False
        self.page.window.maximizable = False
        self.page.window.center()

        def boton_login(e):
            self.actualizartxt()
            nueva_contrasena = campo_contrasena.value
            nuevo_usuario = campo_usuario.value
            nuevo_enlace = campo_enlace.value
            if nuevo_usuario != self.user and nueva_contrasena != self.contraseana:
                open("login.txt", "w").write(
                    campo_usuario.value + "\n" + campo_contrasena.value
                )
                self.user = campo_usuario.value
                self.contraseana = campo_enlace.value
            elif nuevo_usuario != self.user:
                open("login.txt", "w").write(
                    campo_usuario.value + "\n" + self.contraseana
                )
                self.user = campo_usuario.value
            elif nueva_contrasena != self.contraseana:
                open("login.txt", "w").write(self.user + "\n" + campo_contrasena.value)
                self.contraseana = campo_enlace.value
            self.principal()
            if nuevo_enlace != self.enlace:
                open("enlaces.txt", "w").write(enlace_sesion + "\n" + campo_enlace.value)
                self.enlace = campo_enlace.value
        campo_usuario = ft.TextField(
            label="NIE",
            hint_text="Escribe aqui...",
            value=self.user,
            width=250,
            prefix_icon=ft.Icons.ACCOUNT_CIRCLE_ROUNDED,
        )

        campo_contrasena = ft.TextField(
            label="Contraseña",
            hint_text="Escribe aqui...",
            password=True,
            can_reveal_password=True,
            value=self.contraseana,
            width=250,
            prefix_icon=ft.Icons.LOCK_OUTLINED,
        )

        campo_enlace = ft.TextField(
            label="Enlace calificaciones asignatura",
            hint_text="Pegar aqui...",
            value=self.enlace,
            width=250,
            prefix_icon=ft.Icons.INSERT_LINK_ROUNDED,
        )

        # Texto centrado arriba
        texto_login = ft.Text(
            value="Introduzca sus credenciales de aules",
            color="blue",
            size=15,
            text_align=ft.TextAlign.CENTER,
        )

        boton = ft.Button(text="Login", on_click=boton_login, color="blue", width=150)

        # Columna con todos los elementos centrados
        columna_principal = ft.Column(
            controls=[
                texto_login,
                ft.Container(height=10),  # Espaciado entre título y campos
                campo_usuario,
                campo_contrasena,
                campo_enlace,
                boton,
            ],
            alignment=ft.MainAxisAlignment.START,  # Centra verticalmente
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centra horizontalmente
            spacing=15,
        )

        # Contenedor principal que ocupa toda la página y centra el contenido
        contenedor_principal = ft.Container(
            content=columna_principal, alignment=ft.alignment.center, expand=True
        )

        # Limpiar la página y agregar el contenido
        self.page.clean()
        self.page.add(contenedor_principal)
        self.page.update()


def main(page: ft.Page):
    pagina = Myscaner()
    page.title = "Escaner de ejercicios aules"
    page.icon = "Icono.png"
    pagina.page = page
    pagina.loggin()


ft.app(main)
