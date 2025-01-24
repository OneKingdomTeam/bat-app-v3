FROM docker.io/library/python:3.11-slim

WORKDIR /bat-app

COPY ./requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY ./app /bat-app/app

# Remove database if there is any
RUN rm -rf /bat-app/app/db/*
RUN rm /bat-app/app/.env
RUN rm /bat-app/app/.env_example

# Remove dotenv for containerized version
RUN sed -i 's/load_dotenv()//' /bat-app/app/config/__init__.py

# Install deps

WORKDIR /bat-app/app

CMD ["fastapi", "run"]
