from database import Database, AuthManager
import getpass

def setup_sqlite(db: Database):
    # Tabla de Credenciales

    auth = AuthManager(db)
    db.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    ''')
    
    # Tabla de Bóveda
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

    # Registrar al usuario principal
    admin_user = input("Introduce nombre de usuario admin: ")
    admin_pass = getpass.getpass("Introduce contraseña admin: ")

    auth.register_user(admin_user, admin_pass)



if __name__ == "__main__":
    db = Database("passmanager.db")
    setup_sqlite(db)
    print("Base de datos SQLite lista.")