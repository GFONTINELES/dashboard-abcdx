import pandas as pd 
from sqlalchemy import create_engine, text
import os
import time
from datetime import datetime, timedelta
import sys

# Caminho do driver IBM
os.add_dll_directory(r"C:\Program Files\IBM\CLI_DRIVER\bin")


engine = create_engine(
    "ibm_db_sa://consulta:sA%40Nc__MjPHU6%40!@FERREIRADB.DATACISS.COM.BR:50022/FERREIRA"
)
loja_arg = None
data_inicial_arg = None
data_final_arg = None
pasta_destino_arg = None

if len(sys.argv) >= 2:
    try:
        loja_arg = int(sys.argv[1])
    except Exception:
        loja_arg = None

if len(sys.argv) >= 3:
    data_inicial_arg = sys.argv[2]

if len(sys.argv) >= 4:
    data_final_arg = sys.argv[3]

if len(sys.argv) >= 5:
    pasta_destino_arg = sys.argv[4]

# Se data_final_arg foi passada use ela; caso contrário mantenha a lógica atual
if data_final_arg:
    ontem = data_final_arg
else:
    from datetime import datetime, timedelta
    ontem = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')

print(f"📅 Data filtrada automaticamente: {ontem}")
# Define o schema padrão
with engine.connect() as conn:
    conn.execute(text("SET SCHEMA DBA"))

query_lojas = "SELECT * FROM dba.empresa"
df_lojas = pd.read_sql(query_lojas, engine)
#df_lojas = df_lojas[df_lojas["idempresa"].isin([2])]#---------------------------

if loja_arg is not None:
    lojas2 = [loja_arg]
else:
    lojas2 = df_lojas["idempresa"].tolist()

print(f"Lojas encontradas para processamento: {lojas2}")

