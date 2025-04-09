from fastapi import FastAPI
import uvicorn
from model_manager import ModelManager

app = FastAPI()
model = ModelManager()

@app.post("/recognize")
def recognize():
    return {"model_id": id(model)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)