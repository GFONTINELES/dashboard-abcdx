import pandas as pd
from sqlalchemy import create_engine, text
import os
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import streamlit as st

st.set_page_config(
    page_icon="🥶"
)
# Driver IBM
os.add_dll_directory(r"C:\Program Files\IBM\CLI_DRIVER\bin")

# Conexão DB2
engine = create_engine(
    "ibm_db_sa://consulta:sA%40Nc__MjPHU6%40!@FERREIRADB.DATACISS.COM.BR:50022/FERREIRA"
)

# Diretório base de saída
BASE_OUTPUT_DIR = (
    r"C:\Users\Ferreira\OneDrive\CIG-CONTROLADORIA"
    r"\3_third_task_abcdx_com_estoque"
)

data_final = datetime.now() - timedelta(days=1)
data_inicial = data_final - timedelta(days=90) 

data_final_str = data_final.strftime("%Y-%m-%d")
data_inicial_str = data_inicial.strftime("%Y-%m-%d")

print(f"📅 Período da consulta: {data_inicial_str} até {data_final_str}")

with engine.connect() as conn:
    conn.execute(text("SET SCHEMA DBA"))

# BUSCA DAS LOJAS
query_lojas = "SELECT idempresa FROM DBA.EMPRESA"
df_lojas = pd.read_sql(query_lojas, engine)
lojas = df_lojas["idempresa"].tolist()

print(f"🏬 Lojas encontradas: {lojas}")

def abc_by_group_excel_style(df, group_cols, item_col, value_col):
    grouped = (
        df.groupby(group_cols + [item_col])[value_col]
          .sum()
          .reset_index()
    )

    def classify_excel_style(group):
        group = group.sort_values(by=value_col, ascending=False).copy()

        total = group[value_col].sum()
        group['pct_contribution'] = group[value_col] / total
        group['cum_pct'] = group['pct_contribution'].cumsum() * 100

        abcx_labels = []

        for idx, row in group.iterrows():
            if row[value_col] == 0:
                abcx_labels.append('X')
                continue

            if idx == group.index[0]:
                abcx_labels.append('A')
                continue

            pct = row['cum_pct']

            if pct < 30:
                abcx_labels.append('A')
            elif pct < 60:
                abcx_labels.append('B')
            elif pct < 80:
                abcx_labels.append('C')
            elif pct < 99.75:
                abcx_labels.append('D')
            else:
                abcx_labels.append('X')

        group['ABCX'] = abcx_labels
        return group

    return (
        grouped
        .groupby(group_cols, group_keys=False)
        .apply(classify_excel_style)
        .reset_index(drop=True)
    )
def format_money_br(valor):
    return (
        valor
        .round(2)
        .map(lambda x: f"R$ {x:,.2f}"
             .replace(",", "X")
             .replace(".", ",")
             .replace("X", "."))
)

