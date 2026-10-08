from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel
from backend.servicos.pubmed import pesquisar_pubmed
from backend.servicos.gemini import analisar_com_gemini, gerar_termos_busca

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
    print("1. Requisição recebida", flush=True)

    try:
        print("2. Gerando termos de busca...", flush=True)
        termos_busca = gerar_termos_busca(entrada.conteudo)
        print("3. Termos gerados com sucesso", flush=True)

        print("4. Consultando PubMed...", flush=True)
        evidencias = pesquisar_pubmed(termos_busca)
        print(f"5. PubMed retornou {len(evidencias)} artigos", flush=True)

        print("6. Solicitando análise ao Gemini...", flush=True)
        resultado_ia = analisar_com_gemini(
            entrada.conteudo,
            evidencias
        )
        print("7. Análise recebida do Gemini", flush=True)

        resultado = {
            "alegacao_principal": entrada.conteudo,
            "classificacao": resultado_ia["classificacao"],
            "nivel_suporte": resultado_ia["nivel_suporte"],
            "explicacao": resultado_ia["explicacao"],
            "trechos_identificados": resultado_ia["trechos_identificados"],
            "evidencias": evidencias,
            "aviso": "O MedCheck AI possui finalidade informativa e educacional."
        }

        print("8. Resultado preparado para retorno", flush=True)
        return resultado

    except Exception as erro:
        print(
            f"ERRO NA ANÁLISE: {type(erro).__name__}: {erro}",
            flush=True
        )
        raise
