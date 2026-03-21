from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from app.predict import predict
from fastapi import Request

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

class InputData(BaseModel):
    features: list

@app.post("/predict")
#async def run_prediction(request: Request):
#    body = await request.json()
#    print("RAW BODY:", body)
#    return {"received": body}
def run_prediction(input_data: InputData):
    data = np.array(input_data.features).reshape(1, -1)
    print(type(data))
    print(input_data)
    result = predict(data)
    return {"prediction": result.tolist()}
    #return result.tolist()
