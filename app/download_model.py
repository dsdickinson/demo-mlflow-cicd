import os
import mlflow

MODEL_NAME = "demo-mlflow-cicd"
MODEL_STAGE = "Production"

tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5002")
mlflow.set_tracking_uri(tracking_uri)

model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"

print(f"Downloading model from: {model_uri}")

local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)

print(f"Model downloaded to: {local_path}")

# Move to consistent directory for Docker
import shutil

if os.path.exists("model"):
    shutil.rmtree("model")

shutil.copytree(local_path, "model")

print("Model ready in ./model")
