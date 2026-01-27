import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


#criar login 
#BASE_DIR = r"C:\Users\Ferreira\OneDrive\CIG-CONTROLADORIA\3_third_task_abcdx_com_estoque"
BASE_DIR = "data"
st.set_page_config(
    page_title="Dashboard ABCDX & Ruptura",
    layout="wide"
)


credentials = {
    "usernames":{
        "gestao_um": {
            "name": "Gestor Loja 1",
            "password": '$2b$12$jgw50OJxyvrl.bTWXJHxKOVuyUMZCK6ibrcDXrYE3eLXgmpXEx6O2', #gestor@123
            "role": "gestor",
            "lojas": ["1"]
        },
        "gestor_dois": {
            "name": "Gestor Loja 2",
            "password": '$2b$12$4FYJS/afhW7FMM7601YGie1tQqKapnhDhKsiq3wrih3dqXM7e1br2', #lojad0isgvr
            "role": "gestor",
            "lojas": ["2"]
        },
        "gestor_tres": {
            "name": "Gestor Loja 3",
            "password": '$2b$12$71FH61QS8gLxu/oJoQjSh.zmUzA.8MwddcpBGskd1HBcNGLocxdoy', #GestaoljaFR3
            "role": "gestor",
            "lojas": ["3"]
        },
        "gestor_quatro": {
            "name": "Gestor Loja 4",
            "password": '$2b$12$.zXygYbZXA1skXcLGaVa9eGTvR1C2VHmgPMrWuO53Z66nsB6Z4x7W', #quatr0loj2
            "role": "gestor",
            "lojas": ["4"]
        },
        "gestor_cinco": {
            "name": "Gestor Loja 5",
            "password": '$2b$12$hejES75TMEIgJBxron05iewrTH8Un6TOC2UhRdAgQEn9VwSLGVR.a', #Loj2@c1nc0
            "role": "gestor",
            "lojas": ["5"]
        },
        "gestor_seis": {
            "name": "Gestor Loja 6",
            "password": '$2b$12$FmLkidPX8qd7JyxPbRaoMuO8xLcw3OkzFqVMxU8pDbOk5kpKMLey2', #lo6ja@66Ferr
            "role": "gestor",
            "lojas": ["6"]
        },
        "gestor_sete": {
            "name": "Gestor Loja 7",
            "password": '$2b$12$Ybg2vQnvn3E.SlLAOgfSeuEhv24kgOYi1QiX.J14hevIgGQcgEP5G', #loj@set3@7
            "role": "gestor",
            "lojas": ["7"]
        },
        "gestor_oito": {
            "name": "Gestor Loja 8",
            "password": '$2b$12$zQrAbzJcg82x6PdnL6vZ.O8TjHuDYB32ex6nUNy6zy6yB6Dhuu2S.', #@gerencia_8@8
            "role": "gestor",
            "lojas": ["8"]
        },
        "gestor_nove": {
            "name": "Gestor Loja 9",
            "password": '$2b$12$w4lcPbVSTVKR.y.3hb5cn.K9yUxsptCDqVj9jSKwIDNICleQuMZXa', #NovE@ferR
            "role": "gestor",
            "lojas": ["9"]
        },
        "gestor_dez": {
            "name": "Gestor Loja 10",
            "password": '$2b$12$6Ymh4bSooQahWd0iPTdLVOYqPaHJfeWdqmGK/o80RToZILI/iXuCG', #ger@dEz@10
            "role": "gestor",
            "lojas": ["10"]
        },
        "gestor_11": {
            "name": "Gestor Loja 11",
            "password": '$2b$12$my8cW50.oQrXe4vL9DTUtO8S7GbJRBzKV37LOyymgBtjKvtismX92', #gestao_11@G
            "role": "gestor",
            "lojas": ["11"]
        },
        "gestor_doze": {
            "name": "Gestor Loja 12",
            "password": '$2b$12$R9S8Ot/Qy1oBS0/rYYEs2.P3afEWzhkCHO0lZCK6PE29GjD6dqkYm', #12gestao_d0ZE
            "role": "gestor",
            "lojas": ["12"]
        },
        "gestor_treze": {
            "name": "Gestor Loja 13",
            "password": '$2b$12$u2KiS.Fmd8g6Mp0kRJ.XFefX.xxw/tIT83WbONjgifHUcmkb8M8Fe', #treze_@gEs
            "role": "gestor",
            "lojas": ["13"]
        },
        "gestor_catorze": {
            "name": "Gestor Loja 14",
            "password": '$2b$12$STA8WaoJ1f4kHOwhd8/JoOJwRskVUH4m1ltCaU5i3GvyB3Nra8jM6', #loja14@QtZ
            "role": "gestor",
            "lojas": ["14"]
        },
        "gestor_quinze": {
            "name": "Gestor Loja 15",
            "password": '$2b$12$M.IIhRxTYjEwm88CdBVhkeXjG7tg/AfZCW9YAbo0ETLoGVQl617ai', #qUiNz@@15
            "role": "gestor",
            "lojas": ["15"]
        },
        "gestor_dezesseis": {
            "name": "Gestor Loja 16",
            "password": '$2b$12$cLLjOIhkHdg62hoYHBLqS.y/zG8LekTwsdNEZzBuecXiXlBRKKcXu', #ges_16@gE
            "role": "gestor",
            "lojas": ["16"]
        },
        "gestor_dezessete": {
            "name": "Gestor Loja 17",
            "password": '$2b$12$P8/EotWTCKNTJ.s2RPpy7OdwIPpyYJdsMHnqiaQFW9KdXTh9nEDfW', #17@@LOj_1
            "role": "gestor",
            "lojas": ["17"]
        },
        "gestor_18": {
            "name": "Gestor Loja 18",
            "password": '$2b$12$w6uEpYiy3i5Kryr/viFUneMy2gV4G04wpmUVRXzRCgyvC7I0BvFhi', #p8fer_@188
            "role": "gestor",
            "lojas": ["18"]
        },
        "gestor_21": {
            "name": "Gestor Loja 21",
            "password": '$2b$12$YxWqJU1cMlQintlFphZA.OViJaAg4Rs0zMNkpKrEC56gyKigVvwS6', #GestAO21@2026
            "role": "gestor",
            "lojas": ["21"]
        },
        "gestor_22": {
            "name": "Gestor Loja 22",
            "password": '$2b$12$N88iRri8LRjb8FoN7eLyTOwCInIAow8QWyc8hsyEMUrXf.cahtBra', #LJ22@feRR
            "role": "gestor",
            "lojas": ["22"]
        },
        "gestor_23": {
            "name": "Gestor Loja 23",
            "password": '$2b$12$39x8ajUR1X/jAwgtNcU34.78Hdqn1sqObkeZTeyxpsXklaRWKZ9cW', #Ferr@F23@
            "role": "gestor",
            "lojas": ["23"]
        },
        "gestor_24": {
            "name": "Gestor Loja 24",
            "password": '$2b$12$TIYx/DLCXI6Fq.ZUo8mebeJnQua7hOrnbDR3BosZhwKKwSwznH4Km', #24@FeRReira42
            "role": "gestor",
            "lojas": ["24"]
        },
        "gestor_25": {
            "name": "Gestor Loja 25",
            "password": '$2b$12$E10bekqh2Ehgc8XxJ7FDZO0NomoX0JLVWgDLfl3kCZopHQTefTIQi', #L25_lj@feR
            "role": "gestor",
            "lojas": ["25"]
        },
        "gestor_101": {
            "name": "Gestor Loja 101",
            "password": '$2b$12$8VYAjm2fgiQ9BTIibpuTUecFn3wV1PsQ39GFdcUjZ66Dol8NXQLda', #Loja@101FRR
            "role": "gestor",
            "lojas": ["101"]
        },
        "diretoria": {
            "name": "Diretor Geral",
            "password": "$2b$12$wcWIGSeo8Bsrc8q4dF9fCODJncEhEYuD84MToAbXM9a1sEkVNMxnK", #diretor@123
            "role": "diretor",
            "lojas": []
        }
    }
}


