import streamlit as st
# from login_utils import login_form, cadastro_form, logout  # Desative temporariamente
from relatorios.relatorio_tipo_item import relatorio_tipo_item
from importar_sped import importar_sped_para_excel  # CORRETO: importa a função do arquivo importar_sped.py
from relatorios.relatorio_conferencia_xml_txt import relatorio_conferencia_xml_txt
from relatorios.relatorio_xml_para_excel import relatorio_xml_para_excel
from excel_para_txt import funcao_excel_para_txt


st.set_page_config(page_title="Automações Fiscais", layout="centered")

menu = st.sidebar.selectbox("Menu", ["🏠 Início", "📂 Importar SPED", "📤 Excel para TXT", "📊 Relatórios"])

if menu == "🏠 Início":
    st.title("Bem-vindo ao Projeto Automação Fiscal")
    st.markdown("""
    <div style="font-size:14px; line-height:1.4;">
    <h3>Origem da Ideia</h3>
    <p>A ideia deste projeto nasceu da necessidade de otimizar as rotinas fiscais que enfrentamos diariamente.<br>
    Durante o trabalho com SPED Fiscal e documentos eletrônicos, percebemos que muitos processos são manuais, repetitivos e sujeitos a erros.</p>

    <h3>Necessidades Encontradas</h3>
    <ul>
        <li>Importação e análise rápida dos arquivos SPED e XML de notas fiscais.</li>
        <li>Consolidação dos dados para facilitar a conferência e geração de relatórios.</li>
        <li>Automação de processos para diminuir o tempo gasto e aumentar a confiabilidade.</li>
    </ul>

    <h3>Obstáculos a Vencer</h3>
    <ul>
        <li>Grande volume de dados e complexidade dos arquivos fiscais.</li>
        <li>Variedade de formatos e registros diferentes no SPED.</li>
        <li>Falta de ferramentas simples e acessíveis para automatizar essas tarefas.</li>
    </ul>

    <p>Este site tem como objetivo fornecer uma plataforma prática e intuitiva para que profissionais da área fiscal possam automatizar suas análises, economizando tempo e reduzindo erros.<br>
    Vamos juntos transformar a rotina fiscal em um processo mais eficiente!</p>
    </div>
    """, unsafe_allow_html=True)

elif menu == "📂 Importar SPED":
    st.title("Importar SPED Fiscal")

    uploaded_file = st.file_uploader("Selecione o arquivo SPED (.txt)", type=["txt"])
    
    if uploaded_file:
        output = importar_sped_para_excel(uploaded_file)

        st.success("Arquivo processado com sucesso!")

        st.download_button(
            label="📥 Baixar Excel Gerado",
            data=output,
            file_name="sped_convertido.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif menu == "📤 Excel para TXT":
    funcao_excel_para_txt()



elif menu == "📊 Relatórios":
    relatorio_selecionado = st.selectbox("Selecione o relatório para visualizar:", [
        "📌 Relatório Tipo Item",
        "🔍 Conferência SPED x XML",
        "🧾 Conversor XML para Excel"
    ])

    if relatorio_selecionado:
        if "Tipo Item" in relatorio_selecionado:
            relatorio_tipo_item()
        elif "SPED x XML" in relatorio_selecionado:
            relatorio_conferencia_xml_txt()
        elif "Conversor XML" in relatorio_selecionado:
            relatorio_xml_para_excel()
