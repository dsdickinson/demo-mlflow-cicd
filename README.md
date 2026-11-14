# MLflow Iris Classification CI/CD Demo

This repository demonstrates a small machine learning workflow: train an Iris classifier, track and register it with MLflow, promote the best model to Production, package it behind a FastAPI endpoint, and build a container image for Kubernetes.

## How the pieces fit together

```text
Push to main
   │
   ▼
GitHub Actions installs dependencies and trains an Iris Random Forest
   │
   ├── MLflow records the run, accuracy, parameter, and registered model
   ├── The new model is promoted when it beats Production accuracy
   ▼
Download the Production model into ./model
   │
   ▼
Build and push ghcr.io/<owner>/<repo>/ml-api:latest
   │
   ▼
FastAPI serves health and prediction endpoints on port 8000
   │
   ▼
Kubernetes runs two API replicas behind a LoadBalancer Service
```

The training data is scikit-learn's built-in Iris dataset. `app/train.py` fits a `RandomForestClassifier` with 100 trees and logs its test accuracy and `n_estimators` value to MLflow. The experiment and registered model are named `demo-mlflow-cicd`. The first trained model is promoted to Production; later versions are promoted only when their measured accuracy is higher than the current Production version.

## Requirements

- Python 3.10
- Docker, if building the container locally
- A Kubernetes cluster and `kubectl`, if deploying to Kubernetes
- A GitHub repository with GitHub Actions and GitHub Container Registry (GHCR) access, for the CI image publishing workflow

## Run locally

Create and activate a virtual environment, then install the pinned project dependencies:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Train and register a model:

```bash
python app/train.py
```

By default, MLflow uses the local `./mlruns` file store. To use another tracking store, set `MLFLOW_TRACKING_URI` before running the script. The training script creates the `demo-mlflow-cicd` experiment each time, so use a fresh tracking store when starting a new local run unless that experiment-creation behavior has been adjusted.

### Prepare the model for serving

The API loads an MLflow model from the repository's `model/` directory. To replace that directory with the Production model from the local file store, run:

```bash
MLFLOW_TRACKING_URI=file:./mlruns python app/download_model.py
```

`app/download_model.py` defaults to `http://127.0.0.1:5002` when `MLFLOW_TRACKING_URI` is not set. The GitHub Actions workflow explicitly sets the file-store URI for this step.

### Start the API

With a valid model in `model/`, start the server:

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

Check the health endpoint:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{"status":"ok"}
```

OpenAPI docs are available at `http://127.0.0.1:8000/docs`. The server binds to `0.0.0.0`, but clients should connect to `127.0.0.1` or `localhost` on the same computer.

If the request hangs and Uvicorn does not log a `GET /`, another service may already be publishing port 8000. On macOS, check which processes are listening:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

If Docker and Uvicorn both appear, stop the container publishing port 8000 or run the local API on another port:

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8001
curl http://127.0.0.1:8001/
```

Send one Iris sample to the prediction endpoint. The four features are sepal length, sepal width, petal length, and petal width, in centimeters:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

The response contains the predicted class index in a `prediction` array; the Iris class indices are 0, 1, and 2.

## Build and run the container

The Docker image includes the API code and `model/` directory. Build and run it from the repository root:

```bash
docker build -t ml-api:local .
docker run --rm -p 8000:8000 ml-api:local
```

Then use the same `/` and `/predict` requests shown above.

## CI/CD workflow

`.github/workflows/ml-ci-cd.yaml` runs on pushes to `main`. It checks out the repository, installs dependencies with Python 3.10, removes the runner's existing `mlruns` directory, trains and registers a model, downloads the Production model, logs in to GHCR with `GITHUB_TOKEN`, and builds and pushes:

```text
ghcr.io/<owner>/<repository>/ml-api:latest
```

The workflow builds and publishes the image. It does not deploy the Kubernetes manifests or update a running cluster.

## Deploy to Kubernetes

The manifests in `k8s/` create a Deployment with two replicas and a `LoadBalancer` Service that forwards port 80 to container port 8000. The Deployment references `ghcr.io/dsdickinson/demo-mlflow-cicd/ml-api:latest` and expects an image pull secret named `gh-regcred`.

For a private GHCR package, create the pull secret using a GitHub username and a personal access token with package read access:

```bash
kubectl create secret docker-registry gh-regcred \
  --docker-server=ghcr.io \
  --docker-username=<github-username> \
  --docker-password=<github-token>
```

Apply the resources:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get service ml-api-service
```

When the LoadBalancer has an external address, send the health and prediction requests to that address (port 80). If your GHCR image path differs from the one in the manifest, update the Deployment image before applying it. `k8s/secret.yaml` contains the `kubectl create secret` command as a template; it is not a Kubernetes Secret YAML manifest.

## Repository map

| Path | Purpose |
| --- | --- |
| `app/train.py` | Train, log, register, and conditionally promote the Iris classifier |
| `app/download_model.py` | Download the Production model into `./model` |
| `app/api.py` | FastAPI health and prediction endpoints |
| `app/predict.py` | Lazily load the local MLflow model and run predictions |
| `model/` | Model artifact used by the API and Docker image |
| `Dockerfile` | Package the API and model into a container |
| `.github/workflows/ml-ci-cd.yaml` | Train the model and publish the image to GHCR on pushes to `main` |
| `k8s/` | Kubernetes Deployment, Service, and registry-secret command template |
| `requirements.txt` | Python dependencies for training and serving |

## Notes

- `mlruns/` and `mlflow.db` are local MLflow tracking data; the GitHub workflow creates fresh tracking data for each run.
- The checked-in model artifact records its own MLflow and scikit-learn environment versions. Those may differ from the top-level `requirements.txt`, which pins the application's training and serving dependencies.
- Model promotion compares accuracy from a single `train_test_split` without an explicit random seed, so the measured score can vary between training runs.
