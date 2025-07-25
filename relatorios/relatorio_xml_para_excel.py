import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import zipfile

def relatorio_xml_para_excel():
    st.subheader("Conversor XML para Excel (NF-e e CT-e)")
    arquivos = st.file_uploader("Faça upload de arquivos XML ou ZIP:", type=["xml", "zip"], accept_multiple_files=True)

    campos_nfe = [
        "Número NF", "Série", "Data", "Emitente", "CNPJ Emitente",
        "Destinatário", "CNPJ Destinatário", "UF Destino", "NCM", "CFOP",
        "CST", "Base ICMS", "Alíquota ICMS", "Valor ICMS",
        "Valor Unitário", "Valor Total Item", "Valor Total NF-e"
    ]

    campos_cte = [
        "Chave", "Número", "Série", "Data", "Remetente", "Destinatário", "Valor Frete"
    ]

    tab_nfe, tab_cte = st.tabs(["Campos NF-e", "Campos CT-e"])

    with tab_nfe:
        selecionar_tudo_nfe = st.checkbox("Selecionar todos os campos NF-e", key="sel_tudo_nfe")
        if selecionar_tudo_nfe:
            campos_selecionados_nfe = st.multiselect(
                "Escolha os campos que deseja exportar para o Excel (NF-e):",
                options=campos_nfe,
                default=campos_nfe,
                key="mult_nfe"
            )
        else:
            campos_selecionados_nfe = st.multiselect(
                "Escolha os campos que deseja exportar para o Excel (NF-e):",
                options=campos_nfe,
                key="mult_nfe"
            )

    with tab_cte:
        selecionar_tudo_cte = st.checkbox("Selecionar todos os campos CT-e", key="sel_tudo_cte")
        if selecionar_tudo_cte:
            campos_selecionados_cte = st.multiselect(
                "Escolha os campos que deseja exportar para o Excel (CT-e):",
                options=campos_cte,
                default=campos_cte,
                key="mult_cte"
            )
        else:
            campos_selecionados_cte = st.multiselect(
                "Escolha os campos que deseja exportar para o Excel (CT-e):",
                options=campos_cte,
                key="mult_cte"
            )

    if st.button("Processar arquivos"):

        if not arquivos:
            st.warning("Por favor, faça upload dos arquivos XML ou ZIP.")
            return

        if not campos_selecionados_nfe and not campos_selecionados_cte:
            st.warning("Selecione pelo menos um campo para NF-e ou CT-e.")
            return

        dados_nfe = []
        dados_cte = []
        chaves_processadas = set()

        for arq in arquivos:
            if arq.name.endswith(".zip"):
                with zipfile.ZipFile(arq, "r") as zip_ref:
                    for nome_arquivo in zip_ref.namelist():
                        if nome_arquivo.endswith(".xml"):
                            with zip_ref.open(nome_arquivo) as file:
                                processar_xml(file, dados_nfe, dados_cte, chaves_processadas)
            else:
                processar_xml(arq, dados_nfe, dados_cte, chaves_processadas)

        if dados_nfe:
            df_nfe = pd.DataFrame(dados_nfe)
            if campos_selecionados_nfe:
                df_nfe = df_nfe[campos_selecionados_nfe]
        else:
            df_nfe = pd.DataFrame()

        if dados_cte:
            df_cte = pd.DataFrame(dados_cte)
            if campos_selecionados_cte:
                df_cte = df_cte[campos_selecionados_cte]
        else:
            df_cte = pd.DataFrame()

        if df_nfe.empty and df_cte.empty:
            st.warning("Nenhum dado foi encontrado para exportar.")
            return

        with pd.ExcelWriter("xml_convertido.xlsx", engine="xlsxwriter") as writer:
            if not df_nfe.empty:
                df_nfe.to_excel(writer, sheet_name="NF-e", index=False)
            if not df_cte.empty:
                df_cte.to_excel(writer, sheet_name="CT-e", index=False)

        with open("xml_convertido.xlsx", "rb") as f:
            st.download_button("📥 Baixar Excel", f, file_name="xml_convertido.xlsx")


