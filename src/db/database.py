
import bcrypt
import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Any

# --- MODELOS DE DATOS ---
# User y entry para representar los objetos con los que se trabaja en las querys


@dataclass(frozen=True)
class User:
    """Representa un usuario en el sistema."""

    id: int
    username: str


@dataclass(frozen=True)
class Entry:
    """Representa una credencial almacenada en la bóveda."""

    id: int
    site_name: str
    site_user: str
    site_password: str

    def __str__(self):
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


class AuthManager:
    def __init__(self, db: Database):
        self.db = db

    def login(self, username: str, password: str) -> Optional[User]:
        """
        Verifica credenciales para el acceso al programa.
        """
        query = "SELECT id, password_hash FROM credentials WHERE username = ?;"
        row = self.db.execute(query, (username,), fetchone=True)

        try:
            if row and bcrypt.checkpw(password.encode("utf-8"), row[1].encode("utf-8")):
                # Retornamos el objeto User
                return User(id=row[0], username=username)
            raise ValueError("Usuario o contraseña incorrectos")
        except Exception as e:
            print(e)

    def change_master_password(self, password: str):
        raise NotImplementedError("")

    def register_user(self, username: str, password: str) -> int:
        """
        Registra un nuevo usuario en la tabla de acceso
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)

        query = "INSERT INTO credentials (username, password_hash) VALUES (?, ?) RETURNING id;"
        row = self.db.execute(query, (username, hashed.decode("utf-8")), fetchone=True)
        return row[0]

    # TODO
    def delete():
        raise NotImplementedError("Delete no implementado")


class VaultManager:
    def __init__(self, db: Database):
        self.db = db

    def add(self, user_id: int, site: str, user: str, password: str) -> None:
        """
        Añade una entrada a la tabla
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        query = "INSERT INTO vault (user_id, site_name, site_user, site_password) VALUES (?, ?, ?, ?);"
        self.db.execute(query, (user_id, site, user, hashed))

    def list_all_entries(self, user_id: int) -> List[Entry]:
        """
        Recupera todas las entradas de un usuario y las mapea a objetos Entry.
        """
        # Obtenemos el nombre del servicio, nombre de usuario y contraseña
        rows = self.db.execute(
            "SELECT id, site_name, site_user, site_password FROM vault WHERE user_id = ?;",
            (user_id,),
            fetch=True,
        )

        # Devuelve las coincidencias como una lista de objetos `Entry`
        return [Entry(*row) for row in rows]

    def list_by_site_name(self, user_id: int, site_name: "str"):
        """
        Aplica búsquedas por patrones para encontrar coincidencias similares según el nombre del servicio
        """
        raise NotImplementedError("")

    def delete_by_site(self, site_name: str, user_id: int):
        """
        Elimina una entrada que coincidan con el nombre del sitio
        """
        query = "DELETE FROM vault WHERE site_name = ? AND user_id = ?;"
        self.db.execute(query, (site_name, user_id))

    def delete_by_id(self, entry_id: int, user_id: int):
        """Borrado seguro por ID."""
        query = "DELETE FROM vault WHERE id = ? AND user_id = ?;"
        self.db.execute(query, (entry_id, user_id))
