FROM python:3.11-slim

WORKDIR /code/py_challenge_data_service/

COPY pyproject.toml README.md /code/py_challenge_data_service/
COPY src/ /code/py_challenge_data_service/src/

RUN python -m pip install .

ENTRYPOINT [ "python", "-m", "py_challenge_data_service", "run", "--port", "8777" ]