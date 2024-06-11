FROM python:3.11.4-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /core

# Install PostgreSQL development packages and netcat for the entrypoint script
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev netcat-openbsd

COPY requirements.txt .
# Install requirements
RUN pip install -r requirements.txt

COPY . .

# Copy the entrypoint script and set it as the entrypoint
COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]