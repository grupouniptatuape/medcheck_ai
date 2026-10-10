import ipaddress
import socket
from urllib.parse import urlparse, urlunparse
import ssl
from urllib3 import HTTPSConnectionPool, HTTPConnectionPool
import requests
from bs4 import BeautifulSoup
import certifi
from urllib3.exceptions import HTTPError

def validar_link(link):
    try:
        endereco = urlparse(link)

        if endereco.scheme != "https":
            raise ValueError("Por enquanto, são aceitos apenas links HTTPS.")

        if not endereco.hostname:
            raise ValueError(
                "O link informado não possui um domínio válido."
            )

        if endereco.username or endereco.password:
            raise ValueError(
                "Links com informações de autenticação não são permitidos."
            )

        porta = endereco.port

        if porta is not None:
            porta_permitida = 443 if endereco.scheme == "https" else 80

            if porta != porta_permitida:
                raise ValueError(
                    "O link utiliza uma porta não permitida."
                )

        return endereco

    except ValueError as erro:
        raise ValueError(f"Link inválido: {erro}") from erro

#Bloqueando endereços internos e privados
def verificar_ip_publico(endereco):
    dominio = endereco.hostname

    try:
        enderecos = socket.getaddrinfo(
            dominio,
            endereco.port or (443 if endereco.scheme == "https" else 80),
            type=socket.SOCK_STREAM
        )
    except socket.gaierror:
        raise ValueError("Não foi possível localizar o domínio informado.")

    if not enderecos:
        raise ValueError(
            "Não foi possível encontrar um endereço IP para o site informado."
        )
    
    ips_publicos = []
    for resultado in enderecos:
        ip = resultado[4][0]
        endereco_ip = ipaddress.ip_address(ip)

        if not endereco_ip.is_global:
            raise ValueError(
                "Não é permitido acessar endereços internos ou privados."
            )
        ips_publicos.append(ip)

    return list(dict.fromkeys(ips_publicos))

def extrair_texto_html(conteudo):
    pagina = BeautifulSoup(conteudo, "html.parser")

    for elemento in pagina([
        "script", "style", "nav", "footer",
        "header", "aside", "noscript"
    ]):
        elemento.decompose()

    artigo = pagina.find("article")

    if artigo:
        texto = artigo.get_text(separator=" ", strip=True)
    else:
        texto = pagina.get_text(separator=" ", strip=True)

    texto = " ".join(texto.split())

    if len(texto) < 100:
        raise ValueError(
            "Não foi possível extrair conteúdo suficiente da notícia."
        )

    return texto[:10000]

def acessar_pagina(link):
    endereco = validar_link(link)
    ips_publicos = verificar_ip_publico(endereco)

    limite_bytes = 2 * 1024 * 1024
    limite_redirecionamentos = 3


    caminho = urlunparse((
        "",
        "",
        endereco.path or "/",
        endereco.params,
        endereco.query,
        ""
    ))

    cabecalhos = {
        "Host": endereco.hostname,
        "User-Agent": "MedCheckAI/0.1",
        "Accept": "text/html",
        "Accept-Encoding": "identity"
    }

    if endereco.scheme == "https":
        conexao = HTTPSConnectionPool(
            host=ips_publicos[0],
            port=443,
            maxsize=1,
            block=True,
            timeout=5,
            cert_reqs="CERT_REQUIRED",
            ca_certs=certifi.where(),
            assert_hostname=endereco.hostname,
            server_hostname=endereco.hostname
        )

        resposta = None


        try:
            resposta = conexao.request(
                "GET",
                caminho,
                headers=cabecalhos,
                redirect=False,
                preload_content=False,
                retries=False
            )

            if resposta.status != 200:
                if resposta.status in (301, 302, 303, 307, 308):
                    raise ValueError(
                        "A página redirecionou para outro endereço. "
                        "O tratamento de redirecionamentos ainda não foi implementado."
                    )

                raise ValueError(
                    f"Não foi possível acessar a notícia. "
                    f"Código HTTP: {resposta.status}."
                )

            tipo_conteudo = resposta.headers.get("Content-Type", "").lower()

            if not tipo_conteudo.split(";")[0].strip() == "text/html":
                raise ValueError(
                    "O link não contém uma página HTML válida."
                )

            codificacao = resposta.headers.get(
                "Content-Encoding", "identity"
            ).lower()

            if codificacao != "identity":
                raise ValueError(
                    "A página utiliza uma codificação não suportada."
                )

            conteudo = resposta.read(limite_bytes + 1, decode_content=False)

            if len(conteudo) > limite_bytes:
                raise ValueError(
                    "A página ultrapassa o limite permitido de 2 MB."
                )

        except HTTPError as erro:
            raise ValueError(
                "Não foi possível acessar a notícia. "
                "Verifique se o site está disponível e tente novamente."
            ) from erro

        finally:
            if resposta is not None:
                resposta.release_conn()

            conexao.close()

    if endereco.scheme == "https":
        return extrair_texto_html(conteudo)


    # A conexão HTTP segura será implementada aqui.