# Dockerfile
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear y establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar proyecto
COPY . .

# Crear carpeta para logs
RUN mkdir -p /app/logs

# Crear usuario no root para seguridad
RUN adduser --disabled-password --gecos '' django-user
RUN chown -R django-user:django-user /app
USER django-user

# Puerto expuesto
EXPOSE 8000

# Comando para ejecutar la aplicación - CAMBIADO A 127.0.0.1
CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]