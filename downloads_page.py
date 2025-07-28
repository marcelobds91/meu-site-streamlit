import streamlit as st
import os

def area_de_downloads():
    st.markdown("## 📥 Área de Downloads")
    st.info("Clique nos botões abaixo para baixar os arquivos disponíveis.")

    pasta = "downloads"

    if not os.path.exists(pasta):
        st.warning("A pasta de downloads não existe.")
        return

    arquivos = os.listdir(pasta)
    arquivos = [f for f in arquivos if os.path.isfile(os.path.join(pasta, f))]

    if arquivos:
        for arquivo in arquivos:
            caminho = os.path.join(pasta, arquivo)
            with open(caminho, "rb") as f:
                conteudo = f.read()
            st.download_button(
                label=f"📎 Baixar {arquivo}",
                data=conteudo,
                file_name=arquivo,
                mime=(
                    "application/pdf" if arquivo.lower().endswith(".pdf")
                    else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    if arquivo.lower().endswith((".xlsx", ".xls"))
                    else "application/octet-stream"
                )
            )
    else:
        st.warning("Nenhum arquivo disponível para download.")
