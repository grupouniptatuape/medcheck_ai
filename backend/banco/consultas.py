
from backend.banco.conexao import conectar_banco


def buscar_analise(id_analise):
    conexao = conectar_banco()
    cursor = None

    try:
        cursor = conexao.cursor(dictionary=True)

        # 1. Buscar os dados principais da análise
        cursor.execute("""
            SELECT
                id_analise,
                tipo_entrada,
                conteudo_original,
                alegacao_principal,
                classificacao,
                nivel_suporte,
                explicacao,
                criada_em
            FROM analises
            WHERE id_analise = %s
        """, (id_analise,))

        analise = cursor.fetchone()

        if analise is None:
            return None

        # 2. Buscar os artigos científicos relacionados
        cursor.execute("""
            SELECT
                e.id_evidencia,
                e.identificador_externo AS pmid,
                e.titulo,
                e.autores,
                e.ano,
                e.resumo,
                e.url,
                f.nome AS fonte
            FROM analise_evidencias ae
            INNER JOIN evidencias e
                ON ae.id_evidencia = e.id_evidencia
            INNER JOIN fontes f
                ON e.id_fonte = f.id_fonte
            WHERE ae.id_analise = %s
            ORDER BY ae.ordem
        """, (id_analise,))

        analise["evidencias"] = cursor.fetchall()

        # 3. Buscar os trechos identificados
        cursor.execute("""
            SELECT texto_trecho
            FROM trechos_analise
            WHERE id_analise = %s
            ORDER BY ordem
        """, (id_analise,))

        analise["trechos_identificados"] = [
            linha["texto_trecho"]
            for linha in cursor.fetchall()
        ]

        return analise

    finally:
        if cursor is not None:
            cursor.close()

        conexao.close()


def buscar_historico(identificador_visitante, limite=20):
    conexao = conectar_banco()
    cursor = None

    try:
        cursor = conexao.cursor(dictionary=True)

        consulta = """
            SELECT
                id_analise,
                tipo_entrada,
                alegacao_principal,
                classificacao,
                nivel_suporte,
                criada_em
            FROM analises
            WHERE identificador_visitante = %s
            ORDER BY criada_em DESC, id_analise DESC
            LIMIT %s
        """

        cursor.execute(
            consulta,
            (identificador_visitante, limite)
        )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        conexao.close()
