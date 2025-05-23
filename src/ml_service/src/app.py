from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated, List

import pandas as pd
from annotated_types import Gt
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sklearn.base import BaseEstimator

from src.data_modeling import prepare_animal_data_for_training, train_animal_desicion_tree
from src.data_service_request import is_data_service_online
from src.minio_connection import (
    is_minio_online,
    minio_all_model_timestamps,
    minio_latest_model_timestamp_id,
    minio_retreive_model,
    minio_save_model,
)
from src.postgres_connection import (
    get_animals_between,
    insert_animals,
    is_postgres_online,
    wait_for_postgres,
)

# To run in bash: PYTHONPATH=src/ml_service uvicorn src.app:app --reload

MODELS = {}
DEFAULT_MODEL_ID = None


class Animal(BaseModel):
    height: Annotated[float, Gt(0)] = Field(..., description='Height in meters')
    weight: Annotated[float, Gt(0)] = Field(..., description='Weight in kilograms')
    walks_on_n_legs: Annotated[int, Gt(0)] = Field(
        ..., description='Number of legs used for walking'
    )
    has_wings: bool = Field(..., description='Whether the animal has wings')
    has_tail: bool = Field(..., description='Whether the animal has a tail')


AnimalList = Annotated[List[Animal], Field(min_length=1)]


def load_model(model_timestamp: str | None) -> BaseEstimator:
    """
    Loads a model from cache or MinIO. If more than 10 models are cached,
    the oldest one is removed.

    :param model_timestamp: Timestamp ID of the model to load. If None, uses the latest available.
    :return: The requested model or the lastest trained if not specified.
    """
    if model_timestamp is None:
        DEFAULT_MODEL_ID = minio_latest_model_timestamp_id()
        model_timestamp = DEFAULT_MODEL_ID

    if model_timestamp not in MODELS:
        if len(MODELS) >= 10:
            oldest_key = next(iter(MODELS))
            MODELS.pop(oldest_key)

        model = minio_retreive_model(model_timestamp)
        MODELS[model_timestamp] = model

    return MODELS[model_timestamp]


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_postgres()
    yield  # Startup complete


app = FastAPI(
    title='Animal Classifier API',
    description='API for classifying animals based on their features',
    version='0.4.0',
    lifespan=lifespan,
)

# TODO: Add endpoint to delete a model from MinIO and cache
# TODO: Add enpoint to list all models in MinIO and cache
# TODO: Add enpoint to save user_generated data into Postgres
# TODO: Add enpoint to retrieve user_generated data and use it for training
# TODO: Only for app (al least for now), create 5 unit tests and measure coverage


@app.get(
    '/api/v1/mpc/models',
    tags=['Machine Learning'],
    summary='List all models',
    description='Retrieves a list of all model timestamp IDs stored in MinIO.',
)
def list_models():
    """
    Endpoint to list all trained model timestamps stored in MinIO.

    :return: JSON response with a list of model IDs or error message.
    """
    try:
        model_ids = minio_all_model_timestamps()
        return JSONResponse(status_code=200, content={'models': model_ids})
    except ConnectionError as e:
        return JSONResponse(status_code=503, content={'error': str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})


@app.post(
    '/api/v1/mpc/train/synthetic',
    tags=['Machine Learning'],
    summary='Train a new model from synthetic data',
    description='Trains a new model using simulated animal data and saves it to MinIO.',
)
def traing_new_model(datapoints: int, seed: int = 42):
    """
    Trains a new model using simulated animal data and saves it to MinIO.

    :param datapoints: Number of synthetic datapoints to generate for training (must be > 0).
    :param seed: Random seed for data generation (default is 42).
    :return: JSON response with training status, model timestamp, and metrics.
    """

    if datapoints < 1:
        return JSONResponse(
            status_code=422, content={'error': 'Number of datapoints must be greater than 0.'}
        )

    df_cleaned = prepare_animal_data_for_training(datapoints=datapoints, seed=seed)

    try:
        model, metrics = train_animal_desicion_tree(df_cleaned)
    except ValueError as e:
        return JSONResponse(status_code=422, content={'error': str(e)})

    timestamp = minio_save_model(model=model, metrics=metrics)

    return JSONResponse(
        status_code=200,
        content={'status': 'Ok', 'trained_model_id': timestamp, 'model_metrics': metrics},
    )


