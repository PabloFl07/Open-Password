import flet as ft
import sqlite3
import logging
import threading
from datetime import datetime
from database import Database, AuthManager, Verify
from llm import AiModel



def main(page: ft.Page):

    page.title        = "Registro de Usuario"
    page.window_width  = 480
    page.window_height = 820
    page.theme_mode    = ft.ThemeMode.DARK
    page.vertical_alignment   = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#0f1117"
    page.scroll  = ft.ScrollMode.AUTO

    try:
        db   = Database("passmanager.db")
        auth = AuthManager(db)
        ai   = AiModel()
    except Exception as e:
        page.add(ft.Text(f"Error de base de datos: {e}", color=ft.Colors.RED_400))
        return

    db.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT UNIQUE NOT NULL,
            password_hash  TEXT NOT NULL,
            salt           TEXT NOT NULL,
            two_fa_contact TEXT NOT NULL
        );
    """)

    def mostrar_snack(mensaje: str, color=ft.Colors.RED_700):
        page.snack_bar = ft.SnackBar(
            ft.Text(mensaje, color=ft.Colors.WHITE), bgcolor=color
        )
        page.snack_bar.open = True
        page.update()


    def actualizar_indicador(password: str):
        errores = Verify.validate_password(password)
        n = len(errores)
        if not password:
            indicador_txt.value   = ""
            barra_fortaleza.value = 0
            barra_fortaleza.color = ft.Colors.GREY_700
        elif n >= 4:
            indicador_txt.value   = "Muy debil"
            indicador_txt.color   = ft.Colors.RED_400
            barra_fortaleza.value = 0.15
            barra_fortaleza.color = ft.Colors.RED_400
        elif n == 3:
            indicador_txt.value   = "Debil"
            indicador_txt.color   = ft.Colors.DEEP_ORANGE_400
            barra_fortaleza.value = 0.35
            barra_fortaleza.color = ft.Colors.DEEP_ORANGE_400
        elif n == 2:
            indicador_txt.value   = "Regular"
            indicador_txt.color   = ft.Colors.ORANGE_400
            barra_fortaleza.value = 0.55
            barra_fortaleza.color = ft.Colors.ORANGE_400
        elif n == 1:
            indicador_txt.value   = "Buena"
            indicador_txt.color   = ft.Colors.YELLOW_400
            barra_fortaleza.value = 0.75
            barra_fortaleza.color = ft.Colors.YELLOW_400
        else:
            indicador_txt.value   = "Fuerte"
            indicador_txt.color   = ft.Colors.GREEN_400
            barra_fortaleza.value = 1.0
            barra_fortaleza.color = ft.Colors.GREEN_400
        analizar_btn.visible = bool(password)
        page.update()

    def btn_analizar_click(e):
        if not reg_pass.value:
            mostrar_snack("Escribe una contrasena primero.")
            return
        analizar_btn.disabled = True
        analizar_btn.text     = "Analizando..."
        groq_panel.visible    = True
        groq_resultado.value  = "Consultando a Groq IA..."
        groq_resultado.color  = ft.Colors.BLUE_GREY_400
        page.update()

        def consultar():
            try:
                resultado = ai.consultar_seguridad(reg_pass.value)
                groq_resultado.value = resultado
                groq_resultado.color = ft.Colors.BLUE_GREY_100
            except Exception as ex:
                logging.error(f"Error Groq: {ex}")
                groq_resultado.value = f"Error al consultar Groq: {ex}"
                groq_resultado.color = ft.Colors.RED_400
            finally:
                analizar_btn.disabled = False
                analizar_btn.text     = "Analizar con IA"
                page.update()

        threading.Thread(target=consultar, daemon=True).start()

    def btn_register_click(e):
        reg_user.error_text         = None
        reg_email.error_text        = None
        reg_pass.error_text         = None
        reg_pass_confirm.error_text = None

        error = Verify.validar_campos(
            reg_user.value.strip(),
            reg_email.value.strip(),
            reg_pass.value,
            reg_pass_confirm.value
        )
        
        if error:
            mostrar_snack(error)
            page.update()
            return

        register_btn.disabled = True
        register_btn.text     = "Registrando..."
        page.update()

        try:
            auth.register_user(
                username       = reg_user.value.strip(),
                password       = reg_pass.value,
                two_fa_contact = reg_email.value.strip()
            )
            mostrar_snack("Cuenta creada con exito!", ft.Colors.GREEN_700)

            reg_user.value = reg_email.value = ""
            reg_pass.value = reg_pass_confirm.value = ""
            indicador_txt.value   = ""
            barra_fortaleza.value = 0
            groq_panel.visible    = False
            groq_resultado.value  = ""
            analizar_btn.visible  = False
            page.update()

        except sqlite3.IntegrityError:
            reg_user.error_text = "Este nombre de usuario ya esta en uso."
            page.update()
        except ValueError as ve:
            mostrar_snack(str(ve))
        except Exception as ex:
            logging.error(f"Error al registrar: {ex}")
            mostrar_snack(f"Error inesperado: {ex}")
        finally:
            register_btn.disabled = False
            register_btn.text     = "Crear cuenta"
            page.update()

    # Componentes
    field_style = {
        "width"               : 340,
        "border_radius"       : 10,
        "border_color"        : ft.Colors.BLUE_GREY_700,
        "focused_border_color": ft.Colors.BLUE_400,
        "bgcolor"             : "#1a1d27",
        "cursor_color"        : ft.Colors.BLUE_400,
    }

    reg_user         = ft.TextField(label="Nombre de usuario",   prefix_icon=ft.Icons.PERSON_OUTLINE,      max_length=30,  **field_style)
    reg_email        = ft.TextField(label="Correo electronico",  prefix_icon=ft.Icons.EMAIL_OUTLINED,      max_length=100, keyboard_type=ft.KeyboardType.EMAIL, **field_style)
    reg_pass         = ft.TextField(label="Contrasena maestra",  prefix_icon=ft.Icons.LOCK_OUTLINE,        max_length=128, password=True, can_reveal_password=True, on_change=lambda e: actualizar_indicador(e.control.value), **field_style)
    reg_pass_confirm = ft.TextField(label="Confirmar contrasena",prefix_icon=ft.Icons.LOCK_RESET_OUTLINED, max_length=128, password=True, can_reveal_password=True, **field_style)

    barra_fortaleza = ft.ProgressBar(width=340, value=0, color=ft.Colors.GREY_700, bgcolor="#1a1d27", border_radius=4)
    indicador_txt   = ft.Text(value="", size=11, color=ft.Colors.GREY_500)

    analizar_btn = ft.OutlinedButton(
        text     = "Analizar con IA",
        on_click = btn_analizar_click,
        width    = 340,
        visible  = False,
        style    = ft.ButtonStyle(
            color = {ft.ControlState.DEFAULT: ft.Colors.BLUE_300},
            side  = {ft.ControlState.DEFAULT: ft.BorderSide(1, ft.Colors.BLUE_700)},
        )
    )

    groq_resultado = ft.Text(value="", size=12, color=ft.Colors.BLUE_GREY_100, selectable=True)
    groq_panel = ft.Container(
        visible       = False,
        content       = ft.Column(
            controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.SMART_TOY_OUTLINED, size=14, color=ft.Colors.BLUE_400),
                    ft.Text("Analisis Groq IA", size=11, color=ft.Colors.BLUE_400, weight=ft.FontWeight.BOLD),
                ], spacing=6),
                ft.Text("Contrasena con las mismas caracteristicas, no la tuya", size=10, color=ft.Colors.BLUE_GREY_600, italic=True),
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_800),
                groq_resultado,
            ],
            spacing=6,
        ),
        bgcolor       = "#111827",
        border_radius = 8,
        padding       = ft.padding.all(12),
        border        = ft.border.all(1, "#1e3a5f"),
        width         = 340,
    )

    register_btn = ft.ElevatedButton(
        text     = "Crear cuenta",
        on_click = btn_register_click,
        width    = 340,
        height   = 48,
        style    = ft.ButtonStyle(
            bgcolor = {ft.ControlState.DEFAULT: ft.Colors.BLUE_700},
            color   = {ft.ControlState.DEFAULT: ft.Colors.WHITE},
        )
    )

    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.Icons.SHIELD_OUTLINED, size=56, color=ft.Colors.BLUE_400),
                                ft.Text("Crear cuenta", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text("Gestor de contrasenas seguro", size=13, color=ft.Colors.BLUE_GREY_300),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                        ),
                        padding=ft.padding.only(bottom=10)
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                reg_user,
                                reg_email,
                                reg_pass,
                                ft.Container(
                                    content=ft.Column(controls=[barra_fortaleza, indicador_txt], spacing=4),
                                    padding=ft.padding.only(left=4)
                                ),
                                analizar_btn,
                                groq_panel,
                                ft.Divider(height=1, color="#2a2f3d"),
                                reg_pass_confirm,
                                ft.Container(height=6),
                                register_btn,
                            ],
                            spacing=12,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor      = "#161923",
                        border_radius= 16,
                        padding      = ft.padding.symmetric(horizontal=28, vertical=28),
                        border       = ft.border.all(1, "#2a2f3d"),
                        shadow       = ft.BoxShadow(blur_radius=30, color="#00000060", offset=ft.Offset(0, 8)),
                        width        = 420,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=30),
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
