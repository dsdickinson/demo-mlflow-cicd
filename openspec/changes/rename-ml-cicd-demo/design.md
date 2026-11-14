## Context

The repository uses `ml-cicd-demo` as its MLflow experiment and registered model name, and in the GHCR image path, README, ignore rule, and checked-in model metadata. The workflow trains into a fresh file store, registers a Production model, downloads it into `model/`, and packages it with the API. Existing local MLflow tracking data includes historical runs and model versions under the old name.

## Goals / Non-Goals

**Goals:**
- Make `demo-mlflow-cicd` the consistent name in active application code and repository configuration.
- Ensure training and model download refer to the same new MLflow experiment and registered model.
- Make the checked-in model package and Kubernetes manifest consistent with the new name.

**Non-Goals:**
- Rewrite or migrate historical MLflow run records in `mlruns/` or the local database.
- Change the classifier, API contract, image tag, or deployment workflow behavior.
- Rename the repository itself or alter external GHCR packages.

## Decisions

- Update maintained source, deployment configuration, docs, ignore rules, and checked-in model metadata. This keeps the runnable project aligned without rewriting append-only tracking history.
- Use `demo-mlflow-cicd` for both the MLflow experiment and registered model name. This matches the established project identity and keeps the training and download scripts aligned.
- Update the Kubernetes image path to `ghcr.io/dsdickinson/demo-mlflow-cicd/ml-api:latest`, matching the repository name reflected by this workspace. Keep the `ml-api:latest` image name and tag unchanged.
- Leave old names found only in MLflow history untouched. Those entries represent prior runs and remain valid historical records; new pipeline runs use the new registered model name.

## Risks / Trade-offs

- [Existing users may expect the old MLflow registry entry] → Existing history stays in place, but future training creates/uses the new model name; document the switch.
- [The owner or repository path may differ in another fork] → The manifest uses the repository identity currently present in the project; forks must adjust their image path.
- [Checked-in MLflow metadata contains machine-specific artifact paths] → Change only name-bearing metadata needed for consistency; avoid broad replacement of unrelated paths or identifiers.

## Migration Plan

1. Update source and repository configuration references to the new name.
2. Update checked-in model identity metadata, leaving artifact IDs, run IDs, and historical `mlruns/` contents unchanged.
3. Verify maintained files no longer use the old project/model name, confirm historical tracking files are unchanged, and inspect the diff.

Rollback consists of reverting the source/configuration and metadata changes. New MLflow runs created after the rename remain under the new model name and are not merged into the old registry history.

## Open Questions

None.
