import json

from google import genai


cliente = genai.Client()


def analisar_com_gemini(alegacao, evidencias):
    textos_evidencias = []

    for evidencia in evidencias:
        texto = f"""
Título: {evidencia.get("titulo", "")}
Autores: {evidencia.get("autores", "")}
Ano: {evidencia.get("ano", "")}
Revista: {evidencia.get("revista", "")}
Resumo: {evidencia.get("resumo", "")}
"""
        textos_evidencias.append(texto)

    evidencias_formatadas = "\n".join(textos_evidencias)

    prompt = f"""
Você é um sistema acadêmico de apoio à análise de evidências científicas em saúde.

Analise a alegação abaixo APENAS com base nas evidências fornecidas.

Alegação:
{alegacao}

Evidências:
{evidencias_formatadas}

Regras:
- Não invente estudos.
- Não use conhecimento externo às evidências fornecidas.
- Não faça diagnóstico médico.
- Diferencie ausência de evidência de evidência contrária.
- Use apenas uma destas classificações:
  - Sustentado pelas evidências
  - Contradito pelas evidências
  - Evidências inconclusivas
  - Evidências insuficientes

Retorne SOMENTE um JSON válido neste formato:

{{
  "classificacao": "uma das quatro classificações",
  "nivel_suporte": 0,
  "explicacao": "explicação curta e clara",
  "trechos_identificados": ["trecho 1", "trecho 2"]
}}
"""

    resposta = cliente.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    texto_resposta = resposta.text.strip()

    if texto_resposta.startswith("```"):
        texto_resposta = texto_resposta.replace("```json", "").replace("```", "").strip()

    return json.loads(texto_resposta)