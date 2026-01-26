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
        "gestor um": {
            "name": "Gestor Loja 1",
            "password": '$2b$12$jgw50OJxyvrl.bTWXJHxKOVuyUMZCK6ibrcDXrYE3eLXgmpXEx6O2', #gestor@123
            "role": "gestor",
            "lojas": ["1"]
        },
        "diretoria": {
            "name": "Diretor Geral",
            "password": "$2b$12$wcWIGSeo8Bsrc8q4dF9fCODJncEhEYuD84MToAbXM9a1sEkVNMxnK", #diretor@123
            "role": "diretor",
            "lojas": []
        }
    }
}

# ===============================
# ===============================
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
