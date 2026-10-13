from typing import Literal
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from backend.servicos.pubmed import pesquisar_pubmed
from backend.servicos.gemini import (
    analisar_com_gemini,
    gerar_termos_busca,
    identificar_alegacao
)
from backend.servicos.extrator_link import acessar_pagina
from backend.banco.persistencia import salvar_analise
from backend.servicos.sessao import obter_sessao
from backend.banco.consultas import buscar_historico, buscar_analise


roteador = APIRouter()


class EntradaAnalise(BaseModel):
    tipo_entrada: Literal["texto", "link"]
    conteudo: str = Field(min_length=1, max_length=5000)
    
    @field_validator("conteudo")
    @classmethod
    def validar_conteudo(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("O conteúdo da análise não pode estar vazio.")

        return valor

class SaidaAnalise(BaseModel):
    alegacao_principal: str
    classificacao: str
    nivel_suporte: int
    explicacao: str
    trechos_identificados: list[str]
    evidencias: list[dict]
    aviso: str



@roteador.post("/analisar", response_model=SaidaAnalise)
def analisar(entrada: EntradaAnalise, 
             request: Request, 
             response: Response):
    print("1. Requisição recebida", flush=True)

    identificador_sessao = obter_sessao(request, response)
    try:
        if entrada.tipo_entrada == "link":
            print("Extraindo conteúdo do link...", flush=True)

            try:
                conteudo_analise = acessar_pagina(entrada.conteudo)
            except ValueError as erro:
                raise HTTPException(
                    status_code=422,
                    detail=str(erro)
                ) from erro
        else:
            conteudo_analise = entrada.conteudo

        print("2. Identificando alegação científica...", flush=True)

        identificacao = identificar_alegacao(conteudo_analise)

        if not identificacao["possui_alegacao"] or not identificacao["alegacao_principal"].strip():
            raise HTTPException(
                status_code=422,
                detail="Não foi identificada uma alegação científica de saúde neste conteúdo."
            )

        alegacao_identificada = identificacao["alegacao_principal"]

        print("3. Gerando termos de busca...", flush=True)
        termos_busca = gerar_termos_busca(alegacao_identificada)
        
        print(f"[PUBMED] Alegação: {alegacao_identificada}", flush=True)
        print(f"[PUBMED] Termos de busca: {termos_busca}", flush=True)

        print("3. Termos gerados com sucesso", flush=True)

        print("4. Consultando PubMed...", flush=True)
        evidencias = pesquisar_pubmed(termos_busca)
        print(f"5. PubMed retornou {len(evidencias)} artigos", flush=True)

        print("6. Solicitando análise ao Gemini...", flush=True)
        resultado_ia = analisar_com_gemini(
            alegacao_identificada,
            evidencias
        )
        print("7. Análise recebida do Gemini", flush=True)

        resultado = {
            "alegacao_principal": alegacao_identificada,
            "classificacao": resultado_ia["classificacao"],
            "nivel_suporte": resultado_ia["nivel_suporte"],
            "explicacao": resultado_ia["explicacao"],
            "trechos_identificados": resultado_ia["trechos_identificados"],
            "evidencias": evidencias,
            "aviso": "O MedCheck AI possui finalidade informativa e educacional."
        }

        print("8. Resultado preparado para retorno", flush=True)

        print("9. Salvando análise no MySQL...", flush=True)

        id_analise = salvar_analise(
            tipo_entrada=entrada.tipo_entrada,
            conteudo_original=entrada.conteudo,
            resultado=resultado,
            identificador_visitante=identificador_sessao
        )

        print(f"10. Análise salva com ID {id_analise}", flush=True)

        return resultado



    except RuntimeError as erro:
        print(f"ERRO DE SERVIÇO: {erro}", flush=True)

        raise HTTPException(
            status_code=503,
            detail=str(erro)
        ) from erro

    except HTTPException:
        raise

    except Exception as erro:
        print(
            f"ERRO NA ANÁLISE: {type(erro).__name__}: {erro}",
            flush=True
        )
        raise




@roteador.get("/historico")
def listar_historico(request: Request, response: Response):
    identificador = obter_sessao(request, response)

    analises = buscar_historico(identificador)

    return {
        "total": len(analises),
        "analises": analises
    }


@roteador.get("/historico/{id_analise}")
def detalhar_historico(
    id_analise: int,
    request: Request,
    response: Response
):
    identificador = obter_sessao(request, response)

    analise = buscar_analise(
        id_analise,
        identificador
    )

    if analise is None:
        raise HTTPException(
            status_code=404,
            detail="Análise não encontrada."
        )

    return analise



@roteador.delete("/historico/{id_analise}")
def remover_historico(
    id_analise: int,
    request: Request,
    response: Response
):
    identificador = obter_sessao(request, response)

    excluiu = excluir_analise(
        id_analise,
        identificador
    )

    if not excluiu:
        raise HTTPException(
            status_code=404,
            detail="Análise não encontrada."
        )

    return {
        "mensagem": "Análise excluída com sucesso."
    }
