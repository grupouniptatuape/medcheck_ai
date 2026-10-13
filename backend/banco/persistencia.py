
from backend.banco.conexao import conectar_banco


def salvar_analise(tipo_entrada, conteudo_original, resultado):
    conexao = conectar_banco()
    cursor = None

    try:
        cursor = conexao.cursor()
        conexao.start_transaction()

        # 1. Salvar o resultado principal
        sql_analise = """
            INSERT INTO analises (
                tipo_entrada,
                conteudo_original,
                alegacao_principal,
                classificacao,
                nivel_suporte,
                explicacao
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(sql_analise, (
            tipo_entrada,
            conteudo_original,
            resultado["alegacao_principal"],
            resultado["classificacao"],
            resultado["nivel_suporte"],
            resultado["explicacao"]
        ))

        id_analise = cursor.lastrowid

        # 2. Salvar os trechos identificados
        for ordem, trecho in enumerate(
            resultado["trechos_identificados"], start=1
        ):
            cursor.execute("""
                INSERT INTO trechos_analise (
                    id_analise, texto_trecho, ordem
                )
                VALUES (%s, %s, %s)
            """, (id_analise, trecho, ordem))

        # 3. Salvar as evidências científicas
        for ordem, evidencia in enumerate(
            resultado["evidencias"], start=1
        ):
            cursor.execute("""
                SELECT id_fonte
                FROM fontes
                WHERE nome = %s
            """, (evidencia["fonte"],))

            fonte = cursor.fetchone()

            if fonte is None:
                raise ValueError(
                    f"Fonte não cadastrada: {evidencia['fonte']}"
                )

            id_fonte = fonte[0]

            ano = evidencia.get("ano")
            ano = int(ano) if ano and str(ano).isdigit() else None

            cursor.execute("""
                INSERT INTO evidencias (
                    id_fonte,
                    titulo,
                    autores,
                    ano,
                    resumo,
                    url,
                    identificador_externo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    id_evidencia = LAST_INSERT_ID(id_evidencia)
            """, (
                id_fonte,
                evidencia["titulo"],
                evidencia.get("autores"),
                ano,
                evidencia.get("resumo"),
                evidencia.get("url"),
                evidencia.get("pmid")
            ))

            id_evidencia = cursor.lastrowid

            # 4. Relacionar o artigo à análise
            cursor.execute("""
                INSERT INTO analise_evidencias (
                    id_analise,
                    id_evidencia,
                    ordem
                )
                VALUES (%s, %s, %s)
            """, (id_analise, id_evidencia, ordem))

        conexao.commit()
        return id_analise

    except Exception:
        conexao.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conexao.close()