# SQL BASE (Consulta sem data de movimento 22/01)
SQL_BASE = """
SELECT
        PRODUTO.DESCRCOMPRODUTO ||' '|| PRODUTO_GRADE.SUBDESCRICAO AS DESCRRESPRODUTO,
        PRODUTO.IDDIVISAO,
        PRODUTO.IDSUBGRUPO,
        SUBGRUPO.DESCRSUBGRUPO,
        FORNECEDOR_PRODUTO.NOME AS FORNECEDOR,
        ESTOQUE_ANALITICO.IDPRODUTO,
        ESTOQUE_ANALITICO.IDEMPRESA,
        ESTOQUE_ANALITICO.IDSUBPRODUTO,
        ESTOQUE_ANALITICO.IDOPERACAO,
        ESTOQUE_ANALITICO.IDPLANILHA,
        ESTOQUE_ANALITICO.IDCREDITOCONTABIL,
        ESTOQUE_ANALITICO.IDDEBITOCONTABIL,
        ESTOQUE_ANALITICO.IDLOCALESTOQUE,
        ESTOQUE_ANALITICO.IDVENDEDOR,

        (SELECT
                DEPARTAMENTOS.DESCRDEPARTAMENTO
         FROM
                VENDEDOR_DEPARTAMENTO_HIST AS VDH
                INNER JOIN DEPARTAMENTOS
                    ON VDH.IDDEPARTAMENTO = DEPARTAMENTOS.IDDEPARTAMENTO
         WHERE
                VDH.IDVENDEDOR = ESTOQUE_ANALITICO.IDVENDEDOR
            AND VDH.DTCADASTRO = (
                    SELECT MAX(VDH2.DTCADASTRO)
                    FROM VENDEDOR_DEPARTAMENTO_HIST VDH2
                    WHERE
                        VDH2.IDVENDEDOR = ESTOQUE_ANALITICO.IDVENDEDOR
                        AND VDH2.DTCADASTRO <= NOTAS.DTMOVIMENTO
            )
        ) AS DESCRDEPARTAMENTO,

        ESTOQUE_ANALITICO.VALDESCONTOPRO,
        ESTOQUE_ANALITICO.VALFRETECONHEC,
        ESTOQUE_ANALITICO.VALICMS,
        ESTOQUE_ANALITICO.VALIPI,
        ESTOQUE_ANALITICO.VALISS,
        ESTOQUE_ANALITICO.VALICMSUBST,
        ESTOQUE_ANALITICO.VALUNITBRUTO,
        ESTOQUE_ANALITICO.VALTOTLIQUIDO,
        ESTOQUE_ANALITICO.QTDPRODUTO,
        ESTOQUE_ANALITICO.VALLUCRO AS VALLUCRO_UNITARIO,
        (ESTOQUE_ANALITICO.VALLUCRO * ESTOQUE_ANALITICO.QTDPRODUTO) AS VALLUCRO_LINHA,
        ESTOQUE_ANALITICO.PERICM,
        ESTOQUE_ANALITICO.PERCOMISSAO,
        ESTOQUE_ANALITICO.TIPOSITTRIB,
        ESTOQUE_ANALITICO.IDSITTRIB,
        ESTOQUE_ANALITICO.VALBASESUBST,
        ESTOQUE_ANALITICO.FLAGCONFENTREGA,
        ESTOQUE_ANALITICO.FLAGCALCULOGIRO,
        ESTOQUE_ANALITICO.FLAGMOVSALDOPRO,
        ESTOQUE_ANALITICO.FLAGMOVCONTABIL,
        OPERACAO_INTERNA.DESCROPERACAO,
        ESTOQUE_CADASTRO_LOCAL.DESCRLOCAL,
        ESTOQUE_ANALITICO.FLAGMOVCUSMEDIO,
        ESTOQUE_ANALITICO.IDEMPRESABAIXAEST,
        ESTOQUE_ANALITICO.TIPOCATEGORIA,
        OPERACAO_INTERNA.TIPOITEMCATEGORIA,
        ESTOQUE_ANALITICO.PERDESCONTOFINANCEIRO,
        NOTAS.NUMNOTA,
        NOTAS.SERIENOTA,
        USUARIO.NOMEUSUARIO,
        ESTOQUE_ANALITICO.NUMSEQUENCIA,
        NOTAS.IDCLIFOR,

        CASE
            WHEN DATE(B.DTHORAENCERRAMENTO) = DATE(ESTOQUE_ANALITICO.DTMOVIMENTO)
                 OR ESTOQUE_ANALITICO.IDOPERACAO <> 2000
            THEN
                COALESCE(
                    CAST(ESTOQUE_ANALITICO.DTMOVIMENTO || '-' || TIME(B.DTHORAENCERRAMENTO) AS TIMESTAMP),
                    CAST(ESTOQUE_ANALITICO.DTMOVIMENTO || '-' || TIME(NOTAS.DTALTERACAO) AS TIMESTAMP),
                    ESTOQUE_ANALITICO.DTMOVIMENTO || '-23.59.59.999999'
                )
            ELSE
                ESTOQUE_ANALITICO.DTMOVIMENTO || '-23.59.59.000000'
        END AS DTMOVIMENTO,

        COALESCE(B.DESCRBALANCO, NOTAS_OBS_PRODUTO.OBSERVACAO) AS MOTIVO,
        NOTAS.NUMCUPOMFISCAL,
        ESTOQUE_ANALITICO.IDLOTE,
        B.FLAGZERASEMCONTAGEM,
        COALESCE(OBS.OBSERVACAO, B.OBSERVACAO, '') AS OBSERVACAOPRODUTO,
        B.DESCRBALANCO,

        (SELECT COALESCE(V_VARCHAR,'F')
         FROM CONFIG_ATRIBUTO_VALORES
         WHERE IDATRIBUTO = 366
         FETCH FIRST 1 ROWS ONLY) AS FLAGEXIBEVALORBRUTO

FROM
        NOTAS
        LEFT JOIN CLIENTE_FORNECEDOR CF
            ON NOTAS.IDCLIFOR = CF.IDCLIFOR

        INNER JOIN ESTOQUE_ANALITICO
            ON NOTAS.IDEMPRESA = ESTOQUE_ANALITICO.IDEMPRESA
           AND NOTAS.IDPLANILHA = ESTOQUE_ANALITICO.IDPLANILHA

        INNER JOIN PRODUTO
            ON ESTOQUE_ANALITICO.IDPRODUTO = PRODUTO.IDPRODUTO

        LEFT JOIN PRODUTO_GRADE
            ON PRODUTO.IDPRODUTO = PRODUTO_GRADE.IDPRODUTO
           AND ESTOQUE_ANALITICO.IDSUBPRODUTO = PRODUTO_GRADE.IDSUBPRODUTO

        LEFT JOIN SUBGRUPO
            ON PRODUTO.IDSUBGRUPO = SUBGRUPO.IDSUBGRUPO

        -- 🔽 fornecedor correto do produto
        LEFT JOIN (
            SELECT
                PF.IDPRODUTO,
                PF.IDSUBPRODUTO,
                MIN(CF.NOME) AS NOME
            FROM PRODUTO_FORNECEDOR PF
            INNER JOIN CLIENTE_FORNECEDOR CF
                ON CF.IDCLIFOR = PF.IDCLIFOR
            GROUP BY
                PF.IDPRODUTO,
                PF.IDSUBPRODUTO
        ) FORNECEDOR_PRODUTO
            ON FORNECEDOR_PRODUTO.IDPRODUTO = PRODUTO.IDPRODUTO
           AND FORNECEDOR_PRODUTO.IDSUBPRODUTO = PRODUTO_GRADE.IDSUBPRODUTO

        LEFT JOIN NOTAS_OBS_PRODUTO
            ON ESTOQUE_ANALITICO.IDEMPRESA = NOTAS_OBS_PRODUTO.IDEMPRESA
           AND ESTOQUE_ANALITICO.IDPLANILHA = NOTAS_OBS_PRODUTO.IDPLANILHA
           AND ESTOQUE_ANALITICO.NUMSEQUENCIA = NOTAS_OBS_PRODUTO.NUMSEQUENCIA

        LEFT JOIN ESTOQUE_BALANCO_ENCERRADO B
            ON ESTOQUE_ANALITICO.IDEMPRESA = B.IDEMPRESA
           AND ESTOQUE_ANALITICO.IDPLANILHA = B.IDPLANILHA
           AND ESTOQUE_ANALITICO.IDPRODUTO = B.IDPRODUTO
           AND ESTOQUE_ANALITICO.IDSUBPRODUTO = B.IDSUBPRODUTO
           AND ESTOQUE_ANALITICO.IDLOCALESTOQUE = B.IDLOCALESTOQUE
           AND COALESCE(ESTOQUE_ANALITICO.IDLOTE,'') = COALESCE(B.IDLOTE,'')

        LEFT JOIN DOCUMENTO_OBSERVACAO_PRODUTO_HISTORICO OBS
            ON ESTOQUE_ANALITICO.IDEMPRESA = OBS.IDEMPRESA
           AND ESTOQUE_ANALITICO.IDPLANILHA = OBS.IDPLANILHA
           AND ESTOQUE_ANALITICO.IDPRODUTO = OBS.IDPRODUTO
           AND ESTOQUE_ANALITICO.IDSUBPRODUTO = OBS.IDSUBPRODUTO
           AND ESTOQUE_ANALITICO.NUMSEQUENCIA = OBS.NUMSEQUENCIA

        INNER JOIN ESTOQUE_CADASTRO_LOCAL
            ON ESTOQUE_ANALITICO.IDLOCALESTOQUE = ESTOQUE_CADASTRO_LOCAL.IDLOCALESTOQUE

        INNER JOIN OPERACAO_INTERNA
            ON ESTOQUE_ANALITICO.IDOPERACAO = OPERACAO_INTERNA.IDOPERACAO

        INNER JOIN USUARIO
            ON NOTAS.IDUSUARIO = USUARIO.IDUSUARIO

WHERE
        ESTOQUE_ANALITICO.IDOPERACAO NOT IN (1301, 3000)
    AND OPERACAO_INTERNA.TIPOITEMCATEGORIA <> 'D11'
    AND UPPER(ESTOQUE_CADASTRO_LOCAL.DESCRLOCAL) LIKE '%AREA VENDA%'
    AND UPPER(OPERACAO_INTERNA.DESCROPERACAO) LIKE 'VENDA%'
    AND ESTOQUE_ANALITICO.IDEMPRESA = {loja}
    AND ESTOQUE_ANALITICO.DTMOVIMENTO >= TIMESTAMP('{data_inicial} 00:00:00')
    AND ESTOQUE_ANALITICO.DTMOVIMENTO <  TIMESTAMP('{data_final} 23:59:59')

"""
#inner join 
#left join idsubgrupo, idempresa, dtmovimento, estoque_analitico.dtmovimento
SQL_ESTOQUE = """
SELECT
    ES.IDEMPRESA,
    ES.IDPRODUTO,
    ES.IDSUBPRODUTO,
    SUM(ES.QTDATUALESTOQUE) AS QTD_ESTOQUE_ATUAL
FROM (
    SELECT
        ES.IDEMPRESA,
        ES.IDPRODUTO,
        ES.IDSUBPRODUTO,
        ES.IDLOCALESTOQUE,
        ES.QTDATUALESTOQUE,
        ROW_NUMBER() OVER (
            PARTITION BY
                ES.IDEMPRESA,
                ES.IDPRODUTO,
                ES.IDSUBPRODUTO,
                ES.IDLOCALESTOQUE
            ORDER BY
                ES.DTMOVIMENTO DESC
        ) AS ORDEM
    FROM DBA.ESTOQUE_SINTETICO ES
    INNER JOIN DBA.ESTOQUE_CADASTRO_LOCAL L
        ON ES.IDLOCALESTOQUE = L.IDLOCALESTOQUE
    WHERE
        ES.IDEMPRESA = {loja}
        AND ES.DTMOVIMENTO <= DATE('{data_final}')
        AND UPPER(L.DESCRLOCAL) LIKE '%AREA VENDA%'
) ES
WHERE ORDEM = 1
GROUP BY
    ES.IDEMPRESA,
    ES.IDPRODUTO,
    ES.IDSUBPRODUTO
"""
SQL_CUSTO_MEDIO = """
SELECT
    FE.IDEMPRESA,
    FE.IDPRODUTO,
    FE.IDSUBPRODUTO,
    FE.VALCUSTOMEDIO
FROM CISSANALYTICS.FATO_ESTOQUE_ATUAL FE
WHERE
    FE.IDEMPRESA = {loja}
"""

