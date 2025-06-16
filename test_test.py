import flet as ft
from flet import Icons, Colors


def main(page: ft.Page):
    page.title = "Animación Candado"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Estado del candado
    is_locked = True

    # Referencia al AnimatedSwitcher
    switcher = ft.Ref[ft.AnimatedSwitcher]()

    def toggle_lock(e):
        nonlocal is_locked
        is_locked = not is_locked

        # Crear nuevo icono según el estado
        if is_locked:
            new_icon = ft.Icon(
                Icons.LOCK_OUTLINED,
                size=100,
                color=Colors.RED_400,
            )
        else:
            new_icon = ft.Icon(
                Icons.LOCK_OPEN_OUTLINED,
                size=100,
                color=Colors.GREEN_400,
            )

        # Actualizar el contenido del switcher
        switcher.current.content = new_icon

        # Actualizar el texto del botón
        button.text = "🔓 Abrir" if is_locked else "🔒 Cerrar"

        page.update()

    # Icono inicial
    initial_icon = ft.Icon(
        Icons.LOCK_OUTLINED,
        size=100,
        color=Colors.RED_400,
    )

    # AnimatedSwitcher para transición suave
    switcher.current = ft.AnimatedSwitcher(
        content=initial_icon,
        duration=400,  # Duración en milisegundos
        reverse_duration=400,
        switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
    )

    # Botón para cambiar estado
    button = ft.ElevatedButton(
        text="🔓 Abrir",
        on_click=toggle_lock,
        style=ft.ButtonStyle(
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
        ),
    )

    # Texto indicativo
    status_text = ft.Text(
        "Haz clic para cambiar el estado del candado",
        size=16,
        color=Colors.GREY_600,
        text_align=ft.TextAlign.CENTER,
    )

    page.add(
        ft.Column(
            [
                ft.Text(
                    "🔐 Animación de Candado",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=Colors.BLUE_800,
                ),
                ft.Container(height=20),  # Espaciado
                switcher.current,
                ft.Container(height=30),  # Espaciado
                button,
                ft.Container(height=20),  # Espaciado
                status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
