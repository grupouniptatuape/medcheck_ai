from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel


roteador = APIRouter()


class EntradaAnalise(BaseModel):
    tipo_entrada: Literal["texto", "link"]
    conteudo: str


class SaidaAnalise(BaseModel):
    alegacao_principal: str
    classificacao: str
    nivel_suporte: int
    explicacao: str
    trechos_identificados: list[str]
    evidencias: list[dict]
    aviso: str


@roteador.post("/analisar", response_model=SaidaAnalise)
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