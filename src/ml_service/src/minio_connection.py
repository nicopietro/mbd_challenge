from datetime import datetime
import json
import os
from minio import Minio
import joblib
import socket
from sklearn.base import BaseEstimator

client = Minio(
    'minio:9000',
    access_key='minioadmin',
    secret_key='minioadmin',
    secure=False
)

def is_minio_online() -> bool:
    """
    Checks if the MinIO server is reachable.

    :return: True if MinIO is reachable, False otherwise.
    """
    try:
        host, port = client._base_url.host.split(':')
        with socket.create_connection((host, port), timeout=5.0):
            return True
    except Exception:
        return False


def minio_save_model(model: BaseEstimator, metrics: dict | None) -> str:
    """
    Saves a model and optional metrics to MinIO.

    :param model: Trained scikit-learn estimator.
    :param metrics: Optional performance metrics to store.
    :return: Model timestamp ID.
    :raises ConnectionError: If MinIO is not reachable.
    """

    if not is_minio_online():
        raise ConnectionError('MinIO server is not reachable.')
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Create a bucket if it doesn't exist
    if not client.bucket_exists('mpc'):
        client.make_bucket('mpc')

    with open('model_file.joblib', mode='wb') as file_:
        joblib.dump(model, file_)

    # Save model 
    client.fput_object('mpc', f'{timestamp}/model.joblib', 'model_file.joblib')

    # If included, save model metrics & more information
    if metrics:
        metrics['model_timestamp'] = timestamp
        metrics['model_type'] = model.__class__.__name__
        with open('model_metrics.json', 'w') as file_:
            json.dump(metrics, file_, indent=4)
        client.fput_object('mpc', f'{timestamp}/model_metrics.json', 'model_metrics.json')

    # Clean up local files
    os.remove('model_file.joblib')
    if metrics and os.path.exists('model_metrics.json'):
        os.remove('model_metrics.json')

    return timestamp


def minio_latest_model_timestamp_id() -> str:
    """
    Retrieves the latest timestamp ID stored in MinIO.

    :return: Most recent timestamp ID, or None if no models exist.
    :raises ConnectionError: If MinIO is not reachable.
    :raises IndexError: If no models are found in MinIO.
    """

    if not is_minio_online():
        raise ConnectionError('MinIO server is not reachable.')

    objects = list(client.list_objects('mpc', recursive=True))
    if not objects:
        raise IndexError('No models found in MinIO.')

    timestamps = set(obj.object_name.split('/')[0] for obj in objects)
    return sorted(timestamps)[-1]


def minio_retreive_model(model_timestamp: str | None = None) -> BaseEstimator:
    """
    Downloads a model from MinIO given its timestamp ID.

    :param model_timestamp: Timestamp ID of the model. If None, fetches the latest model.
    :return: The deserialized scikit-learn model.
    :raises ConnectionError: If MinIO is not reachable.
    :raises FileNotFoundError: If the specified model does not exist.
    """

    if not is_minio_online():
        raise ConnectionError('MinIO server is not reachable.')

    if model_timestamp is None:
        model_timestamp = minio_latest_model_timestamp_id()

    # Download model file
    try:
        client.fget_object('mpc', f'{model_timestamp}/model.joblib', 'model_file.joblib')
    except Exception as e:
        raise FileNotFoundError('There is no model with {model_timestamp} timestamp ID.')
    
    model = joblib.load('model_file.joblib')
    os.remove('model_file.joblib')

    return model


if __name__ == '__main__':
    print('Is minio Online?:', is_minio_online())
    lastest_model_id = minio_latest_model_timestamp_id()
    model = minio_retreive_model()
    print(lastest_model_id)
    print()
    print(model)