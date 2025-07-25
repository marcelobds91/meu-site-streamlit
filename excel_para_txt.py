import streamlit as st
import pandas as pd

def funcao_excel_para_txt():
    st.markdown("## 📤 Converter Excel para TXT (SPED Fiscal)")

    arquivo_excel = st.file_uploader("Selecione o arquivo Excel (.xlsx):", type=["xlsx"])

    if arquivo_excel is not None:
        st.success("Arquivo carregado com sucesso!")

        nome_arquivo = st.text_input("Nome do arquivo TXT de saída (ex: sped.txt):", value="sped.txt")

        if st.button("Gerar TXT"):
            df = pd.read_excel(arquivo_excel, dtype=str).fillna("")

            # Dicionário com campos que precisam zeros à esquerda para cada registro
            campos_zeros_por_registro = {
                "0000": {
                    "REG": 4,
                    "COD_VER": 3,
                    "COD_FIN": 1,
                    "DT_INI": 8,
                    "DT_FIN": 8,
                    "CNPJ": 14,
                    "CPF": 11,
                    "IE": 14,
                    "COD_MUN": 7,
                    "SUFRAMA": 9,
                    "IND_PERFIL": 1,
                    "IND_ATIV": 1
                },
                "0001": {
                    "REG": 4,
                    "IND_MOV": 1
                },
                "0150": {
                    "REG": 4,
                    "COD_PART": 14,
                    "COD_PAIS": 4,
                    "CNPJ": 14,
                    "CPF": 11,
                    "IE": 14,
                    "COD_MUN": 7,
                    "SUFRAMA": 9
                },
                "0200": {
                    "REG": 4,
                    "COD_ITEM": 60,  # Ajuste conforme seu tamanho máximo esperado
                    "COD_NCM": 8,
                    "CEST": 7
                },
                "C100": {
                    "REG": 4,
                    "IND_OPER": 1,
                    "IND_EMIT": 1,
                    "COD_PART": 14,
                    "COD_MOD": 2,
                    "COD_SIT": 2,
                    "SER": 3,
                    "NUM_DOC": 9,
                    "CHV_NFE": 44,
                    "DT_DOC": 8,
                    "DT_E_S": 8,
                    "IND_PGTO": 1,
                    # ... outros campos se desejar
                },
                "C170": {
                    "REG": 4,
                    "NUM_ITEM": 3,
                    "COD_ITEM": 60,
                    "UNID": 6,
                    "CST_ICMS": 3,
                    "CFOP": 4,
                    "CST_IPI": 3,
                    "CST_PIS": 3,
                    "CST_COFINS": 3,
                    # ... outros campos se desejar
                },
                # Continue para outros registros se desejar...
            }

            def preencher_zeros(valor, tamanho):
                valor = valor.strip()
                return valor.zfill(tamanho)

            linhas = []
            for _, row in df.iterrows():
                reg = row.get("REG", "").strip()
                campos_zeros = campos_zeros_por_registro.get(reg, {})

                campos = []
                for col in df.columns:
                    val = str(row[col]).strip()
                    if col in campos_zeros:
                        val = preencher_zeros(val, campos_zeros[col])
                    campos.append(val)
                linha = "|" + "|".join(campos) + "|"
                linhas.append(linha)

            conteudo_txt = "\n".join(linhas)

            st.download_button(
                label="📥 Baixar TXT Gerado",
                data=conteudo_txt,
                file_name=nome_arquivo,
                mime="text/plain"
            )
    else:
        st.info("📁 Nenhum arquivo foi selecionado ainda.")