# LOGIN
# ===============================
authenticator = stauth.Authenticate(
    credentials,
    "abcdx_dashboard",
    "abcdef123456",
    cookie_expiry_days=7
)

authenticator.login(location="sidebar")

authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")
name = st.session_state.get("name")

#deveser sidebar, ou main
if authentication_status is False:
    st.error("Usuário ou senha incorretos")
    st.stop()

if authentication_status is None:
    st.warning("Digite seu usuário e senha")
    st.stop()

authenticator.logout("logout", "sidebar")

perfil = credentials["usernames"][username]

# ===============================
# CONTROLE DE LOJA
# ===============================
if perfil["role"] == "gestor":
    loja_selecionada = perfil["lojas"][0]
    st.info(f"👤 Usuário: {perfil['name']} | Loja {loja_selecionada}")

elif perfil["role"] == "diretor":
    lojas_disponiveis = sorted(
        [d for d in os.listdir(BASE_DIR) if d.isdigit()]
    )

    loja_selecionada = st.selectbox(
        "Selecione a loja",
        lojas_disponiveis
    )

    st.info(f"👤 Usuário: {perfil['name']} | Acesso total")

else:
    st.error("Perfil de usuário inválido")
    st.stop()

# ===============================
# TÍTULO
# ===============================
st.title("📊 Dashboard Executivo — ABCDX, Estoque e Ruptura")
st.caption("Período de análise: 90 dias")

