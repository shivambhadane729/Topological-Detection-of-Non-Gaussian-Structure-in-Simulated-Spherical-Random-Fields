from fastapi import FastAPI
from routers import upload, preprocess, compute, results

app = FastAPI(title="CosmoPH Backend")

app.include_router(upload.router)
app.include_router(preprocess.router)
app.include_router(compute.router)
app.include_router(results.router)

@app.get("/")
def home():
    return {"message": "CosmoPH backend running"}