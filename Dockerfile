# Gunakan image Python sebagai basis
FROM python:3.9

# Set lingkungan kerja di container
WORKDIR /app

# Salin requirements.txt dan instal dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file proyek ke dalam container
COPY . /app/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Jalankan perintah untuk migrasi database dan memulai server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