# ===============================


# 🔽 Arquivo mais recente da loja
pasta_loja = os.path.join(BASE_DIR, loja_selecionada)
arquivos = sorted(
    [f for f in os.listdir(pasta_loja) if f.endswith(".parquet")],
    reverse=True
)

arquivos = [
    os.path.join(pasta_loja, f)
    for f in os.listdir(pasta_loja)
    if f.endswith(".parquet")
]

arquivo = max(arquivos, key=os.path.getmtime)
df = pd.read_parquet(arquivo)
df['CMV_POR_DIA_NUM'] = (
    df['CMV_POR_DIA']
    .str.replace('R$', '', regex=False)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
    .astype(float)
)

valor_ruptura = (
        df.loc[df['RUPTURA'] == 1, 'CMV_POR_DIA_NUM']
        .sum()
    )
# 🔝 KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔴 Produtos em ruptura", int(df['RUPTURA'].sum()))
col2.metric(
        "💸 Perda diária estimada",
        f"R$ {valor_ruptura:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
        help="Valor estimado de perda diária considerando produtos em ruptura"
    )
col3.metric("📦 DDE médio atual", round(df['DDE_ATUAL'].mean(), 1))
col4.metric(
    "🎯 % fora do DDE ideal",
    round((df['DDE_ATUAL'] < df['DDE_IDEAL']).mean() * 100, 1)
)
st.divider()

with st.expander("📊 Ver gráficos detalhados"):
    import matplotlib.pyplot as plt

    st.subheader("🔴 Distribuição da Ruptura por ABCDX ((Empresa))")

    ruptura_abc = (
        df[df['RUPTURA'] == 1]
        .groupby('ABCX_EMPRESA')
        .size()
    )

    if not ruptura_abc.empty:
        total = ruptura_abc.sum()

        labels = [
            f"{classe} — {valor / total:.1%}"
            for classe, valor in ruptura_abc.items()
        ]

        fig, ax = plt.subplots()
        wedges, _ = ax.pie(
            ruptura_abc,
            startangle=90
        )

        ax.axis('equal')

        ax.legend(
            wedges,
            labels,
            title="Classe ABCDX",
            loc="center left",
            bbox_to_anchor=(1, 0.5)
        )

        st.pyplot(fig)
    else:
        st.info("Nenhum produto em ruptura para os filtros selecionados.")


    st.subheader("🎯 Produtos dentro x fora do DDE ideal")

    dde_status = pd.Series({
        "Dentro do DDE ideal": (df['DDE_ATUAL'] >= df['DDE_IDEAL']).sum(),
        "Fora do DDE ideal": (df['DDE_ATUAL'] < df['DDE_IDEAL']).sum()
    })

    fig, ax = plt.subplots()
    ax.bar(dde_status.index, dde_status.values)

    ax.set_ylabel("Quantidade de produtos")
    ax.set_xlabel("")
    ax.set_title("Situação de cobertura de estoque")

    for i, v in enumerate(dde_status.values):
        ax.text(i, v, f"{v:,}", ha='center', va='bottom')

    st.pyplot(fig)

st.divider() #divisória visual

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    divisao = st.multiselect(
        "Divisão",
        options=sorted(df['iddivisao'].unique())
    )

with col_f2:
    abcx_empresa = st.multiselect(
        "ABCDX (Empresa)",
        options=sorted(df['ABCX_EMPRESA'].dropna().unique())
    )

with col_f3:
    abcx_subgrupo = st.multiselect(
        "ABCDX (Subgrupo)",
        options=sorted(df['ABCX_SUBGRUPO'].dropna().unique())
    )

# Aplicação dos filtros
if divisao:
    df = df[df['iddivisao'].isin(divisao)]

if abcx_empresa:
    df = df[df['ABCX_EMPRESA'].isin(abcx_empresa)]

if abcx_subgrupo:
    df = df[df['ABCX_SUBGRUPO'].isin(abcx_subgrupo)]

#  Tabela final
st.dataframe(
    df.sort_values('RUPTURA_VALOR', ascending=False),
    use_container_width=True
)
