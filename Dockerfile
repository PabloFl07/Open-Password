FROM python:3.13-slim

# Instalamos dependencias del sistema para Flet
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos requerimientos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos TODO el contenido de tu proyecto a /app
COPY . .

# Creamos la carpeta de datos y damos permisos totales
RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 8000

# Ejecutamos apuntando a la carpeta src donde está tu archivo
CMD ["python", "src/interface.py"]