def processar_xml(file, dados_nfe, dados_cte, chaves_processadas):
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        if root.tag == "NFe" or root.find("NFe") is not None:
            nfe = root.find("NFe") if root.find("NFe") is not None else root
            infNFe = nfe.find("infNFe")
            chave = infNFe.attrib.get("Id", "").replace("NFe", "")

            if chave in chaves_processadas:
                return
            chaves_processadas.add(chave)

            ide = infNFe.find("ide")
            emit = infNFe.find("emit")
            dest = infNFe.find("dest")
            total = infNFe.find("total")
            ICMSTot = total.find("ICMSTot") if total is not None else None

            numero = ide.findtext("nNF", "")
            serie = ide.findtext("serie", "")
            data_emissao = ide.findtext("dhEmi", "")[:10] or ide.findtext("dEmi", "")
            nome_emit = emit.findtext("xNome", "")
            cnpj_emit = emit.findtext("CNPJ", "")
            nome_dest = dest.findtext("xNome", "") if dest is not None else ""
            cnpj_dest = dest.findtext("CNPJ", "") if dest is not None else ""
            uf_dest = dest.findtext("enderDest/UF", "") if dest is not None else ""

            total_nota = ICMSTot.findtext("vNF", "") if ICMSTot is not None else ""

            produtos = infNFe.findall("det")
            total_itens = len(produtos)
            for i, det in enumerate(produtos):
                prod = det.find("prod")
                imposto = det.find("imposto")

                ncm = prod.findtext("NCM", "")
                cfop = prod.findtext("CFOP", "")
                valor_unitario = prod.findtext("vUnCom", "")
                valor_total_item = prod.findtext("vProd", "")
                cst = ""
                base_icms = ""
                aliquota_icms = ""
                valor_icms = ""

                icms = imposto.find("ICMS") if imposto is not None else None
                if icms is not None and list(icms):
                    icms_tipo = list(icms)[0]
                    cst = icms_tipo.findtext("CST", "")
                    base_icms = icms_tipo.findtext("vBC", "")
                    aliquota_icms = icms_tipo.findtext("pICMS", "")
                    valor_icms = icms_tipo.findtext("vICMS", "")

                linha = {
                    "Número NF": numero,
                    "Série": serie,
                    "Data": data_emissao,
                    "Emitente": nome_emit,
                    "CNPJ Emitente": cnpj_emit,
                    "Destinatário": nome_dest,
                    "CNPJ Destinatário": cnpj_dest,
                    "UF Destino": uf_dest,
                    "NCM": ncm,
                    "CFOP": cfop,
                    "CST": cst,
                    "Base ICMS": base_icms,
                    "Alíquota ICMS": aliquota_icms,
                    "Valor ICMS": valor_icms,
                    "Valor Unitário": valor_unitario,
                    "Valor Total Item": valor_total_item,
                    "Valor Total NF-e": total_nota if i == total_itens - 1 else ""
                }

                dados_nfe.append(linha)

        elif root.tag == "CTe" or root.find("CTe") is not None:
            cte = root.find("CTe") if root.find("CTe") is not None else root
            infCte = cte.find("infCte")
            chave = infCte.attrib.get("Id", "").replace("CTe", "")

            if chave in chaves_processadas:
                return
            chaves_processadas.add(chave)

            ide = infCte.find("ide")
            remet = infCte.find("rem")
            dest = infCte.find("dest")
            vPrest = infCte.find("vPrest")

            numero = ide.findtext("nCT", "")
            serie = ide.findtext("serie", "")
            data = ide.findtext("dhEmi", "")[:10]
            nome_remet = remet.findtext("xNome", "")
            nome_dest = dest.findtext("xNome", "")
            valor_frete = vPrest.findtext("vTPrest", "") if vPrest is not None else ""

            dados_cte.append({
                "Chave": chave,
                "Número": numero,
                "Série": serie,
                "Data": data,
                "Remetente": nome_remet,
                "Destinatário": nome_dest,
                "Valor Frete": valor_frete
            })

    except Exception as e:
        st.warning(f"Erro ao processar XML: {e}")
