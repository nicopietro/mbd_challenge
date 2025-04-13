import socket
import requests

def is_data_service_online() -> bool:
    """
    Checks if the data service server is reachable.

    :return: True if Data Service is reachable, False otherwise.
    """

    try:
        with socket.create_connection(('data-service', '8777'), timeout=5.0):
            return True
    except OSError:
        return False

def fetch_animals(datapoints: int, seed: int=42) -> tuple[dict, int]:
    """
    Fetches a list of animal datapoints from the data service API.

    :param datapoints: Number of datapoints to fetch (must be > 0).
    :param seed: Seed for random generation (default is 42).
    :return: Tuple containing the response JSON and HTTP status code.
    :raises ValueError: If datapoints is less than or equal to 0.
    :raises ConnectionError: If the data service is not reachable.
    """

    if not is_data_service_online():
        raise ConnectionError("Data Service server is not reachable.")

    if datapoints <= 0:
        raise ValueError("Number of datapoints must be greater than zero.")

    payload = {
        "seed": seed,
        "number_of_datapoints": datapoints
        }

    response = requests.post('http://data-service:8777/api/v1/animals/data', json=payload)
    response.raise_for_status()
    return response.json(), response.status_code


def fetch_schema() -> tuple[dict, int]:
    """
    Fetches the schema for the animal dataset from the data service API.

    :return: Tuple containing the schema JSON and HTTP status code.
    :raises ConnectionError: If the data service is not reachable.
    """

    if not is_data_service_online():
        raise ConnectionError("Data Service server is not reachable.")

    response = requests.get('http://data-service:8777/api/v1/animals/schema')
    response.raise_for_status()
    return response.json(), response.status_code


if __name__ == "__main__":
    print('Is data service Online?:', is_data_service_online())
    data = fetch_animals(10)
    schema = fetch_schema()
    print(data)
    print()
    print(schema)