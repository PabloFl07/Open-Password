import flet as ft
from database import Database, AuthManager, VaultManager, User
from encryption import EncryptionManager
from pathlib import Path
import sqlite3
import logging
import threading
from datetime import datetime
from database import Database, AuthManager, Verify
from llm import AiModel
import os

DB_PATH = str(Path(__file__).parent / "passmanager.db")


class AppSession:
    def __init__(self):
        self.db: Database | None = None
        self.auth: AuthManager | None = None
        self.vault: VaultManager | None = None
        self.user: User | None = None


def main(page: ft.Page):
    page.title = "Open Password Manager"
    page.window_width = 960
    page.window_height = 640
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    session = AppSession()
    if os.path.exists(DB_PATH):
        session.db   = Database(DB_PATH)
        session.auth = AuthManager(session.db)

    def show_snack(msg: str, color=ft.Colors.GREEN_400):
        snack = ft.SnackBar(
            content=ft.Text(msg, color=ft.Colors.WHITE),
            bgcolor=color,
            open=True,
        )
        page.overlay.append(snack)
        page.update()

    def go_to_vault():
        page.overlay.clear()
        page.controls.clear()
        page.add(build_vault_view())
        page.update()

    def go_to_login():
        session.user = None
        session.vault = None
        page.overlay.clear()
        page.controls.clear()
        page.add(build_login_view())
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    #  VISTA LOGIN
    # ══════════════════════════════════════════════════════════════════════════
    def build_login_view():
        error_label    = ft.Text("", color=ft.Colors.RED_400, size=13)
        username_field = ft.TextField(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            width=340,
            autofocus=True,
        )
        password_field = ft.TextField(
            label="Contraseña Maestra",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            width=340,
        )
        login_btn = ft.Button(
            "Desbloquear Bóveda",
            icon=ft.Icons.LOCK_OPEN_OUTLINED,
            width=340,
            height=46,
        )
        loading = ft.ProgressRing(width=20, height=20, visible=False)

        def on_login(e):
            username = username_field.value.strip()
            password = password_field.value

            if not username or not password:
                error_label.value = "Completa todos los campos."
                page.update()
                return

            login_btn.disabled = True
            loading.visible = True
            error_label.value = ""
            page.update()

            user_data = session.auth.login(username, password)

            if user_data:
                engine = EncryptionManager(password, user_data.salt)
                password = " "
                session.vault = VaultManager(session.db, engine)
                session.user  = user_data
                go_to_vault()
            else:
                password = " "
                error_label.value = "Usuario o contraseña incorrectos."
                login_btn.disabled = False
                loading.visible = False
                page.update()

        login_btn.on_click       = on_login
        password_field.on_submit = on_login
        if os.path.exists(DB_PATH):
            return ft.Container(
                content=ft.Column(
                [
                    ft.Icon(ft.Icons.SHIELD_OUTLINED, size=64, color=ft.Colors.BLUE_300),
                    ft.Text("Open Password Manager", size=26, weight=ft.FontWeight.BOLD),
                    ft.Text("Identifícate para continuar", size=14, color=ft.Colors.GREY_400),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    username_field,
                    password_field,
                    error_label,
                    ft.Row(
                        [login_btn, loading],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
            ),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        else:
            '''page.title        = "Registro de Usuario"
            page.window_width  = 480
            page.window_height = 820
            page.theme_mode    = ft.ThemeMode.DARK
            page.vertical_alignment   = ft.MainAxisAlignment.CENTER
            page.horizontal_alignment = ft.CrossAxisAlignment.CENTER'''
            page.bgcolor = "#0f1117"
            page.scroll  = ft.ScrollMode.AUTO

            try:
                db   = Database(DB_PATH)
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
            db.execute("""
                CREATE TABLE IF NOT EXISTS vault (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id       INTEGER NOT NULL,
                    site_name     TEXT NOT NULL,
                    site_user     TEXT NOT NULL,
                    site_password TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES credentials (id) ON DELETE CASCADE
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
                    # Inicializar sesión con la DB recién creada
                    session.db   = db
                    session.auth = AuthManager(db)

                    mostrar_snack("¡Cuenta creada! Inicia sesión.", ft.Colors.GREEN_700)
                    page.window_width  = 960
                    page.window_height = 640
                    page.bgcolor       = None
                    page.scroll        = ft.ScrollMode.HIDDEN
                    page.update()
                    # Ir al login (la DB ya existe, mostrará el formulario de login)
                    go_to_login()

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
                "Analizar con IA",
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
                padding       = ft.Padding.all(12),
                border        = ft.Border.all(1, "#1e3a5f"),
                width         = 340,
            )

            register_btn = ft.Button(
                "Crear cuenta",
                on_click = btn_register_click,
                width    = 340,
                height   = 48,
                style    = ft.ButtonStyle(
                    bgcolor = {ft.ControlState.DEFAULT: ft.Colors.BLUE_700},
                    color   = {ft.ControlState.DEFAULT: ft.Colors.WHITE},
                )
            )


            return    ft.Container(
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
                                padding=ft.Padding.only(bottom=10)
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        reg_user,
                                        reg_email,
                                        reg_pass,
                                        ft.Container(
                                            content=ft.Column(controls=[barra_fortaleza, indicador_txt], spacing=4),
                                            padding=ft.Padding.only(left=4)
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
                                padding      = ft.Padding.symmetric(horizontal=28, vertical=28),
                                border       = ft.Border.all(1, "#2a2f3d"),
                                shadow       = ft.BoxShadow(blur_radius=30, color="#00000060", offset=ft.Offset(0, 8)),
                                width        = 420,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding.symmetric(vertical=30),
                )

    # ══════════════════════════════════════════════════════════════════════════
    #  VISTA BÓVEDA
    # ══════════════════════════════════════════════════════════════════════════
    def build_vault_view():
        entries = session.vault.list_all_entries(session.user.id)

        # ── detail dialog ─────────────────────────────────────────────────────
        # Flet >=0.81 exige contenido al añadir al overlay
        def close_detail():
            page.close(detail_dialog)

        detail_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(""),
            content=ft.Text(""),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: close_detail())],
        )

        def show_detail(entry):
            detail_dialog.title = ft.Text(
                f"🔐 {entry.site_name}", weight=ft.FontWeight.BOLD
            )
            detail_dialog.content = ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON),
                        title=ft.Text("Usuario"),
                        subtitle=ft.Text(entry.site_user, selectable=True),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.KEY),
                        title=ft.Text("Contraseña"),
                        subtitle=ft.Text(
                            entry.site_password,
                            selectable=True,
                            font_family="monospace",
                        ),
                    ),
                ],
                tight=True,
                spacing=0,
            )
            page.open(detail_dialog)

        # ── add dialog ────────────────────────────────────────────────────────
        site_f = ft.TextField(label="Servicio / Sitio web", autofocus=True)
        user_f = ft.TextField(label="Usuario / Correo")
        pass_f = ft.TextField(
            label="Contraseña (vacío = generar automáticamente)",
            password=True,
            can_reveal_password=True,
        )
        err_f = ft.Text("", color=ft.Colors.RED_400, size=12)

        # FIX: add_dialog definido ANTES de close_add para evitar referencia forward
        add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("➕ Nueva Entrada"),
            content=ft.Column(
                [site_f, user_f, pass_f, err_f],
                tight=True,
                spacing=10,
                width=340,
            ),
            actions=[ft.Text("")],  # placeholder; se reemplaza abajo
        )

        def close_add():
            page.close(add_dialog)

        def save_entry(e):
            site = site_f.value.strip()
            usr  = user_f.value.strip()
            pwd  = pass_f.value.strip() or None

            if not site or not usr:
                err_f.value = "Servicio y usuario son obligatorios."
                page.update()
                return

            session.vault.add(session.user.id, site, usr, pwd or "__generate__")
            page.close(add_dialog)
            go_to_vault()
            show_snack("Entrada guardada correctamente.")

        add_dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda _: close_add()),
            ft.Button("Guardar", on_click=save_entry),
        ]

        def show_add_dialog(e):
            site_f.value = ""
            user_f.value = ""
            pass_f.value = ""
            err_f.value  = ""
            page.open(add_dialog)


        # ── confirm delete dialog ──────────────────────────────────────────────
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar eliminación"),
            content=ft.Text(""),
            actions=[ft.Text("")],  # placeholder
        )

        def close_confirm():
            page.close(confirm_dialog)

        def do_delete(entry_id: int, site_name: str):
            session.db.execute(
                "DELETE FROM vault WHERE id = ? AND user_id = ?;",
                (entry_id, session.user.id),
            )
            page.close(confirm_dialog)
            go_to_vault()
            show_snack(f"Entrada \"{site_name}\" eliminada.")

        def show_confirm_delete(entry_id: int, site_name: str):
            confirm_dialog.content = ft.Text(
                f"¿Seguro que quieres eliminar \"{site_name}\"?\nEsta acción no se puede deshacer.",
            )
            confirm_dialog.actions = [
                ft.TextButton("Cancelar", on_click=lambda _: close_confirm()),
                ft.Button(
                    "Eliminar",
                    on_click=lambda _, eid=entry_id, sn=site_name: do_delete(eid, sn),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.RED_700,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ]
            page.open(confirm_dialog)


        # ── tabla ─────────────────────────────────────────────────────────────
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Servicio",   weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario",    weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Contraseña", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones",   weight=ft.FontWeight.BOLD)),
            ],
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
            heading_row_color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            data_row_max_height=56,
            expand=True,
        )

        def make_row(entry):
            def on_copy(e, pwd=entry.site_password):
                try:
                    import pyperclip
                    pyperclip.copy(pwd)
                    show_snack("¡Contraseña copiada al portapapeles!")
                except Exception as ex:
                    show_snack(f"Error al copiar: {ex}", ft.Colors.RED_400)

            def on_view(e, ent=entry):
                show_detail(ent)

            def on_delete(e, eid=entry.id, sn=entry.site_name):
                show_confirm_delete(eid, sn)


            return ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.WEB_OUTLINED, size=16, color=ft.Colors.BLUE_300),
                                ft.Text(entry.site_name, weight=ft.FontWeight.W_500),
                            ],
                            spacing=8,
                        )
                    ),
                    ft.DataCell(ft.Text(entry.site_user, color=ft.Colors.GREY_300)),
                    ft.DataCell(
                        ft.Text("•" * 12, font_family="monospace", color=ft.Colors.GREY_500)
                    ),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.CONTENT_COPY_OUTLINED,
                                    icon_color=ft.Colors.BLUE_300,
                                    icon_size=20,
                                    tooltip="Copiar contraseña",
                                    on_click=on_copy,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY_OUTLINED,
                                    icon_color=ft.Colors.GREEN_300,
                                    icon_size=20,
                                    tooltip="Ver detalles",
                                    on_click=on_view,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_300,
                                    icon_size=20,
                                    tooltip="Eliminar entrada",
                                    on_click=on_delete,
                                ),
                            ],
                            spacing=2,
                        )
                    ),
                ]
            )

        def refresh_table(query: str = ""):
            q = query.lower()
            filtered = (
                entries if not q
                else [e for e in entries if q in e.site_name.lower() or q in e.site_user.lower()]
            )
            if filtered:
                table.rows = [make_row(e) for e in filtered]
            else:
                table.rows = [
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(
                            "Sin resultados." if q else "La bóveda está vacía.",
                            italic=True, color=ft.Colors.GREY_500,
                        )),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ])
                ]
            page.update()

        refresh_table()

        # ── toolbar ───────────────────────────────────────────────────────────
        search_field = ft.TextField(
            label="Buscar servicio o usuario…",
            prefix_icon=ft.Icons.SEARCH,
            width=260,
            height=44,
            on_change=lambda e: refresh_table(e.control.value),
        )

        toolbar = ft.Row(
            [
                ft.Button(
                    "➕  Añadir Entrada",
                    on_click=show_add_dialog,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE,
                    ),
                ),
                search_field,
                ft.Row(
                    [
                        ft.Icon(ft.Icons.PERSON_OUTLINE, color=ft.Colors.GREY_400, size=16),
                        ft.Text(session.user.username, color=ft.Colors.GREY_300, size=13),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            tooltip="Cerrar sesión",
                            icon_color=ft.Colors.RED_300,
                            on_click=lambda _: go_to_login(),
                        ),
                    ],
                    spacing=4,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        stats_row = ft.Row([
            ft.Container(
                ft.Column(
                    [
                        ft.Text(
                            str(len(entries)),
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_300,
                        ),
                        ft.Text("Entradas", size=12, color=ft.Colors.GREY_400),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                border_radius=10,
                padding=ft.Padding.symmetric(vertical=12, horizontal=24),
            ),
        ])

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.SHIELD, color=ft.Colors.BLUE_300, size=22),
                                ft.Text("Open Password Manager", size=20, weight=ft.FontWeight.BOLD),
                            ],
                            spacing=10,
                        ),
                        padding=ft.Padding.symmetric(vertical=14, horizontal=20),
                        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
                    ),
                    ft.Container(
                        ft.Column(
                            [
                                toolbar,
                                ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                                stats_row,
                                ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                                ft.Column([table], scroll=ft.ScrollMode.AUTO, expand=True),
                            ],
                            expand=True,
                            spacing=10,
                        ),
                        padding=ft.Padding.symmetric(vertical=16, horizontal=20),
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )

    page.add(build_login_view())


if __name__ == "__main__":
    ft.run(main)