import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Parquet → Excel",
    layout="centered",
    page_icon="🎲"
)

st.title("📊 Conversor de Parquet para Excel")
st.write("Faça upload de um arquivo **.parquet**, visualize os dados e baixe em **Excel**.")

# Upload do arquivo Parquet
uploaded_file = st.file_uploader(
    "Selecione o arquivo Parquet",
    type=["parquet"]
)

if uploaded_file:
    try:
        # Leitura do Parquet
        df = pd.read_parquet(uploaded_file)

        st.success("Arquivo Parquet carregado com sucesso!")

        # Exibir informações básicas
        st.write("### 🔍 Visualização dos dados")
        st.write(f"Linhas: **{df.shape[0]}** | Colunas: **{df.shape[1]}**")

        st.dataframe(df, use_container_width=True)

        # Converter para Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Dados")

        output.seek(0)

        # Botão de download
        st.download_button(
            label="⬇️ Baixar arquivo Excel",
            data=output,
            file_name="arquivo_convertido.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("Erro ao processar o arquivo Parquet.")
        st.exception(e)