SQL_LUCRO = """
SELECT
    EA.IDEMPRESA,
    EA.IDPRODUTO,
    EA.IDSUBPRODUTO,
    SUM(
        CASE
            WHEN NES.TIPOMOVIMENTO = 'E'
                THEN (EA.VALLUCRO * EA.QTDPRODUTO) * (-1)
            ELSE (EA.VALLUCRO * EA.QTDPRODUTO)
        END
    ) AS VALLUCRO_TOTAL
FROM
    DBA.ESTOQUE_ANALITICO EA
    INNER JOIN DBA.NOTAS_ENTRADA_SAIDA NES
        ON NES.IDEMPRESA   = EA.IDEMPRESA
       AND NES.IDPLANILHA  = EA.IDPLANILHA
       AND EA.DTMOVIMENTO >= NES.DTMOVIMENTO
       AND EA.DTMOVIMENTO <  NES.DTMOVIMENTO + 1 DAY
    INNER JOIN DBA.NOTAS N
        ON N.IDEMPRESA  = NES.IDEMPRESA
       AND N.IDPLANILHA = NES.IDPLANILHA
WHERE
    N.FLAGNOTACANCEL = 'F'
    AND NES.FLAGMOVPRODUTOS = 'T'
    AND NES.TIPOMOVIMENTO IN ('V','E','O')
    AND (EA.NUMSEQUENCIAKIT IS NULL OR EA.NUMSEQUENCIAKIT <= 0)
    AND EA.IDEMPRESA = {loja}
    AND EA.DTMOVIMENTO >= TIMESTAMP('{data_inicial} 00:00:00')
    AND EA.DTMOVIMENTO <  TIMESTAMP('{data_final} 23:59:59')
GROUP BY
    EA.IDEMPRESA,
    EA.IDPRODUTO,
    EA.IDSUBPRODUTO
"""

