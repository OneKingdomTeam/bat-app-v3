# BAT App v3

Main improvement is to set it free from Wordpress to allow for more flexibility while developing.

The functions by themselves are pretty much the same as they were but further development should be much much easier.


## Setup instructions

For setup there are 2 things needed to do + one optinal.

1) Set encryption key.
2) Add default user and questions
3) Optional: Set SMTP settings for the app

### 1) Set encryption key

We are using 32 character long hex string. Easiest way to generate it is through OpenSSL

```bash
openssl rand -hex 32
```
Then store the value in the .env file

### 2) Set credentials for default user and add questions

These values are also stored in the .env file. So either edit that or copy the example into the `.env`

Make sure you are in the repository root directory. Not in the `app` folder but one above it.

```bash
export PYTHONPATH="$( pwd )"
```

Now run python in interactive mode and add default user.

```bash
python -i app/main.py
```

Now just import add default user and question function and execute.

```python
from app.service.user import add_default_user
from app.service.question import add_default_questions
add_default_user()
add_default_questions()
```
## Run the app

With that out of the way the app can be runned. Navigate to the app folder and run it:

```bash
fastapi run
```


## Podman Compose / Docker Compose

There is example `compose.yml` in the repository

Compose file is preapred to use the bat-app:latest version of the container.

## Building the container

Repository contains the containerfile that instructs podman how to build the container.

For that you can simply run: 

```bash
podman build -f containerfile -t bat-app:<version> .
```


