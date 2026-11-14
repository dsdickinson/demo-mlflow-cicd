## 1. Update active project identity

- [x] 1.1 Change the MLflow experiment and registered model names in `app/train.py` to `demo-mlflow-cicd`.
- [x] 1.2 Change the registered model name in `app/download_model.py` to `demo-mlflow-cicd`.
- [x] 1.3 Update the Kubernetes GHCR image path and `.gitignore` entry to use `demo-mlflow-cicd`.
- [x] 1.4 Update README references to the old project, model, and image names.

## 2. Align checked-in model metadata and verify

- [x] 2.1 Update name-bearing metadata in `model/` and `app/model/` while preserving artifact IDs, run IDs, and model payloads.
- [x] 2.2 Confirm maintained application/configuration files have no old-name references, historical MLflow records remain untouched, and the complete diff has no unintended changes.