@app.post(
    '/api/v1/mpc/train/userdata',
    tags=['Machine Learning'],
    summary='Train a new model from stored data',
    description="""Trains a new model using stored animal data in PostgreSQL
    between two timestamps and saves it to MinIO.""",
)
def train_model_from_stored_data(
    start: datetime = Query(
        default=datetime.now(),
        description='Start timestamp in ISO format',
        example='2025-04-20T12:00:00',
    ),
    end: datetime = Query(
        default=datetime.now() - timedelta(days=7),
        description='End timestamp in ISO format',
        example='2025-04-20T12:00:00',
    ),
):
    """
    Trains a model using real stored animal data from PostgreSQL between two timestamps.

    :param start: Start datetime (inclusive).
    :param end: End datetime (inclusive).
    :return: JSON response with training status, model timestamp, and metrics.
    """
    try:
        records = get_animals_between(start, end)
    except ValueError as e:
        return JSONResponse(status_code=503, content={'error': str(e)})

    if not records:
        return JSONResponse(
            status_code=404,
            content={'error': 'No data found in the specified time range.'},
        )

    try:
        model, metrics = train_animal_desicion_tree(pd.DataFrame(records))
    except ValueError as e:
        return JSONResponse(status_code=422, content={'error': str(e)})

    timestamp = minio_save_model(model=model, metrics=metrics)

    return JSONResponse(
        status_code=200,
        content={'status': 'Ok', 'trained_model_id': timestamp, 'model_metrics': metrics},
    )


@app.post(
    '/api/v1/mpc/predict',
    tags=['Machine Learning'],
    summary='Predict animal type',
    description='Predicts the animal type for a list of animal feature inputs using a trained model.',
)
def predict(
    animals: AnimalList,
    model_timestamp: str | None = Query(
        default=None,
        description='Optional model timestamp, if not specified, latests model will be used',
    ),
):
    """
    Predicts the animal type for a list of animal feature inputs using a trained model.

    :param animals: List of Animal objects with input features (height, weight, etc.).
    :param model_timestamp: Optional model timestamp ID. Uses latest if not provided.
    :return: JSON response with predicted animal types or error message.
    """

    try:
        model = load_model(model_timestamp)
    except ValueError as e:
        return JSONResponse(status_code=422, content={'error': str(e)})
    except ConnectionError as e:
        return JSONResponse(status_code=503, content={'error': str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})

    df = pd.DataFrame([a.model_dump() for a in animals])
    prediction = model.predict(df)
    print(prediction)

    results = []
    for animal, pred in zip(animals, prediction):
        result = animal.model_dump()
        result['animal_type'] = pred
        results.append(result)

    db_status = 'saved into postgresql'
    if not insert_animals(results):
        db_status = 'save to postgresql failed'

    return JSONResponse(
        status_code=200, content={'prediction': results, 'database_status': db_status}
    )


@app.get(
    '/api/v1/mpc/animals',
    tags=['Database'],
    summary='Retrieve stored animals',
    description='Returns all animal records stored in the database between two timestamps.',
)
def read_animals_between(
    start: datetime = Query(
        default=datetime.now(),
        description='Start timestamp in ISO format',
        example='2025-04-20T12:00:00',
    ),
    end: datetime = Query(
        default=datetime.now() - timedelta(days=7),
        description='End timestamp in ISO format',
        example='2025-04-20T12:00:00',
    ),
) -> List[dict]:
    """
    API endpoint to retrieve animal records stored between two datetimes.

    :param start: Start datetime (inclusive).
    :param end: End datetime (inclusive).
    :return: List of animal records.
    """
    try:
        return get_animals_between(start, end)
    except ValueError as e:
        return JSONResponse(status_code=503, content={'error': str(e)})


@app.get(
    '/health',
    tags=['Health'],
    summary='Health check',
    description="""Checks the health of the service and its dependencies
    (MinIO, PostgreSQL and Data Service API).""",
)
def health_check():
    """
    Health check endpoint to validate service dependencies
    (MinIO, PostgreSQL and Data Service API).

    :return: JSON response indicating system and dependency health.
    """

    status = {
        'status': 'ok',
        'minio': 'unknown',
        'postresql': 'unknown',
        'data_service_api': 'unknown',
    }

    # Check MinIO
    if is_minio_online():
        status['minio'] = 'reachable'
    else:
        status['minio'] = 'unreachable: Is Minio running?'
        status['status'] = 'error'

    # Check Data Service API
    if is_data_service_online():
        status['data_service_api'] = 'reachable'
    else:
        status['data_service_api'] = 'unreachable: Is data service running?'
        status['status'] = 'error'

    # Check PostgreSQL
    if is_postgres_online():
        status['postresql'] = 'reachable'
    else:
        status['postresql'] = 'unreachable: Is PostgreSQL running?'
        status['status'] = 'error'

    return status


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app:app', reload=True)
