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
    with open('model_file.joblib', mode='wb') as file_:
        joblib.dump(model, file_)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    if not client.bucket_exists('mpc'):
        client.make_bucket('mpc')

    # Save model 
    client.fput_object('mpc', f'{timestamp}/model.joblib', 'model_file.joblib')

    # If included, save model metrics
    if metrics:
        with open('model_metrics.json', 'w') as file_:
            json.dump(metrics, file_, indent=4)
        client.fput_object('mpc', f'{timestamp}/model_metrics.json', 'model_metrics.json')

    # Clean up local files
    os.remove('model_file.joblib')
    if metrics and os.path.exists('model_metrics.json'):
        os.remove('model_metrics.json')