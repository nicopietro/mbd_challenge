# Data service for the py_challenge
This project contains a small REST API that will provide the data required to implement the rest of the challenge.

This README is intentionally light on details on how to use the API or the data that is provided, but there should be enough information to complete the challenge by running the API and reading the documentation of the endpoints. Go look for it!

# How to run in Docker?

To build the image run:
```bash
$ docker build -t py_challenge_data_service:latest .
```

Then to run the API use:
```bash
$ docker run -d --name challenge_data_service \
-p 8777:8777 py_challenge_data_service:latest
```

You can then start using it from http://127.0.0.1:8777

# How to test its working?
You can send a request through [curl](https://curl.se/)
```bash
$ curl -X 'POST' \
  'http://localhost:8777/api/v1/animals/data' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "seed": 42,
  "number_of_datapoints": 500
}'
```