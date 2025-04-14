# ML Service

This auxiliar readme is kept if each docker container wants to be run separately from the docker-compose file

### To create the docker image for ml service run:
```bash
docker build -t ml-service .
```
### To launch
```bash
docker run -d -p 8000:8000 --name challenge_ml_service ml-service
```
# Minio

### Bash command to create the minio container
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