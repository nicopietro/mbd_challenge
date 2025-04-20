# ML Service

This module provides a simple, modular API for serving machine learning predictions using FastAPI. It's structured for production-readiness, supports containerization via Docker, and is organized as a Python package.

The preferred method for the deployment is the ```docker-compose``` file present in the root directory.

This auxiliar readme is kept if each docker container wants to be run separately from the docker-compose file

# How to run in Docker?

## ML Service API
### To create the docker image for ml service run:
```bash
docker build -t ml-service .
```
### To launch
```bash
docker run -d \
  --name challenge_ml_service ml-service \
  -p 8000:8000 \
  -e MINIO_HOST=host.docker.internal:9000 \
  -e DATA_SERVICE_API_HOST=http://host.docker.internal:8777 \
  
```

## Posgres

```bash
docker run -d \
  --name postgre_db \
  -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=challenge_db \
  -v "/$(pwd)/data/user_generated_data:/var/lib/postgresql/data" \
  postgres:latest
```

## Minio
### Bash command to create the minio container
```bash
 docker run -d \
  --name challenge_minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v "/$(pwd)/data/models:/data" \
  quay.io/minio/minio server /data --console-address ":9001"
```

There's a known error in bash when it in on Windows. In that case the following powershell command is fully functional on windows.

### Powershell command to create the minio container
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