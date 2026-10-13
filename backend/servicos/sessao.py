
import os
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Request, Response
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


load_dotenv()

NOME_COOKIE = "medcheck_sessao"
DURACAO_SESSAO = 60 * 60 * 24 * 30

chave_secreta = os.getenv("SESSION_SECRET_KEY")

if not chave_secreta:
    raise RuntimeError("SESSION_SECRET_KEY não configurada.")

assinador = URLSafeTimedSerializer(chave_secreta, salt="medcheck-sessao")


def obter_sessao(request: Request, response: Response):
    cookie = request.cookies.get(NOME_COOKIE)

    if cookie:
        try:
            return assinador.loads(
                cookie,
                max_age=DURACAO_SESSAO
            )
        except (BadSignature, SignatureExpired):
            pass

    identificador = str(uuid4())
    cookie_assinado = assinador.dumps(identificador)

    response.set_cookie(
        key=NOME_COOKIE,
        value=cookie_assinado,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=DURACAO_SESSAO,
        path="/"
    )

    return identificador
