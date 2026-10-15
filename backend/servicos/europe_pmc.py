
import requests


URL_BUSCA = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def pesquisar_europe_pmc(termo, quantidade=5):
    parametros = {
        "query": f"TITLE_ABS:({termo})",
        "sort": "RELEVANCE",
        "format": "json",
        "pageSize": quantidade,
        "resultType": "core"
    }

    try:
        resposta = requests.get(
            URL_BUSCA,
            params=parametros,
            timeout=15
        )

        resposta.raise_for_status()

        dados = resposta.json()
        resultados = dados.get("resultList", {}).get("result", [])

        artigos = []

        for resultado in resultados:
            pmid = resultado.get("pmid", "")
            pmcid = resultado.get("pmcid", "")
            doi = resultado.get("doi", "")

            if pmid:
                url = f"https://europepmc.org/article/MED/{pmid}"
            elif pmcid:
                url = f"https://europepmc.org/articles/{pmcid}"
            elif doi:
                url = f"https://doi.org/{doi}"
            else:
                continue

            artigos.append({
                "pmid": pmid,
                "titulo": resultado.get("title", ""),
                "autores": resultado.get("authorString", ""),
                "ano": str(resultado.get("pubYear", "")),
                "revista": resultado.get("journalTitle", ""),
                "resumo": resultado.get("abstractText", "") or "",
                "fonte": "Europe PMC",
                "url": url
            })

        return artigos

    except requests.exceptions.Timeout as erro:
        raise RuntimeError(
            "O Europe PMC demorou demais para responder."
        ) from erro

    except requests.exceptions.RequestException as erro:
        raise RuntimeError(
            "Não foi possível estabelecer comunicação com o Europe PMC."
        ) from erro
