# Project
This project exists only to show strange behavior during one or more rollbacks in a session containing several side objects.

Maybe a bug? Or just my lack of knowledge about SQLAlchemy 

# Init Project
```sh
python3 -m venv venv
. ./venv/bin/activate
python3 -m pip install -r requirements.txt
alembic upgrade head
```

# Launch script
```sh
python3 main.py
```
