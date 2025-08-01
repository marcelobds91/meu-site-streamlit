import pandas as pd
import io
import xlsxwriter
import streamlit as st  # <-- FALTAVA ESTA LINHA


dict_cabecalhos = {
    "0000": ["REG", "COD_VER", "COD_FIN", "DT_INI", "DT_FIN", "NOME", "CNPJ", "CPF", "UF", "IE", "COD_MUN", "IM", "SUFRAMA", "IND_PERFIL", "IND_ATIV"],
    "0001": ["REG", "IND_MOV"],
    "0002": ["REG", "CLAS_ESTAB_IND"],
    "0005": ["REG", "FANTASIA", "CEP", "END", "NUM", "COMPL", "BAIRRO", "FONE", "FAX", "EMAIL", "COD_MUN"],
    "0015": ["REG", "UF_ST", "IE_ST"],
    "0100": ["REG", "NOME", "CPF", "CRC", "CNPJ", "CEP", "END", "NUM", "COMPL", "BAIRRO", "FONE", "FAX", "EMAIL", "COD_MUN"],
    "0110": ["REG", "COD_INC_TRIB", "IND_APRO_CRED", "COD_TIPO_CONT", "IND_REG_CUM"],
    "0150": ["REG", "COD_PART", "NOME", "COD_PAIS", "CNPJ", "CPF", "IE", "COD_MUN", "SUFRAMA", "END", "NUM", "COMPL", "BAIRRO"],
    "0175": ["REG", "DT_ALT", "NR_CAMPO", "CONT_ANT"],
    "0190": ["REG", "UNID", "DESCR"],
    "0200": ["REG", "COD_ITEM", "DESCR_ITEM", "COD_BARRA", "COD_ANT_ITEM", "UNID_INV", "TIPO_ITEM", "COD_NCM", "EX_IPI", "COD_GEN", "COD_LST", "ALIQ_ICMS", "CEST"],
    "0205": ["REG", "DESCR_ANT_ITEM", "DT_INI", "DT_FIM", "COD_ANT_ITEM"],
    "0206": ["REG", "COD_COMB"],
    "0210": ["REG", "COD_ITEM_COMP", "QTD_COMP", "PERDA", "IND_PROC", "TP_ITEM", "COD_INS_SUBST"],
    "0220": ["REG", "UNID_CONV", "FAT_CONV", "VL_UNID_CONV"],
    "0300": ["REG", "COD_IND_BEM", "IDENT_MERC", "DESCR_ITEM", "COD_PRNC", "COD_CTA", "NR_PARC"],
    "0305": ["REG", "COD_CCUS", "FUNC", "VIDA_UTIL"],
    "0500": ["REG", "DT_ALT", "COD_NAT_CC", "IND_CTA", "NIVEL", "COD_CTA", "NOME_CTA"],
    "0600": ["REG", "DT_ALT", "COD_CCUS", "CCUS"],

    "C001": ["REG", "IND_MOV"],
    "C100": ["REG", "IND_OPER", "IND_EMIT", "COD_PART", "COD_MOD", "COD_SIT", "SER", "NUM_DOC", "CHV_NFE", "DT_DOC", "DT_E_S", "VL_DOC", "IND_PGTO", "VL_DESC", "VL_ABAT_NT", "VL_MERC", "IND_FRT", "VL_FRT", "VL_SEG", "VL_OUT_DA", "VL_ICMS", "VL_ICMS_ST", "VL_IPI", "VL_PIS", "VL_COFINS", "VL_PIS_ST", "VL_COFINS_ST"],
    "C101": ["REG", "VL_FCP_UF_DEST", "VL_ICMS_UF_DEST", "VL_ICMS_UF_REM"],
    "C105": ["REG", "OPER", "UF"],
    "C110": ["REG", "COD_INF", "TXT_COMPL"],
    "C111": ["REG", "NUM_PROC", "IND_PROC"],
    "C112": ["REG", "COD_DA","UF", "NUM_DA", "COD_AUT", "VL_DA", "DT_VCTO", "DT_PGTO"],
    "C170": ["REG", "NUM_ITEM", "COD_ITEM", "DESCR_COMPL", "QTD", "UNID", "VL_ITEM", "VL_DESC", "IND_MOV", "CST_ICMS", "CFOP", "COD_NAT", "VL_BC_ICMS", "ALIQ_ICMS", "VL_ICMS", "VL_BC_ICMS_ST", "ALIQ_ST", "VL_ICMS_ST", "IND_APUR", "CST_IPI", "COD_ENQ", "VL_BC_IPI", "ALIQ_IPI", "VL_IPI", "CST_PIS", "VL_BC_PIS", "ALIQ_PIS_PERC", "QUANT_BC_PIS", "ALIQ_PIS_REAIS", "VL_PIS", "CST_COFINS", "VL_BC_COFINS", "ALIQ_COFINS_PERC", "QUANT_BC_COFINS", "ALIQ_COFINS_REAIS", "VL_COFINS", "COD_CTA"],
    "C190": ["REG", "CST_ICMS", "CFOP", "ALIQ_ICMS", "VL_OPR", "VL_BC_ICMS", "VL_ICMS", "VL_BC_ICMS_ST", "VL_ICMS_ST", "VL_RED_BC", "COD_OBS"],

    "D100": ["REG", "IND_OPER", "IND_EMIT", "COD_PART", "COD_MOD", "COD_SIT", "SER", "SUB", "NUM_DOC", "CHV_CTE", "DT_DOC", "DT_A_P", "VL_DOC", "VL_DESC", "IND_FRT", "VL_SERV", "VL_BC_ICMS", "VL_ICMS", "COD_INF", "COD_CTA", "TP_ASSINANTE"],
    "D190": ["REG", "CST_ICMS", "CFOP", "ALIQ_ICMS", "VL_OPR", "VL_BC_ICMS", "VL_ICMS", "VL_RED_BC", "COD_OBS"],

    "E100": ["REG", "DT_INI", "DT_FIN"],
    "E110": ["REG", "VL_TOT_DEBITOS", "VL_AJ_DEBITOS", "VL_TOT_AJ_DEBITOS", "VL_ESTORNOS_DEBITOS", "VL_TOT_CREDITOS", "VL_AJ_CREDITOS", "VL_TOT_AJ_CREDITOS", "VL_ESTORNOS_CREDITOS", "VL_SLD_CREDOR_ANT", "VL_SLD_APURADO", "VL_TOT_DED", "VL_ICMS_RECOLHER", "VL_SLD_CREDOR_TRANSPORTAR", "DEB_ESP"],
    "E116": ["REG", "COD_OR", "VL_OR", "DT_VCTO", "COD_REC", "NUM_PROC", "IND_PROC", "PROC", "TXT_COMPL", "MES_REF"],

    "G001": ["REG", "IND_MOV"],
    "G110": ["REG", "DT_INI", "DT_FIN", "SALDO_IN_ICMS", "SOM_PARC", "VL_TRIB_EXP", "VL_TOTAL", "IND_PER_SAI", "VL_CRED_PIS", "VL_CRED_COFINS", "VL_CRED_ICMS", "DESC_CRED", "VL_DESC", "VL_OUT_DED"],
    "G125": ["REG", "COD_IND_BEM", "DT_MOV", "TIPO_MOV", "VL_IMOB_ICMS_OP", "VL_IMOB_ICMS_ST", "VL_IMOB_ICMS_FRT", "VL_IMOB_ICMS_DIF", "NUM_PARC", "VL_PARC_PASS", "VL_ICMS_APUR"],
    "G130": ["REG", "IND_EMIT", "COD_PART", "COD_MOD", "SERIE", "NUM_DOC", "CHV_NFE_CTE", "DT_DOC", "VL_DOC", "VL_DESC", "VL_ICMS_OP", "VL_ICMS_ST", "VL_ICMS_FRT", "VL_ICMS_DIF", "NUM_PARC", "VL_PARC"],
    "G140": ["REG", "NUM_ITEM", "COD_ITEM", "VL_ICMS_OP_APROP", "VL_ICMS_ST_APROP", "VL_ICMS_FRT_APROP", "VL_ICMS_DIF_APROP"],

    "H001": ["REG", "IND_MOV"],
    "H005": ["REG", "DT_INV", "VL_INV", "MOT_INV"],
    "H010": ["REG", "COD_ITEM", "UNID", "QTD", "VL_UNIT", "VL_ITEM", "IND_PROP", "COD_PART", "TXT_COMPL", "COD_CTA", "VL_ITEM_IR"],

    "K100": ["REG", "DT_INI", "DT_FIN"],
    "K200": ["REG", "DT_EST", "COD_ITEM", "QTD", "IND_EST", "COD_PART"],
    "K210": ["REG", "DT_INI_OP", "DT_FIN_OP", "COD_DOC_OP", "COD_ITEM", "QTD_ENC"],
    "K215": ["REG", "COD_ITEM_COMP", "QTD_COMP", "PERDA"],
    "K220": ["REG", "REG_CAMP", "COD_ITEM", "QTD", "UNID", "VL_UNIT"],
    "K230": ["REG", "DT_INI_OP", "DT_FIN_OP", "COD_DOC_OP", "COD_ITEM", "QTD_ENC"],
    "K235": ["REG", "COD_ITEM_COMP", "QTD_COMP", "PERDA"],
    "K250": ["REG", "DT_PROD", "COD_ITEM", "QTD", "UNID", "VL_UNIT"],

    "1010": ["REG", "IND_EXP", "IND_CCRF", "IND_COMB", "IND_USINA", "IND_VA", "IND_EE", "IND_CART", "IND_FORM", "IND_AER", "IND_GIAF1", "IND_GIAF3", "IND_RED", "COD_RED"],
    "1100": ["REG", "IND_DOC", "NRO_DECLA", "DT_DECLA", "NRO_PROTO", "IND_PROC", "PROC", "COD_INF"],
    "1105": ["REG", "COD_INF", "TXT_COMPL"],
    "1150": ["REG", "COD_INF", "VL_INF"],
    "1160": ["REG", "COD_INF", "QTD"],
    "1200": ["REG", "SINAL", "COD_INF", "NUM_DA", "VL_AJ", "COD_CTA", "DESC_AJ"],
    "1210": ["REG", "TIPO_UTIL", "NR_DOC", "DT_UTIL", "VL_CRED_UTIL"],
    "1250": ["REG", "COD_INFORMACAO", "DT_VCTO", "VL_INFORMACAO", "IND_OPER", "NR_DOCUMENTO"],
    "1300": ["REG", "COD_ITEM", "DT_FECH", "ESTQ_ABERT", "VL_UNI", "ENT_QTD", "SAI_QTD", "ESTQ_ESCR", "VAL_AJ_PERDA", "VAL_AJ_GANHO", "FECH_QTD"],
    "1310": ["REG", "NUM_TANQUE", "ESTQ_ABERT", "ENT_QTD", "SAI_QTD", "ESTQ_ESCR", "FECH_QTD"],
    "1320": ["REG", "NUM_BICO", "QTD_AFER", "QTD_VENDAS"],

    "9001": ["REG", "IND_MOV"],
    "9900": ["REG", "REG_BLC", "QTD_REG_BLC"],
    "9990": ["REG", "QTD_LIN_9"],
    "9999": ["REG", "QTD_LIN"]
}