for loja in lojas2:
    print(f"\n🚀 Executando consulta para a loja {loja}...")

    # Cria a query dinamicamente, usando a loja atual e a data de ontem
    query = f"""
WITH BASE AS (
    SELECT 
        Q1.*,
        (CUSTOMEDIOUN * QTDATUALESTOQUE) AS CUSTOMEDIOTOTAL
    FROM
    (
        SELECT
            COALESCE(EMPRESA.IDEMPRESA, 0) AS IDEMPRESA,
            TRIM(COALESCE(EMPRESA.RAZAOSOCIAL, 'PRODUTOS SEM MOVIMENTAÇÃO DE ESTOQUE')) AS RAZAOSOCIAL,
            PVIEW.IDDIVISAO,
            DIVISAO.DESCRDIVISAO,
            PVIEW.IDSECAO,
            SECAO.DESCRSECAO,
            PVIEW.IDGRUPO,
            GRUPO.DESCRGRUPO,
            PVIEW.IDSUBGRUPO,
            SUBGRUPO.DESCRSUBGRUPO,
            PVIEW.IDPRODUTO,
            PVIEW.IDSUBPRODUTO,
            PVIEW.IDCODBARPROD,
            PVIEW.DESCRICAOPRODUTO,
            PVIEW.TIPOBAIXAMESTRE,
            PVIEW.EMBALAGEMENTRADA,
            PVIEW.VALGRAMAENTRADA,
            LOCAL.IDLOCALESTOQUE,
            LOCAL.DESCRLOCAL,
            RTRIM(LTRIM(PVIEW.FABRICANTE)) AS FABRICANTE,
            COALESCE(SINTETICO.QTDATUALESTOQUE, 0) AS QTDATUALESTOQUE,
            COALESCE(PRECOS.CUSTONOTAFISCAL, 0) AS CUSTONOTAFISCAL,
            COALESCE(PRECOS.CUSTONOTAFISCAL, 0) * COALESCE(SINTETICO.QTDATUALESTOQUE, 0) AS CUSTOTOTAL,

            COALESCE(SINTETICO_MES_ANTERIOR.QTDATUALESTOQUE, 0) AS QTD_ESTOQUE_MES_ANTERIOR,
            COALESCE(SINTETICO_MES_ANTERIOR.IDLOCALESTOQUE, 0) AS IDLOCAL_MES_ANTERIOR,
            COALESCE(LOCAL_MES_ANTERIOR.DESCRLOCAL, '') AS DESCRLOCAL_MES_ANTERIOR,

            PRECOS.VALPRECOVAREJO,
            PRECOS.CUSTOULTIMACOMPRA,
            CAST(
                DBA.UF_BUSCACUSTOMEDIO(
                    SINTETICO.IDEMPRESA,
                    SINTETICO.IDPRODUTO,
                    SINTETICO.IDSUBPRODUTO,
                    CAST(0 AS INTEGER),
                    SINTETICO.DTMOVIMENTO
                ) AS DECIMAL(15, 6)
            ) AS CUSTOMEDIOUN,
            PG.IDCODBARPRODTRIB,
            LENGTH(CAST(PG.IDCODBARPRODTRIB AS VARCHAR(14))) AS LENGTHIDCODBARPRODTRIB
        FROM
            DBA.PRODUTOS_VIEW AS PVIEW
            INNER JOIN DBA.PRODUTO_GRADE AS PG
                ON PG.IDPRODUTO = PVIEW.IDPRODUTO
               AND PG.IDSUBPRODUTO = PVIEW.IDSUBPRODUTO
            LEFT OUTER JOIN DBA.DIVISAO AS DIVISAO
                ON PVIEW.IDDIVISAO = DIVISAO.IDDIVISAO
            JOIN DBA.SECAO AS SECAO
                ON SECAO.IDSECAO = PVIEW.IDSECAO
            JOIN DBA.GRUPO AS GRUPO
                ON GRUPO.IDGRUPO = PVIEW.IDGRUPO
            JOIN DBA.SUBGRUPO AS SUBGRUPO
                ON SUBGRUPO.IDSUBGRUPO = PVIEW.IDSUBGRUPO
            JOIN (
                SELECT
                    IDEMPRESA,
                    IDPRODUTO,
                    IDSUBPRODUTO,
                    IDLOCALESTOQUE,
                    QTDATUALESTOQUE,
                    DTMOVIMENTO
                FROM
                (
                    SELECT
                        IDEMPRESA,
                        IDPRODUTO,
                        IDSUBPRODUTO,
                        IDLOCALESTOQUE,
                        QTDATUALESTOQUE,
                        DTMOVIMENTO,
                        ROW_NUMBER() OVER(
                            PARTITION BY IDEMPRESA, IDPRODUTO, IDSUBPRODUTO, IDLOCALESTOQUE
                            ORDER BY DTMOVIMENTO DESC
                        ) AS ORDEM
                    FROM
                        DBA.ESTOQUE_SINTETICO AS ES
                    WHERE
                        ES.IDEMPRESA = {loja}
                        AND ES.DTMOVIMENTO <= date('{ontem}')
                ) AS ES
                WHERE
                    ORDEM = 1
            ) AS SINTETICO
                ON SINTETICO.IDPRODUTO = PVIEW.IDPRODUTO
               AND SINTETICO.IDSUBPRODUTO = PVIEW.IDSUBPRODUTO
            LEFT JOIN (
                SELECT
                    IDEMPRESA,
                    IDPRODUTO,
                    IDSUBPRODUTO,
                    IDLOCALESTOQUE,
                    QTDATUALESTOQUE,
                    DTMOVIMENTO
                FROM (
                    SELECT
                        IDEMPRESA,
                        IDPRODUTO,
                        IDSUBPRODUTO,
                        IDLOCALESTOQUE,
                        QTDATUALESTOQUE,
                        DTMOVIMENTO,
                        ROW_NUMBER() OVER(
                            PARTITION BY IDEMPRESA, IDPRODUTO, IDSUBPRODUTO, IDLOCALESTOQUE
                            ORDER BY DTMOVIMENTO DESC
                        ) AS ORDEM
                    FROM DBA.ESTOQUE_SINTETICO
                    WHERE
                        IDEMPRESA = {loja}
                        AND DTMOVIMENTO <= DATE('{ontem}') - 30 DAY
                ) AS ES
                WHERE ORDEM = 1
            ) AS SINTETICO_MES_ANTERIOR
                ON SINTETICO_MES_ANTERIOR.IDPRODUTO = PVIEW.IDPRODUTO
               AND SINTETICO_MES_ANTERIOR.IDSUBPRODUTO = PVIEW.IDSUBPRODUTO

            LEFT OUTER JOIN DBA.ESTOQUE_CADASTRO_LOCAL AS LOCAL
                ON SINTETICO.IDLOCALESTOQUE = LOCAL.IDLOCALESTOQUE

            LEFT OUTER JOIN DBA.ESTOQUE_CADASTRO_LOCAL AS LOCAL_MES_ANTERIOR
                ON SINTETICO_MES_ANTERIOR.IDLOCALESTOQUE = LOCAL_MES_ANTERIOR.IDLOCALESTOQUE

            JOIN DBA.POLITICA_PRECO_PRODUTO AS PRECOS
                ON PRECOS.IDPRODUTO = SINTETICO.IDPRODUTO
               AND PRECOS.IDSUBPRODUTO = SINTETICO.IDSUBPRODUTO
               AND PRECOS.IDEMPRESA = SINTETICO.IDEMPRESA

            LEFT OUTER JOIN DBA.EMPRESA AS EMPRESA
                ON EMPRESA.IDEMPRESA = SINTETICO.IDEMPRESA

        WHERE
            PVIEW.FLAGINATIVO = ('F')
            AND SINTETICO.QTDATUALESTOQUE >= (-99999999)
            AND UPPER(LOCAL.DESCRLOCAL) LIKE '%AREA VENDA%'
    ) AS Q1
),

MODA AS (
    SELECT 
        DESCRLOCAL_MES_ANTERIOR,
        COUNT(*) AS FREQ,
        ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS RN
    FROM BASE
    GROUP BY DESCRLOCAL_MES_ANTERIOR
)

SELECT *
FROM BASE
WHERE DESCRLOCAL_MES_ANTERIOR = (SELECT DESCRLOCAL_MES_ANTERIOR FROM MODA WHERE RN = 1);
"""

start = time.time()
try:
        df = pd.read_sql(query, engine)

        if df.empty:
            print(f"⚠️ Loja {loja}: Nenhum dado retornado.")
        else:
            print(f"✅ Loja {loja}: {len(df):,} registros encontrados.")

            # define pasta destino
            if pasta_destino_arg:
                pasta_destino = pasta_destino_arg
            else:
                pasta_destino = r"C:\Users\Pc Ferreira\Documents\balanco_sql_teste\resultados"
            os.makedirs(pasta_destino, exist_ok=True)

            # salva o arquivo parquet
            output_file = os.path.join(pasta_destino, f"{data_inicial_arg},150052 {loja}.parquet")
            df.to_parquet(output_file, index=False)
            print(f"💾 Arquivo salvo: {output_file}")

except Exception as e:
        print(f"❌ Erro ao executar a consulta da loja {loja}: {e}")

end = time.time()
print(f"⏱️ Tempo total: {end - start:.2f} segundos.")

print("\n🏁 Todas as consultas foram processadas.")

#    WHERE
            #PVIEW.FLAGINATIVO = ('F')
            #AND SINTETICO.QTDATUALESTOQUE >= (-99999999)
            #AND UPPER(LOCAL.DESCRLOCAL) LIKE '%AREA VENDA%'
    #) AS Q1