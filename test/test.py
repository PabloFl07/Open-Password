"""
main.py – Punto de entrada de Open Password Manager

  · Si NO existe passmanager.db  →  registro inicial (register.py)
  · Si     existe passmanager.db  →  gestor de contraseñas (user_interface.py)
"""

from pathlib import Path
import flet as ft

DB_PATH = Path(__file__).parent / "passmanager.db"


def _launch_register():
    import register2 as _reg
    ft.run(_reg.main)          # target= evita ambigüedad con 'main' local


def _launch_vault():
    import user_interface as _ui
    ft.run(_ui.main)


if __name__ == "__main__":
    if not DB_PATH.exists():
        print("🔧 Primera ejecución: abriendo configuración inicial…")
        _launch_register()

        if DB_PATH.exists():
            print("✅ Bóveda creada. Iniciando gestor de contraseñas…")
            _launch_vault()
        else:
            print("⚠️  El registro fue cancelado. No se creó la base de datos.")
    else:
        print("🔓 Base de datos encontrada. Iniciando gestor de contraseñas…")
        _launch_vault()