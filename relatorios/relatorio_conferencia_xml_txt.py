import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import re

def extrair_chave_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        ns = {'ns': root.tag.split('}')[0].strip('{')}
        
        # Tenta identificar se é NF-e ou CT-e
        if root.tag.endswith("NFe") or root.find(".//ns:infNFe", ns) is not None:
            tipo = "NF-e"
            chave = root.find(".//ns:infNFe", ns).attrib.get("Id", "")[-44:]
        elif root.tag.endswith("CTe") or root.find(".//ns:infCte", ns) is not None:
            tipo = "CT-e"
            chave = root.find(".//ns:infCte", ns).attrib.get("Id", "")[-44:]
        else:
            tipo = "Desconhecido"
            chave = ""
        return {"chave": re.sub(r'\D', '', chave), "tipo": tipo}
    except Exception as e:
        return {"chave": "", "tipo": "Erro"}

def extrair_chaves_txt_sped(conteudo_txt):
    chaves = []
    for linha in conteudo_txt.splitlines():
        if linha.startswith("|C100|"):
            campos = linha.split("|")
            if len(campos) >= 10:
                chave = re.sub(r'\D', '', campos[8])  # campo 9 = chave, índice 8
                if len(chave) == 44:
                    chaves.append(chave)
    return chaves

def relatorio_conferencia_xml_txt():
    st.subheader("Conferência de Chaves NF-e / CT-e entre XML e TXT")

    txt_file = st.file_uploader("📄 Carregue o arquivo TXT do SPED Fiscal", type=["txt"])
    xml_files = st.file_uploader("📂 Carregue os arquivos XML de NF-e e CT-e", type=["xml"], accept_multiple_files=True)

    if txt_file and xml_files:
        # Leitura do TXT
        conteudo_txt = txt_file.read().decode("utf-8", errors="ignore")
        chaves_txt = extrair_chaves_txt_sped(conteudo_txt)
        chaves_txt_set = set(chaves_txt)

        # Leitura dos XMLs
        registros_xml = []
        for xml in xml_files:
            info = extrair_chave_xml(xml)
            if info["chave"]:
                registros_xml.append(info)

        df_xml = pd.DataFrame(registros_xml).drop_duplicates()
        chaves_xml_set = set(df_xml["chave"])

        # Diferenças
        chaves_somente_no_txt = chaves_txt_set - chaves_xml_set
        chaves_somente_no_xml = chaves_xml_set - chaves_txt_set

        df_faltando_no_xml = pd.DataFrame(
            [{"chave": chave, "origem": "SPED TXT", "tipo": "NF-e ou CT-e"} for chave in chaves_somente_no_txt]
        )

        df_faltando_no_txt = df_xml[df_xml["chave"].isin(chaves_somente_no_xml)].copy()
        df_faltando_no_txt["origem"] = "XML"

        df_final = pd.concat([df_faltando_no_xml, df_faltando_no_txt], ignore_index=True)

        st.success("✅ Comparação realizada com sucesso!")

        # Exibir botão para download
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_final.to_excel(writer, sheet_name="Divergências", index=False)
        st.download_button(
            label="⬇️ Baixar Relatório de Divergências",
            data=buffer.getvalue(),
            file_name="relatorio_chaves_diferenca.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )




