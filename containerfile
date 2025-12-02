FROM docker.io/library/python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY ./app /bat-app/app

# Remove any database files that may have been copied
RUN rm -rf /bat-app/app/data/db/*.db* 2>/dev/null || true
RUN rm -f /bat-app/app/.env
RUN rm -f /bat-app/app/.env_example

# Remove dotenv for containerized version
RUN sed -i 's/load_dotenv()//' /bat-app/app/config/__init__.py

# Install deps

WORKDIR /bat-app/app

CMD ["fastapi", "run"]
