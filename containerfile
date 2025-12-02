FROM docker.io/library/python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY ./app /bat-app/app

# Remove database if there is any
RUN rm -rf /app/app/db/*
RUN rm -f /app/app/.env
RUN rm -f /app/app/.env_example

# Remove dotenv for containerized version
RUN sed -i 's/load_dotenv()//' /app/app/config/__init__.py

# Install deps

WORKDIR /app/app

CMD ["fastapi", "run"]
