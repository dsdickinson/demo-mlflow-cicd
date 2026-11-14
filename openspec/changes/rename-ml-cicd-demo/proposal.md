## Why

The project is now named `demo-mlflow-cicd`, but its training, serving, deployment, and documentation still use `ml-cicd-demo`. Using one name across the application avoids confusion when registering and downloading models or publishing and deploying the container image.

## What Changes

- **BREAKING**: Use `demo-mlflow-cicd` as the MLflow experiment and registered model name for new training runs and Production model downloads.
- Update repository documentation, ignore rules, Kubernetes image configuration, and checked-in model metadata to use the new project name.
- Keep historical MLflow run records intact; they describe past runs under the old name.

## Capabilities

### New Capabilities
- `project-naming`: Consistent project identity across training, model serving, container publishing, deployment configuration, and documentation.

### Modified Capabilities

## Impact

- `app/train.py` and `app/download_model.py` model and experiment identifiers.
- `README.md`, `.gitignore`, `k8s/deployment.yaml`, and checked-in model metadata under `model/` and `app/model/`.
- MLflow model registration and local model artifact lookup. Existing model registry entries named `ml-cicd-demo` remain historical; new runs use `demo-mlflow-cicd`.
- The image path in the Kubernetes manifest will use the repository's new name, `ghcr.io/dsdickinson/demo-mlflow-cicd/ml-api:latest`.
