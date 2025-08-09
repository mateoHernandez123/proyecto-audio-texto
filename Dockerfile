# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el archivo de requisitos e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto que usará la aplicación
EXPOSE 9000

# Comando para correr la aplicación
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
