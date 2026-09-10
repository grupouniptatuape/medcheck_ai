import requests
import xml.etree.ElementTree as ET


URL_BUSCA = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
URL_DETALHES = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


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

def buscar_detalhes(pmids):
    parametros = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    resposta = requests.get(
        URL_DETALHES,
        params=parametros,
        timeout=10
    )

    resposta.raise_for_status()

    raiz = ET.fromstring(resposta.text)

    artigos = []

    for artigo_xml in raiz.findall(".//PubmedArticle"):
        pmid = artigo_xml.findtext(".//PMID", default="")

        titulo_elemento = artigo_xml.find(".//ArticleTitle")
        titulo = "".join(titulo_elemento.itertext()) if titulo_elemento is not None else ""

        autores_lista = []
        for autor in artigo_xml.findall(".//Author"):
            sobrenome = autor.findtext("LastName", default="")
            iniciais = autor.findtext("Initials", default="")

            nome = f"{sobrenome} {iniciais}".strip()

            if nome:
                autores_lista.append(nome)

        autores = ", ".join(autores_lista)

        revista = artigo_xml.findtext(".//Journal/Title", default="")

        ano = artigo_xml.findtext(".//PubDate/Year", default="")

        if not ano:
            data_medline = artigo_xml.findtext(".//PubDate/MedlineDate", default="")
            ano = data_medline[:4] if data_medline else ""

        resumo_partes = []

        for parte in artigo_xml.findall(".//Abstract/AbstractText"):
            texto = "".join(parte.itertext()).strip()

            if texto:
                resumo_partes.append(texto)

        resumo = " ".join(resumo_partes)

        artigos.append({
            "pmid": pmid,
            "titulo": titulo,
            "autores": autores,
            "ano": ano,
            "revista": revista,
            "resumo": resumo,
            "fonte": "PubMed",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        })

    return artigos