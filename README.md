# Gestor de Olesa
Gestor de Olesa es un gestor de contraseñas completo, permite generar, guardar y gestionar contraseñas de forma segura. 

### Avisos de seguridad !
1. Todos los datos que introduzcas en la base de datos estarán completamente cifrados
2. Las contraseñas que generamos para ti ya son seguras
3. La IA usa una cadena transformada a partir de tu contraseña para analizarla, nunca la tuya

### Modo de uso
La aplicación se puede desplegar desde un contenedor docker:


```
git clone https://github.com/PabloFl07/Open-Password.git

cd Open-Password
```

Crea un archivo `.env` y añade una clave API para poder usar la IA

```
docker-compose up -d --build
```

Ahora puedes conectarte al localhost por el puerto 8000 y acceder a la aplicación

### Requirements
```
pip install -r requirements.txt
```


### Features
Esta aplicación permite la implementación sencilla de uso multiusuario por su lógica y estructura
