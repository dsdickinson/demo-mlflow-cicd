## ADDED Requirements

### Requirement: Use the repository name for active project and model identity
The application and maintained repository configuration SHALL use `demo-mlflow-cicd` in place of `ml-cicd-demo` for the MLflow experiment name, registered model name, documentation, ignore rules, deployment image path, and checked-in model identity metadata.

#### Scenario: Train and retrieve the model under one identity
- **WHEN** a user runs the training and model download scripts for a new run
- **THEN** both scripts refer to the `demo-mlflow-cicd` MLflow model, and training uses the `demo-mlflow-cicd` experiment

#### Scenario: Build and deploy the project image
- **WHEN** the documented CI image is deployed using the Kubernetes manifest
- **THEN** the documentation and manifest identify the image repository as `ghcr.io/dsdickinson/demo-mlflow-cicd/ml-api`

### Requirement: Preserve historical MLflow tracking records
The rename SHALL NOT rewrite historical MLflow run records, version records, or tracking database contents that refer to `ml-cicd-demo`.

#### Scenario: Inspect existing tracking history after the rename
- **WHEN** a user inspects MLflow tracking data created before the rename
- **THEN** historical records retain their original names and identifiers
