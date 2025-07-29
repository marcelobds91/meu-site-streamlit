import streamlit as st
import os

TIPOS_ITEM = {
    "00": "Mercadoria para revenda",
    "01": "Matéria-prima",
    "02": "Embalagem",
    "03": "Produto em processo",
    "04": "Produto acabado",
    "05": "Subproduto",
    "06": "Produto intermediário",
    "07": "Material de uso e consumo",
    "08": "Ativo imobilizado",
    "09": "Serviços",
    "10": "Outros insumos",
    "99": "Outras"
}

def alterar_tipo_item_por_cfop():
    st.title("🧾 Alterar Tipo de Item por CFOP no SPED Fiscal")

    uploaded_file = st.file_uploader("📤 Envie o arquivo TXT do SPED Fiscal", type=["txt"])
    if uploaded_file:
        txt_content = uploaded_file.read().decode("latin1")  # ou "cp1252"

        linhas = txt_content.splitlines()

        dict_0200 = {}
        dict_cfop_coditens = {}
        chave_nota = ""

        for linha in linhas:
            if linha.startswith("|0200|"):
                partes = linha.split("|")
                if len(partes) >= 8:
                    cod_item = partes[2]
                    dict_0200[cod_item] = linha

        for linha in linhas:
            if linha.startswith("|C100|"):
                partes = linha.split("|")
                chave_nota = partes[2] + partes[3] + partes[4]
            elif linha.startswith("|C170|"):
                partes = linha.split("|")
                if len(partes) >= 12:
                    cfop = partes[11]
                    cod_item = partes[3]
                    if cfop not in dict_cfop_coditens:
                        dict_cfop_coditens[cfop] = set()
                    dict_cfop_coditens[cfop].add(cod_item)

        st.markdown("### ✅ CFOPs identificados")
        if dict_cfop_coditens:
            tipos_escolhidos = {}
            for cfop in sorted(dict_cfop_coditens.keys()):
                with st.expander(f"CFOP {cfop}"):
                    tipo_novo = st.selectbox(
                        f"Tipo de Item para CFOP {cfop}:",
                        options=[""] + list(TIPOS_ITEM.keys()),
                        format_func=lambda x: f"{x} - {TIPOS_ITEM[x]}" if x in TIPOS_ITEM else "",
                        key=f"cfop_{cfop}"
                    )
                    if tipo_novo:
                        tipos_escolhidos[cfop] = tipo_novo

            if st.button("🔄 Aplicar alterações e gerar arquivo"):
                log_alteracoes = "Alterações realizadas:\n"

                for cfop, tipo_novo in tipos_escolhidos.items():
                    for cod_item in dict_cfop_coditens[cfop]:
                        if cod_item in dict_0200:
                            partes = dict_0200[cod_item].split("|")
                            partes[7] = tipo_novo
                            nova_linha = "|".join(partes)
                            dict_0200[cod_item] = nova_linha
                            log_alteracoes += f"CFOP: {cfop} | CodItem: {cod_item} | Tipo alterado para: {tipo_novo} - {TIPOS_ITEM[tipo_novo]}\n"

                novas_linhas = []
                for linha in linhas:
                    if linha.startswith("|0200|"):
                        partes = linha.split("|")
                        cod_item = partes[2]
                        if cod_item in dict_0200:
                            linha = dict_0200[cod_item]
                    novas_linhas.append(linha)

                novo_arquivo = "\n".join(novas_linhas)
                log_nome = "log_tipo_item.txt"
                txt_nome = "SPED_TIPO_ITEM_ALTERADO.txt"

                st.success("✅ Alterações aplicadas com sucesso!")
                st.download_button("⬇️ Baixar TXT Alterado", data=novo_arquivo, file_name=txt_nome, mime="text/plain")
                st.download_button("📄 Baixar Log das Alterações", data=log_alteracoes, file_name=log_nome, mime="text/plain")
        else:
            st.warning("Nenhum CFOP com C170 encontrado no arquivo enviado.")
