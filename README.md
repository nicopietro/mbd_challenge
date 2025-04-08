# MBD_challenge
Master’s in Big Data – Laboratory Challenge

# Description

This project creates, deploys and manages a ML model to infer if an animal belong to any of these 4 possible types: Kangaroo, Elephant, Chicken, and Dog.

# Quick Start

TODO

# Structure

This project is divided in 5 different components:

1. Data service: An external data service is deployed locally to retreive animal data.
2. Data processing: Exploratory Data Analysis (EDA) is performed. All data manipulation and cleaning is done and a ML model is created and stored to be used later.
3. Backend: API is configured to communicate ML model with frontend.
4. Frontend: GUI is configured for the user to interact with the app.
5. Containerization: A set of Dockers are created to easily deploy the project on other enviroments.

# Docker commands

## Minio

### bash
```bash
 docker run -d \
  --name challenge_minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v "/$(pwd):/data" \
  quay.io/minio/minio server /data --console-address ":9001"
```

There's a known error in bash when it in on Windows. In that case the following powershell command is fully functional on windows.

### Powershell
```powershell
docker run -d `
  --name challenge_minio `
  -p 9000:9000 `
  -p 9001:9001 `
  -e MINIO_ROOT_USER=minioadmin `
  -e MINIO_ROOT_PASSWORD=minioadmin `
  -v "${PWD}\data\models:/data" `
  quay.io/minio/minio server /data --console-address ":9001"
```