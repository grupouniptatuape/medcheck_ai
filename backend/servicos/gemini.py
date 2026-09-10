import json

from google import genai
import time

from google.genai.errors import ServerError

cliente = genai.Client()

def gerar_termos_busca(alegacao):
    prompt = f"""
Transforme a alegação abaixo em uma consulta curta e objetiva para pesquisa
de artigos científicos no PubMed.

Alegação:
{alegacao}

Regras:
- Retorne somente os termos de busca.
- Use inglês.
- Preserve os principais conceitos científicos da alegação.
- Não explique a resposta.
- Não acrescente informações que não estejam presentes na alegação.
- Não use aspas.
- Não use frases completas desnecessariamente.

Exemplo:
Alegação: A vitamina C previne o resfriado comum.
Resposta: vitamin C common cold prevention

Agora gere a consulta para a alegação fornecida.
"""

    resposta = cliente.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return resposta.text.strip()


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

Sua tarefa é comparar a ALEGAÇÃO DO USUÁRIO com as EVIDÊNCIAS CIENTÍFICAS fornecidas.

ALEGAÇÃO DO USUÁRIO:
{alegacao}

EVIDÊNCIAS CIENTÍFICAS:
{evidencias_formatadas}

REGRAS:
- Analise apenas com base nas evidências científicas fornecidas.
- Não invente estudos, resultados, autores ou informações.
- Não utilize conhecimento externo às evidências fornecidas.
- Não faça diagnóstico médico nem prescreva tratamentos.
- Diferencie ausência de evidência de evidência contrária.
- Considere possíveis diferenças entre população geral e grupos específicos.
- Caso as evidências sejam insuficientes para avaliar a alegação, indique isso claramente.

CLASSIFICAÇÃO:
Use exatamente uma destas quatro opções:
- Sustentado pelas evidências
- Contradito pelas evidências
- Evidências inconclusivas
- Evidências insuficientes

TRECHOS IDENTIFICADOS:
- Os trechos identificados devem ser retirados exclusivamente da ALEGAÇÃO DO USUÁRIO.
- Não copie frases dos artigos científicos para este campo.
- Selecione apenas palavras ou expressões da alegação que sejam importantes para a conclusão.
- Não invente trechos que não estejam presentes na alegação.

NÍVEL DE SUPORTE:
- Utilize uma escala de 0 a 100.
- O número representa quanto as evidências fornecidas sustentam a alegação do usuário.
- 0 significa ausência de suporte ou evidências fortemente contrárias.
- 100 significa suporte muito robusto à alegação.
- Este valor não representa probabilidade de a alegação ser verdadeira.
- O valor é provisório e será posteriormente substituído ou complementado por critérios objetivos do MedCheck.

Retorne SOMENTE um JSON válido neste formato:

{{
  "classificacao": "uma das quatro classificações",
  "nivel_suporte": 0,
  "explicacao": "explicação curta, clara e baseada nas evidências fornecidas",
  "trechos_identificados": ["trecho literal da alegação"]
}}
"""

    try:
    resposta = cliente.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

except ServerError as erro:
    if erro.code == 503:
        time.sleep(3)

        resposta = cliente.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
    else:
        raise

    texto_resposta = resposta.text.strip()

    if texto_resposta.startswith("```"):
        texto_resposta = texto_resposta.replace("```json", "").replace("```", "").strip()

    return json.loads(texto_resposta)