# Título e upload
st.title("📥 Importador de SPED Fiscal para Excel")
uploaded_file = st.file_uploader("Selecione o arquivo SPED (.txt)", type=["txt"])


# Opção do tipo de exportação (sempre visível)
exportar_tudo = st.radio(
    "O que deseja exportar?",
    ["🔹 Somente os registros encontrados no arquivo", "🔸 Todos os registros com estrutura completa"],
    index=1
)

# ✅ Transformar em booleano (sempre, fora do IF)
exportar_todos = exportar_tudo == "🔸 Todos os registros com estrutura completa"

# Função principal
def importar_sped_para_excel(uploaded_file, exportar_todos):
    try:
        linhas = uploaded_file.read().decode('utf-8').splitlines()
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        linhas = uploaded_file.read().decode('latin1').splitlines()

    registros = {}
    for linha in linhas:
        partes = linha.strip().split("|")
        if len(partes) > 1 and partes[1]:
            reg = partes[1]
            if reg not in registros:
                registros[reg] = []
            registros[reg].append(partes[1:-1])  # remove o primeiro e o último campo vazio

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for reg in dict_cabecalhos:
            if not exportar_todos and reg not in registros:
                continue

            colunas = dict_cabecalhos[reg]
            linhas_reg = registros.get(reg, [])

            df_reg = pd.DataFrame(linhas_reg)

            if df_reg.shape[1] < len(colunas):
                for _ in range(len(colunas) - df_reg.shape[1]):
                    df_reg[df_reg.shape[1]] = None
            df_reg = df_reg.iloc[:, :len(colunas)]
            df_reg.columns = colunas

            df_reg.to_excel(writer, sheet_name=f"REG_{reg}", index=False)

    output.seek(0)
    return output


# Processamento e botão de download
if uploaded_file:
    excel_file = importar_sped_para_excel(uploaded_file, exportar_todos)

    st.success("✅ Arquivo processado com sucesso!")
    st.download_button(
        label="📤 Baixar Excel Gerado",
        data=excel_file,
        file_name="sped_convertido.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )