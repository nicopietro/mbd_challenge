FROM python:3.12-slim

WORKDIR /code/ml_service/

COPY pyproject.toml /code/ml_service/
COPY src/ /code/ml_service/src/

RUN python -m pip install .

ENTRYPOINT [ "python", "-m", "src", "run"]