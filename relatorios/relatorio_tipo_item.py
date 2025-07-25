import streamlit as st
import io
import pandas as pd

def relatorio_tipo_item():

    st.markdown("""
    <h2 style="font-size:28px; margin-bottom: 0;">📌 Relatório Tipo Item</h2>
""", unsafe_allow_html=True)

    st.markdown("""
    🧾 **Descrição:**  
    Este módulo gera um relatório com os **tipos de itens (registro 0200)** vinculados às operações fiscais no SPED Fiscal, 
    com base nos **CFOPs dos registros C170**.  
    Permite identificar e alterar a classificação dos itens conforme a natureza da operação (venda, revenda, uso, consumo etc.).
    """)
    
    st.markdown("""---""")

    st.markdown("""
    📂 **Arraste e solte seu arquivo TXT do SPED Fiscal aqui**  
    ou clique no botão abaixo para selecionar o arquivo.  
    **Tamanho máximo:** 200MB  
    **Formato permitido:** .txt
    """)

    uploaded_file = st.file_uploader(label="", type=["txt"])


    if uploaded_file is not None:
        try:
            linhas = uploaded_file.read().decode("latin1").splitlines()
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return

        def parse_float(valor):
            try:
                return float(str(valor).replace(",", "."))
            except:
                return 0.0

        map_itens = {}
        map_notas = {}
        chave_atual = ""
        dados_consolidados = []

        for linha in linhas:
            partes = linha.strip().split("|")

            if len(partes) < 2:
                continue

            if partes[1] == "0200" and len(partes) >= 9:
                cod_item = partes[2]
                desc_item = partes[3]
                cod_tipo = partes[7]
                ncm_item = partes[8]

                tipo_item = {
                    "00": "Mercadoria para Revenda",
                    "01": "Matéria-prima",
                    "02": "Embalagem",
                    "03": "Produto em Processo",
                    "04": "Produto Acabado",
                    "05": "Subproduto",
                    "06": "Produto Intermediário",
                    "07": "Material de Uso e Consumo",
                    "08": "Ativo Imobilizado",
                    "09": "Serviços",
                    "10": "Outros insumos",
                    "99": "Outras"
                }.get(cod_tipo, f"Desconhecido ({cod_tipo})")

                map_itens[cod_item] = (desc_item, tipo_item, ncm_item)

            elif partes[1] == "C100" and len(partes) >= 12:
                num_nota = partes[8]
                chave = partes[9]
                data_entrada = partes[11]
                chave_atual = chave
                map_notas[chave] = (num_nota, data_entrada)

            elif partes[1] == "C170" and len(partes) >= 16:
                cod_item = partes[3]
                valor_item = partes[7]
                cst = partes[10]
                cfop = partes[11]
                bc_icms = partes[13]
                aliq_icms = partes[14]
                valor_icms = partes[15]

                num_nota, data_entrada = map_notas.get(chave_atual, ("", ""))
                desc_item, tipo_item, ncm_item = map_itens.get(cod_item, ("", "", ""))

                dados_consolidados.append({
                    "Chave da Nota": chave_atual,
                    "Número da Nota": num_nota,
                    "Data da Entrada": data_entrada,
                    "Código do Item": cod_item,
                    "Descrição do Item": desc_item,
                    "NCM": ncm_item,
                    "Tipo do Item": tipo_item,
                    "CFOP": cfop,
                    "CST": cst,
                    "Valor do Item": parse_float(valor_item),
                    "BC ICMS": parse_float(bc_icms),
                    "Alíquota ICMS": parse_float(aliq_icms) / 100,
                    "Valor ICMS": parse_float(valor_icms)
                })

        if not dados_consolidados:
            st.warning("Nenhum dado encontrado nos registros 0200, C100 e C170.")
        else:
            df = pd.DataFrame(dados_consolidados)

            st.success("Relatório gerado com sucesso!")
            

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Tipo de Item")
                worksheet = writer.sheets["Tipo de Item"]
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
            output.seek(0)

            st.download_button(
                label="📥 Baixar Relatório Excel",
                data=output,
                file_name="relatorio_tipo_item.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
