import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import re

def extrair_chave_xml(xml_file):
    """Extrai a chave da NF-e ou CT-e de um arquivo XML."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}

        infNFe = root.find(".//ns:infNFe", ns) if ns else root.find(".//infNFe")
        if infNFe is not None:
            chave = infNFe.attrib.get("Id", "")[-44:]
            tipo = "NF-e"
        else:
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
    """Extrai todas as chaves do registro C100 campo 09 (índice 8) do SPED."""
    chaves = []
    for linha in conteudo_txt.splitlines():
        if linha.startswith("|C100|"):
            campos = linha.split("|")
            if len(campos) >= 10:
                chave = re.sub(r'\D', '', campos[8])
                if len(chave) == 44:
                    chaves.append(chave)
    return chaves

def relatorio_conferencia_xml_txt():
    st.markdown("""
🔍 **Descrição:**  
Este módulo realiza a conferência entre o SPED Fiscal (registro C100 - campo 09) e os arquivos XML de NF-e e CT-e, 
mostrando as chaves que aparecem em um e não no outro.
""")
    
    txt_file = st.file_uploader("📄 Carregue o arquivo TXT do SPED Fiscal", type=["txt"])
    xml_files = st.file_uploader("📂 Carregue os arquivos XML de NF-e e CT-e", type=["xml"], accept_multiple_files=True)

    if txt_file and xml_files:
        # Leitura do conteúdo TXT
        conteudo_txt = txt_file.read().decode("utf-8", errors="ignore")
        chaves_txt = extrair_chaves_txt_sped(conteudo_txt)
        set_txt = set(chaves_txt)

        # Extração das chaves dos XMLs
        registros_xml = []
        for xml in xml_files:
            info = extrair_chave_xml(xml)
            if info["chave"]:
                registros_xml.append(info)

        df_xml = pd.DataFrame(registros_xml).drop_duplicates()
        set_xml = set(df_xml["chave"])

        # União das chaves para comparação geral
        todas_chaves = sorted(set_txt.union(set_xml))

        # Montar relatório lado a lado
        relatorio = []
        for chave in todas_chaves:
            tem_no_xml = chave in set_xml
            tem_no_txt = chave in set_txt

            if tem_no_xml:
                tipo = df_xml[df_xml["chave"] == chave]["tipo"].values[0]
            else:
                tipo = "Desconhecido"

            if tem_no_xml and tem_no_txt:
                status = "OK"
            elif tem_no_xml and not tem_no_txt:
                status = "Somente no XML"
            elif not tem_no_xml and tem_no_txt:
                status = "Somente no TXT"
            else:
                status = "Erro"

            relatorio.append({
                "CHAVE": chave,
                "TIPO": tipo,
                "TEM NO XML": "✅" if tem_no_xml else "❌",
                "TEM NO TXT": "✅" if tem_no_txt else "❌",
                "STATUS": status
            })

        df_relatorio = pd.DataFrame(relatorio)

        st.success("✅ Comparação realizada com sucesso!")
        if st.checkbox("👁️ Visualizar relatório na tela antes do download"):
            st.dataframe(df_relatorio)
        # Gera Excel para download
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_relatorio.to_excel(writer, sheet_name="Conferencia_XML_vs_TXT", index=False)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Baixar Relatório Excel",
            data=buffer,
            file_name="relatorio_conferencia_xml_txt.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
