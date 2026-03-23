import mlflow.pyfunc

model = None

def get_model():
    global model
    if model is None:
        model = mlflow.pyfunc.load_model("model")
    return model

def predict(data):
    model = get_model()
    return model.predict(data)
