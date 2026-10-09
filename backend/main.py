from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.rotas.analise import roteador
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="MedCheck AI",
    description="API backend do MedCheck AI",
    version="0.1.0"
)

app.include_router(roteador)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

origens_permitidas = [
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return FileResponse("frontend/index.html")