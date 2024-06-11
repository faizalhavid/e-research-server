FROM python:3.11.4-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /core

# Install PostgreSQL development packages
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt .
# Install requirements
RUN pip install -r requirements.txt

COPY . .

CMD python manage.py runserver 0.0.0.0:80