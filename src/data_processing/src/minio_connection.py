from datetime import datetime
import json
import os
from minio import Minio
import joblib
from sklearn.base import BaseEstimator

client = Minio(
    'localhost:9000',
    access_key='minioadmin',
    secret_key='minioadmin',
    secure=False
)

def minio_save_model(model: BaseEstimator, metrics: dict | None) -> None:
    # TODO: Add documentation

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
        metrics["model_timestamp"] = timestamp
        metrics["model_type"] = model.__class__.__name__
        with open('model_metrics.json', 'w') as file_:
            json.dump(metrics, file_, indent=4)
        client.fput_object('mpc', f'{timestamp}/model_metrics.json', 'model_metrics.json')

    # Clean up local files
    os.remove('model_file.joblib')
    if metrics and os.path.exists('model_metrics.json'):
        os.remove('model_metrics.json')


def minio_latest_model_id() -> str | None:
    # TODO: Add documentation
    objects = client.list_objects('mpc', recursive=True)
    timestamps = set(obj.object_name.split('/')[0] for obj in objects)
    return sorted(timestamps)[-1]


def minio_retreive_model(model_timestamp: str | None) -> BaseEstimator:
    # TODO: Add documentation

    if model_timestamp is None:
        model_timestamp = minio_latest_model_id()

    # Download model file
    client.fget_object('mpc', f'{model_timestamp}/model.joblib', 'model_file.joblib')
    model = joblib.load('model_file.joblib')
    os.remove('model_file.joblib')

    return model


if __name__ == "__main__":
    lastest_model_id = minio_latest_model_id()
    model = minio_retreive_model()
    print(lastest_model_id)
    print()
    print(model)