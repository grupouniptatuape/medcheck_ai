from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="MedCheck AI",
    description="API backend do MedCheck AI",
    version="0.1.0"
)
// o que o sistema está recebendo: texto ou linkw
class EntradaAnalise(BaseModel):
    tipo_entrada: str
    conteudo: str



@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "MedCheck AI backend funcionando"
    }

// teste de recebimento
@app.post("/analisar")
def analisar(entrada: EntradaAnalise):
    return {
        "tipo_entrada": entrada.tipo_entrada,
        "conteudo": entrada.conteudo,
        "mensagem": "Conteúdo recebido com sucesso"
    }