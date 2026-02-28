import flet as ft
from pathlib import Path
from database import Database, AuthManager, Verify
from llm import AiModel

DB_PATH = str(Path(__file__).parent / "passmanager.db")


def _create_tables(db: Database):
    db.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            two_fa_contact TEXT NOT NULL
        );
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            site_name TEXT NOT NULL,
            site_user TEXT NOT NULL,
            site_password TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES credentials (id) ON DELETE CASCADE
        );
    ''')


def main(page: ft.Page):
    page.title = "Open Password Manager – Configuración inicial"
    page.window_width  = 520
    page.window_height = 660
    page.theme_mode    = ft.ThemeMode.DARK
    page.padding       = 0

    # ── Campos ────────────────────────────────────────────────────────────────
    username_field = ft.TextField(
        label="Nombre de usuario",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        width=380,
        autofocus=True,
    )
    email_field = ft.TextField(
        label="Correo de recuperación",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        width=380,
    )
    password_field = ft.TextField(
        label="Contraseña maestra",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        width=380,
    )
    confirm_field = ft.TextField(
        label="Confirmar contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_RESET_OUTLINED,
        width=380,
    )

    error_label   = ft.Text("", color=ft.Colors.RED_400,   size=13, width=380)
    success_label = ft.Text("", color=ft.Colors.GREEN_400, size=13, width=380)
    ai_result     = ft.Text("", color=ft.Colors.BLUE_200,  size=12, width=380, selectable=True)
    loading       = ft.ProgressRing(width=22, height=22, visible=False)

    # Flet >= 0.80: primer argumento posicional, NO text=
    register_btn = ft.FilledButton(
        "Crear bóveda",
        icon=ft.Icons.SHIELD_OUTLINED,
        width=380,
        height=48,
    )
    analizar_btn = ft.OutlinedButton(
        "Analizar seguridad con IA",
        icon=ft.Icons.ANALYTICS_OUTLINED,
        width=380,
    )

    def show_error(msg: str):
        error_label.value     = msg
        success_label.value   = ""
        loading.visible       = False
        register_btn.disabled = False
        page.update()

    def on_analyze(e):
        password = password_field.value
        if not password:
            show_error("❌ Introduce una contraseña primero.")
            return

        req = Verify.validate_password(password)
        if req:
            show_error(f"❌ {req[0]}")
            return

        analizar_btn.disabled = True
        ai_result.value       = "⏳ Analizando con IA…"
        error_label.value     = ""
        page.update()

        try:
            ai           = AiModel()
            ai_result.value = ai.consultar_seguridad(password)
        except Exception as ex:
            ai_result.value = f"⚠️ No se pudo contactar con la IA: {ex}"
        finally:
            analizar_btn.disabled = False
            page.update()

    def on_register(e):
        username = username_field.value.strip()
        email    = email_field.value.strip()
        password = password_field.value
        confirm  = confirm_field.value

        error = Verify.validar_campos(username, email, password, confirm)
        if error:
            show_error(f"❌ {error}")
            return

        register_btn.disabled = True
        loading.visible       = True
        error_label.value     = ""
        page.update()

        ai = AiModel()
        if ai.buscar_en_dataset(password):
            show_error("❌ La contraseña aparece en un diccionario de contraseñas comprometidas.")
            return

        try:
            db   = Database(DB_PATH)
            _create_tables(db)
            auth = AuthManager(db)
            auth.register_user(username, password, email)
            db.close_all()
        except Exception as ex:
            show_error(f"❌ Error al crear la bóveda: {ex}")
            return

        loading.visible       = False
        register_btn.disabled = True
        success_label.value   = "✅ ¡Bóveda creada! Iniciando el gestor…"
        page.update()
        page.window_destroy()

    register_btn.on_click   = on_register
    analizar_btn.on_click   = on_analyze
    confirm_field.on_submit = on_register

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.SECURITY, size=60, color=ft.Colors.BLUE_300),
                    ft.Text("Configuración Inicial", size=26, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Primera ejecución – crea tu bóveda personal",
                        size=13,
                        color=ft.Colors.GREY_400,
                    ),
                    ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
                    username_field,
                    email_field,
                    password_field,
                    confirm_field,
                    analizar_btn,
                    ai_result,
                    error_label,
                    success_label,
                    ft.Row(
                        [register_btn, loading],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                    ft.Text(
                        "La contraseña maestra cifra todos tus datos.\nNo existe forma de recuperarla si la olvidas.",
                        size=11,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.padding.symmetric(vertical=30, horizontal=20),
        )
    )


if __name__ == "__main__":
    ft.run(main)