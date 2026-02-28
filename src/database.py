import bcrypt
import sqlite3
import base64
from dataclasses import dataclass
from typing import Optional, List, Any
from encryption import EncryptionManager
import secrets
import re

# --- MODELOS DE DATOS ---
# User y entry para representar los objetos con los que se trabaja en las querys


@dataclass(frozen=True)
class User:
    """Representa un usuario en el sistema."""

    id: int
    username: str
    salt : str


@dataclass(frozen=True)
class Entry:
    """Representa una credencial almacenada en la bóveda."""

    id: int
    site_name: str
    site_user: str
    site_password: str

    def __str__(self):

        return f"Servicio: {self.site_name} | Usuario: {self.site_user} | Contraseña: {'*' * 10}"

    # ! Implementado con un botón en la UI
    def display(self) -> str: 
        """Muestra la contraseña en texto plano. Usar con precaución."""
        return f"Servicio: {self.site_name} | Usuario: {self.site_user} | Contraseña: {self.site_password}"


class Database:
    """Gestiona la conexión al archivo .db local de SQLite."""

    def __init__(self, db_name: str = "passmanager.db"):
        try:
            # check_same_thread=False permite que Auth y Vault compartan la db
            # de forma segura en aplicaciones simples
            self._conn = sqlite3.connect(db_name, check_same_thread=False)
            self._conn.row_factory = (
                sqlite3.Row
            )  # Permite acceso por nombre de columna si se desea
        except Exception as e:
            raise ConnectionError(f"Error al conectar con SQLite: {e}")

    def execute(
        self,
        query: str,
        params: tuple = (),
        fetch: bool = False,
        fetchone: bool = False,
    ) -> Any:
        """
        Ejecuta queries adaptando el placeholder de Postgres (%s) a SQLite (?)
        automáticamente si fuera necesario.
        """
        # Adaptación de sintaxis: PostgreSQL (%s) -> SQLite (?)

        try:
            with self._conn:  # Auto-commit / Rollback
                cur = self._conn.cursor()
                cur.execute(query, params)

                if fetchone:
                    return cur.fetchone()
                if fetch:
                    return cur.fetchall()
                return None
        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")
            raise

    def close_all(self):
        self._conn.close()


class Verify:

    @staticmethod
    def validar_campos(username: str, email: str, password: str, password_confirm: str) -> Optional[str]:
        if not all([username, email, password, password_confirm]):
            return "Por favor, rellena todos los campos."
        if password != password_confirm:
            return "Las contrasenas no coinciden."
        errores = Verify.validate_password(password)
        if errores:
            return errores[0]
        if not Verify.validate_email(email):
            return "El formato del correo no es valido."
        return None

    @staticmethod
    def validate_password(password:str) -> list[str]:
        requirements = []
        if len(password) < 12:
            requirements.append("La contraseña debe tener al menos 12 caracteres")
        if not re.search(r'[A-Z]', password):
            requirements.append("Debe contener al menos una mayúscula")
        if not re.search(r'[a-z]', password):
            requirements.append("Debe contener al menos una minúscula")
        if not re.search(r'\d', password):
            requirements.append("Debe contener al menos un número")
        if not re.search(r'[^A-Za-z0-9]', password):
            requirements.append("Debe contener al menos un caracter especial")

        return requirements

    @staticmethod
    def validate_email(email: str) -> bool:
        """FIX #5: Validación básica de formato de correo electrónico."""
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

# ... (Imports y DataClasses se mantienen igual) ...

class AuthManager:
    def __init__(self, db: Database):
        self.db = db

    def login(self, username: str, password: str) -> Optional[User]:
        # CORRECCIÓN: Añadido 'salt' a la consulta SQL
        query = "SELECT id, password_hash, salt FROM credentials WHERE username = ?;"
        row = self.db.execute(query, (username,), fetchone=True)

        try:
            if row and bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
                # CORRECCIÓN: Acceso por nombre de columna (sqlite3.Row)
                return User(id=row["id"], username=username, salt=row["salt"])
            return None
        except Exception as e:
            print(f"Error en login: {e}")
            return None

    def register_user(self, username: str, password: str, two_fa_contact: str) -> int:

        if not Verify.validate_email(two_fa_contact):
            raise ValueError("Formato de correo electrónico inválido.")


        salt_login = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt_login)

        # Salt para el cifrado AES-GCM
        salt_encrypt = secrets.token_bytes(16)
        salt_encrypt_str = base64.b64encode(salt_encrypt).decode('utf-8')

        # SQLite soporta RETURNING id en versiones recientes
        query = "INSERT INTO credentials (username, password_hash, salt, two_fa_contact) VALUES (?, ?, ?, ?) RETURNING id;"
        row = self.db.execute(query, (username, hashed.decode("utf-8"), salt_encrypt_str, two_fa_contact), fetchone=True)
        return row[0]

class VaultManager:
    def __init__(self, db: Database, engine: EncryptionManager):
        self.engine = engine
        self.db = db

    def add(self, user_id: int, site: str, user: str, password: str | None = None) -> None:
        # FIX #1: Cifrar también site_name y site_user
        encrypted_site = self.engine.encrypt(site)
        encrypted_user = self.engine.encrypt(user)
        plain_pass     = self.engine.generate_password() if (not password or password == "__generate__") else password
        encrypted_pass = self.engine.encrypt(plain_pass)
        query = "INSERT INTO vault (user_id, site_name, site_user, site_password) VALUES (?, ?, ?, ?);"
        self.db.execute(query, (user_id, encrypted_site, encrypted_user, encrypted_pass))

    def list_all_entries(self, user_id: int) -> List[Entry]:
        rows = self.db.execute(
            "SELECT id, site_name, site_user, site_password FROM vault WHERE user_id = ?;",
            (user_id,),
            fetch=True,
        )

        decrypted_entries = []
        for row in rows:
            # FIX #1: Descifrar todos los campos
            decrypted_entries.append(Entry(
                id=row["id"],
                site_name=self.engine.decrypt(row["site_name"]),
                site_user=self.engine.decrypt(row["site_user"]),
                site_password=self.engine.decrypt(row["site_password"]),
            ))
        return decrypted_entries