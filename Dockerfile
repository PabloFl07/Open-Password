# Usamos una versión ligera de Python
FROM python:3.13-slim

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias para Flet y librerías de Python
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiamos e instalamos dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la carpeta src al contenedor
COPY src/ .

# Exponemos el puerto 8000 que configuramos en interface.py
EXPOSE 8000

# Ejecutamos la aplicación
CMD ["python", "interface.py"]
