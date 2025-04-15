FROM python:3.12-slim

WORKDIR /code/user_interface/

COPY pyproject.toml /code/user_interface/
COPY src/ /code/user_interface/src/

RUN python -m pip install .

ENTRYPOINT [ "python", "-m", "streamlit", "run", "src/app.py"]