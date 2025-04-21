# User Interface

This module provides a simple, modular **Streamlit web interface** for interacting with the machine learning API. It is designed for exploratory use and ease of interaction with prediction and training features.

The preferred method for deployment is the `docker-compose` file present in the root directory.

This auxiliary README is kept in case this Docker container is run separately from the full compose stack.

# How to run in Docker?

## ML Service API
### To create the docker image for ml service run:
```bash
docker build -t challenge_user_interface:latest .
```
### To launch

Make sure the `ml-service` container is already running.

Then run:
```bash
docker run -d \
  --name user_interface \
  -p 8501:8501 \
  --env ML_API_HOST=http://host.docker.internal:8000 \
  challenge_user_interface:latest
```
