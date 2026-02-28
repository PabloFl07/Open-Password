
# TODO: validación de correo electrónico

# ! El campo username, user_id no son necesarios para un programa personal, pero facilitan la implementacion de varios usuarios
 
from database import Database, AuthManager
import getpass
from llm import AiModel
from database import Verify


def setup_sqlite(db: Database):
    # Tabla de Credenciales

    auth = AuthManager(db)
    db.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            two_fa_contact TEXT NOT NULL
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
    # Registrar al usuario principal
    admin_user = input("Introduce nombre de usuario admin: ")
    admin_pass = getpass.getpass("Introduce contraseña admin: ")
    
    # 1. Validar la primera contraseña ingresada
    req = Verify.validate_password(admin_pass)
    ai = AiModel()
    if ai.buscar_en_dataset(admin_pass):
        req.append("La contraseña se encuentra en un diccionario de contraseñas robadas, prueba con otra!")

    # 2. Mientras la lista de requisitos NO esté vacía...
    while len(req) > 0:
        print(f"❌ Esta contraseña no es segura, le falta: {', '.join(req)}")
        
        # Volvemos a pedir
        admin_pass = getpass.getpass("Inténtalo de nuevo: ")
        
        # 3. Volvemos a validar el nuevo intento
        req = Verify.validate_password(admin_pass)
        if ai.buscar_en_dataset(admin_pass):
            req.append("La contraseña se encuentra en un diccionario de contraseñas robadas, prueba con otra!")

    print("✅ ¡Contraseña establecida con éxito!")
    
    two_fa_contact = input("Correo de recuperación: ")

    auth.register_user(admin_user, admin_pass, two_fa_contact)



if __name__ == "__main__":
    db = Database("passmanager.db") 
    setup_sqlite(db)
    print("Base de datos SQLite lista.")