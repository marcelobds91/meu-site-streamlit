import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import re

def extrair_chave_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}

        # Tenta achar infNFe (NF-e)
        infNFe = root.find(".//ns:infNFe", ns) if ns else root.find(".//infNFe")
        if infNFe is not None:
            chave = infNFe.attrib.get("Id", "")[-44:]
            tipo = "NF-e"
        else:
            # Tenta achar infCte (CT-e)
            infCte = root.find(".//ns:infCte", ns) if ns else root.find(".//infCte")
            if infCte is not None:
                chave = infCte.attrib.get("Id", "")[-44:]
                tipo = "CT-e"
            else:
                chave = ""
                tipo = "Desconhecido"
        return {"chave": re.sub(r'\D', '', chave), "tipo": tipo}
    except Exception:
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
    st.markdown("""
🔍 **Descrição:**  
Este módulo realiza a **conferência entre o SPED Fiscal (TXT)** e os **arquivos XML de NF-e e CT-e**, 
verificando divergências nas **chaves das notas fiscais**.
""")
    txt_file = st.file_uploader("📄 Carregue o arquivo TXT do SPED Fiscal", type=["txt"])
    xml_files = st.file_uploader("📂 Carregue os arquivos XML de NF-e e CT-e", type=["xml"], accept_multiple_files=True)

    if txt_file and xml_files:
        # Leitura do conteúdo do TXT
        conteudo_txt = txt_file.read().decode("utf-8", errors="ignore")
        chaves_txt = extrair_chaves_txt_sped(conteudo_txt)
        chaves_txt_set = set(chaves_txt)

        registros_xml = []
        for xml in xml_files:
            info = extrair_chave_xml(xml)
            if info["chave"]:
                registros_xml.append(info)

        df_xml = pd.DataFrame(registros_xml).drop_duplicates()
        chaves_xml_set = set(df_xml["chave"])

        # Diferenças entre chaves
        chaves_somente_no_txt = chaves_txt_set - chaves_xml_set
        chaves_somente_no_xml = chaves_xml_set - chaves_txt_set

        df_faltando_no_xml = pd.DataFrame(
            [{"chave": chave, "origem": "SPED TXT", "tipo": "NF-e ou CT-e"} for chave in chaves_somente_no_txt]
        )
        df_faltando_no_txt = df_xml[df_xml["chave"].isin(chaves_somente_no_xml)].copy()
        df_faltando_no_txt["origem"] = "XML"

        df_final = pd.concat([df_faltando_no_xml, df_faltando_no_txt], ignore_index=True)

        st.success("✅ Comparação realizada com sucesso!")

        # Botão para download do relatório Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_final.to_excel(writer, sheet_name="Divergências", index=False)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Baixar Relatório de Divergências",
            data=buffer,
            file_name="relatorio_chaves_diferenca.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )