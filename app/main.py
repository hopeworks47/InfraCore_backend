from fastapi import FastAPI

app = FastAPI(title="InfraCore API")

@app.get("/")
def root():
    return {"message": "InfraCore API is running"}