MAPA_DDE_IDEAL = {
    0: 25,    # <PRODUTOS SEM DIVISÃO>
    1: 8,     # AÇOUGUE
    2: 45,    # ALMOXARIFADO
    3: 45,    # BAZAR
    4: 25,    # COMMODITIES
    5: 6,     # CONFEITARIA/PADARIA
    6: 30,    # CONGELADOS
    7: 25,    # FRIOS E RESFRIADOS
    8: 40,    # HIGIENE E LIMPEZA
    9: 6,     # HORTIFRUTI
    10: 25,   # MERCEARIA LÍQUIDA
    11: 24,   # MERCEARIA SECA DOCE
    12: 15,   # MERCEARIA SECA SALGADA
    13: 25,   # PADARIA INDUSTRIALIZADOS
    14: 45,   # PERFUMARIA
    15: 25,   # PRODUTOS NATURAIS
    16: 35,   # RESFRIADOS LÁCTEOS
    17: 6,    # ROTISSERIE
    18: 6     # SALGADOS
}

# EXECUÇÃO POR LOJA
for loja in lojas:
    print(f"\n🚀 Processando loja {loja}...")
    start = time.time()

    query = SQL_BASE.format(
        loja=loja,
        data_inicial=data_inicial_str,
        data_final=data_final_str
    )

    query_estoque = SQL_ESTOQUE.format(
        loja=loja,
        data_final=data_final_str
    )

    query_lucro = SQL_LUCRO.format(
        loja=loja,
        data_inicial=data_inicial_str,
        data_final=data_final_str
    )

    df_lucro = pd.read_sql(query_lucro, engine)
    df_estoque = pd.read_sql(query_estoque, engine)
    query_custo_medio = SQL_CUSTO_MEDIO.format(loja=loja)
    df_custo_medio = pd.read_sql(query_custo_medio, engine)


    try:
        df = pd.read_sql(query, engine)
        df = (
            df
            .groupby(
                [
                    'idempresa',
                    'idproduto',
                    'idsubproduto',
                    'descrresproduto',
                    'iddivisao',
                    'idsubgrupo',
                    'fornecedor',
                ],
                as_index=False
            )
            .agg({
                'qtdproduto': 'sum',
                'valtotliquido': 'sum',
                'vallucro_linha': 'sum',
                'descrlocal': 'first',
                'descroperacao': 'first'
            })
        )


        if df.empty:
            print(f"⚠️ Loja {loja}: nenhum dado retornado.")
            continue

        print(f"✅ Loja {loja}: {len(df):,} registros")
        
        abc_empresa = abc_by_group_excel_style(
            df=df,
            group_cols=['idempresa'],
            item_col='descrresproduto', 
            value_col='valtotliquido'
        )[[
            'idempresa',
            'descrresproduto',
            'pct_contribution',
            'ABCX'
        ]].rename(columns={
            'ABCX': 'ABCX_EMPRESA',
            'pct_contribution': 'PCT_CONTRIB_EMPRESA'
        })

        abc_subgrupo = abc_by_group_excel_style(
            df=df,
            group_cols=['idempresa', 'idsubgrupo'],
            item_col='descrresproduto',
            value_col='valtotliquido'
        )[[
            'idempresa',
            'idsubgrupo',
            'descrresproduto',
            'pct_contribution',
            'ABCX'
        ]].rename(columns={
            'ABCX': 'ABCX_SUBGRUPO',
            'pct_contribution': 'PCT_CONTRIB_SUBGRUPO',
        })

        df_final = (
            df
            .merge(
                abc_empresa,
                on=['idempresa', 'descrresproduto'],
                how='left'
            )

            .merge(
                abc_subgrupo,
                on=['idempresa', 'idsubgrupo', 'descrresproduto'],
                how='left'
            )
        )

        df_final = df_final.merge(
            df_estoque,
            on=['idempresa', 'idproduto', 'idsubproduto'],
            how='left'
        )
        df_final = df_final.merge(
            df_custo_medio,
            on=['idempresa', 'idproduto', 'idsubproduto'],
            how='left'
        )

        df_final['DDE_IDEAL'] = (
            df_final['iddivisao']
            .map(MAPA_DDE_IDEAL)
            .fillna(25)  
            .astype(int)
        )

        df_final['qtd_estoque_atual'] = (
            df_final['qtd_estoque_atual']
            .fillna(0)
        )
        df_final['MDV'] = (
            df_final['valtotliquido']
                .fillna(0)
                .astype(float)
                / 90
        )
        df_final = df_final.merge(
            df_lucro,
            on=['idempresa', 'idproduto', 'idsubproduto'],
            how='left'
        )

        df_final['vallucro_total'] = (
            df_final['vallucro_total']
            .fillna(0)
        )
        df_final['margem'] = (
            df_final['vallucro_linha']
            / df_final['valtotliquido']
        ).replace([float('inf'), -float('inf')], 0).fillna(0)

        df_final['margem_pct'] = ((df_final['margem'] * 100) + 3).round(0)
        df_final['CMV_DIA'] = (
            df_final['MDV'] * (1 - (df_final['margem_pct'] / 100))
        )
        df_final['VALORDDE_IDEAL'] = (
            df_final['DDE_IDEAL'] * df_final['CMV_DIA']
        )
        df_final['DDE_ATUAL'] = (
            df_final['qtd_estoque_atual'] / df_final['CMV_DIA']
        ).replace([float('inf'), -float('inf')], 0).fillna(0)

        df_final['DDE_ATUAL'] = df_final['DDE_ATUAL'].round(1)
        df_final['valcustomedio'] = (
            df_final['valcustomedio']
            .fillna(0)
            .astype(float)
        )
        df_final['RUPTURA'] = (
            (df_final['valcustomedio'] <= 0)
            .astype(int)
        )
        df_final['RUPTURAVALOR'] = (
            df_final['RUPTURA'] * df_final['CMV_DIA']
        )


        df_final['MDV_MONETÁRIO'] = format_money_br(df_final['MDV'])
        df_final['CMV_POR_DIA'] = format_money_br(df_final['CMV_DIA'])
        df_final['VALOR_DDE_IDEAL'] = format_money_br(df_final['VALORDDE_IDEAL'])
        df_final['ESTOQUE_CUSTO_MEDIO'] = format_money_br(
            df_final['valcustomedio']
        )
        df_final['RUPTURA_VALOR'] = format_money_br(
            df_final['RUPTURAVALOR']
        )

        pasta_loja = os.path.join(BASE_OUTPUT_DIR, str(loja))
        os.makedirs(pasta_loja, exist_ok=True)

        output_file = os.path.join(pasta_loja, f"abcdx_estoque_{loja}_{data_final_str}.parquet"
)
       
        #COLUNAS A EXCLUIR DO DATAFRAME FINAL
        COLUNAS_EXCLUIR = [
            'vallucro_total',
            'margem',
            'MDV',
            'CMV_DIA',
            'motivo',
            'numcupomfiscal',
            'idlote',
            'flagzerasemcontagem',
            'observacaoproduto',
            'descrbalanco',
            'flagexibevalorbruto',
            'valbasesubst',
            'tiposittrib',
            'idcreditocontabil',
            'iddebitocontabil',
            'idvendedor',
            'descrdepartamento',
            'valfreteconhec',
            'VALORDDE_IDEAL',
            'valcustomedio',
            'RUPTURAVALOR',
        ]
        df_final = df_final.drop(
            columns=COLUNAS_EXCLUIR,
            errors='ignore'  
        )
        # salva parquet
        df_final.to_parquet(output_file, index=False)

        print(f"💾 Arquivo salvo em: {output_file}")

    except Exception as e:
        print(f"❌ Erro na loja {loja}: {e}")

    end = time.time()
    print(f"⏱️ Tempo da loja {loja}: {end - start:.2f}s")

print("\n🏁 Processamento finalizado para todas as lojas.")
#evitar redundância e robustez 
#consulta de abcdx com estoque