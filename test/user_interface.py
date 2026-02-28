import flet as ft
from database import Database, AuthManager, VaultManager, User
from encryption import EncryptionManager
from pathlib import Path

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
    session.db = Database(DB_PATH)
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

    # ══════════════════════════════════════════════════════════════════════════
    #  VISTA BÓVEDA
    # ══════════════════════════════════════════════════════════════════════════
    def build_vault_view():
        entries = session.vault.list_all_entries(session.user.id)

        # ── detail dialog ─────────────────────────────────────────────────────
        # Flet >=0.81 exige contenido al añadir al overlay
        def close_detail():
            detail_dialog.open = False
            page.update()

        detail_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(""),
            content=ft.Text(""),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: close_detail())],
        )
        page.overlay.append(detail_dialog)

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
            detail_dialog.open = True
            page.update()

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
            add_dialog.open = False
            page.update()

        def save_entry(e):
            site = site_f.value.strip()
            usr  = user_f.value.strip()
            pwd  = pass_f.value.strip() or None

            if not site or not usr:
                err_f.value = "Servicio y usuario son obligatorios."
                page.update()
                return

            session.vault.add(session.user.id, site, usr, pwd or "__generate__")
            go_to_vault()  # limpia overlay internamente, no hace falta close_add()
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
            add_dialog.open = True
            page.update()

        page.overlay.append(add_dialog)

        # ── confirm delete dialog ──────────────────────────────────────────────
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar eliminación"),
            content=ft.Text(""),
            actions=[ft.Text("")],  # placeholder
        )
        page.overlay.append(confirm_dialog)

        def close_confirm():
            confirm_dialog.open = False
            page.update()

        def do_delete(entry_id: int, site_name: str):
            session.db.execute(
                "DELETE FROM vault WHERE id = ? AND user_id = ?;",
                (entry_id, session.user.id),
            )
            go_to_vault()  # limpia overlay internamente, no hace falta close_confirm()
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
            confirm_dialog.open = True
            page.update()


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