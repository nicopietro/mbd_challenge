# MBD_challenge
Master’s in Big Data – Laboratory Challenge

## Description

This project creates, deploys and manages a ML model to infer if an animal belongs to any of these 4 possible types: Kangaroo, Elephant, Chicken, and Dog.

The architecture is composed of modular microservices built using FastAPI. It also includes a PostgreSQL database to store data sent by users, MinIO for object storage, and is fully orchestrated using Docker Compose.

## Quick Start

### 1. Prerequisites

- Ensure [Docker](https://www.docker.com/) is installed and the Docker daemon is running.

### 2. Build and Start the System

From the project root, run the following command to build and start all services:

```bash
docker compose up --build
```

## Services Overview

### `data-service`
- Generates synthetic animal data for training.
- REST API accessible at: `http://localhost:8777`

### `ml-service`
- Exposes a REST API to train machine learning models and perform predictions.
- Handles inference logic, model lifecycle management, and integrates with MinIO for model storage.
- REST API accessible at: `http://localhost:8000`

### `minio`
- Acts as an object storage backend for saving trained models.
- Console UI: `http://localhost:9001`
- API: `http://localhost:9000`
- Default credentials:
  - Username: `minioadmin`
  - Password: `minioadmin`

### `postgres`
- Stores user-generated and model-related data in a PostgreSQL database.
- Exposed on port `5432`.
- Default credentials:
  - Username: `postgres`
  - Password: `postgres`
  - Database: `challenge_db`
