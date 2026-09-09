from fastapi import FastAPI

app = FastAPI(
    title="MedCheck AI",
    description="API backend do MedCheck AI",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "MedCheck AI backend funcionando"
    }