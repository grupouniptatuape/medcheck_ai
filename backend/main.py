from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MedCheck AI",
    description="API backend do MedCheck AI",
    version="0.1.0"
)

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
# o que o sistema está recebendo: texto ou linkw
class EntradaAnalise(BaseModel):
    tipo_entrada: Literal["texto", "link"]
    conteudo: str

# para saída
class SaidaAnalise(BaseModel):
    alegacao_principal: str
    classificacao: str
    nivel_suporte: int
    explicacao: str
    trechos_identificados: list[str]
    evidencias: list[dict]
    aviso: str

@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "MedCheck AI backend funcionando"
    }

# teste de recebimento analisar
@app.post("/analisar", response_model=SaidaAnalise)
def analisar(entrada: EntradaAnalise):
    return {
        "alegacao_principal": entrada.conteudo,
        "classificacao": "Evidências inconclusivas",
        "nivel_suporte": 50,
        "explicacao": "Resposta simulada para teste de integração.",
        "trechos_identificados": [entrada.conteudo],
        "evidencias": [],
        "aviso": "O MedCheck AI possui finalidade informativa e educacional."
    }