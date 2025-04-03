import requests

def fetch_animals(datapoints: int, seed: int=42) -> tuple[dict, int]:
    """
    Fetch a list of animal datapoints from the API.

    :param datapoints: Number of datapoints to fetch (must be > 0).
    :param seed: Seed for random generation (default is 42).
    :return: Tuple with response JSON and HTTP status code.
    :raises ValueError: If datapoints is less than or equal to 0.
    """

    if datapoints <= 0:
        raise ValueError("Number of datapoints must be greater than zero.")

    payload = {
        "seed": seed,
        "number_of_datapoints": datapoints
        }

    try:
        response = requests.post('http://localhost:8777/api/v1/animals/data', json=payload)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}, 500

def fetch_schema() -> tuple[dict, int]:
    """
    Fetch the schema for the animal dataset from the API.

    :return: Tuple with schema JSON and HTTP status code.
    """

    try:
        response = requests.get('http://localhost:8777/api/v1/animals/schema')
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}, 500

if __name__ == "__main__":
    data = fetch_animals(10)
    schema = fetch_schema()
    print(data)
    print()
    print(schema)