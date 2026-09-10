import requests


URL_BUSCA = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


def buscar_artigos(termo, quantidade=5):
    parametros = {
        "db": "pubmed",
        "term": termo,
        "retmode": "json",
        "retmax": quantidade,
        "sort": "relevance"
    }

    resposta = requests.get(
        URL_BUSCA,
        params=parametros,
        timeout=10
    )

    resposta.raise_for_status()

    dados = resposta.json()

    return dados["esearchresult"]["idlist"]