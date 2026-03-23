import os
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

mlflow.set_tracking_uri(
    os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5002")
) # match your MLflow UI port

mlflow.set_experiment("ml-cicd-demo")

promoted = False
MODEL_NAME = "ml-cicd-demo"

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Train the model
with mlflow.start_run() as run:
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", acc)

    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name=MODEL_NAME
    )

    print(f"Model accuracy: {acc}")


client = MlflowClient()

# Get latest version
latest_versions = client.get_latest_versions(MODEL_NAME, stages=["None"])
latest_version = latest_versions[0].version
print(latest_version)

# Get current production model
prod_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])

if prod_versions:
    prod_version = prod_versions[0]
    print(prod_version)
    prod_run = client.get_run(prod_version.run_id)
    prod_acc = prod_run.data.metrics["accuracy"]

    if acc > prod_acc:
        print("New model is better. Promoting...")
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=latest_version,
            stage="Production"
        )
        promoted = True
    else:
        print("New model is worse. Skipping promotion.")
else:
    print("No production model found. Promoting first model.")
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=latest_version,
        stage="Production"
    )
    promoted = True

if promoted:
    print(f"Promoted version {latest_version} to Production")
