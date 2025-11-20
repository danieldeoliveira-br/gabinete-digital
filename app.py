import streamlit as st
import pandas as pd
import os
from datetime import datetime
from groq import Groq

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gabinete Digital", page_icon="🏛️", layout="wide")

# --- CONFIGURAÇÃO DA IA ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = ""

# --- FUNÇÃO: REDATOR IA ---
def gerar_documento_ia(tipo_doc, assunto):
    if not api_key:
        return "⚠️ ERRO: A chave da API não foi encontrada nos Secrets!"
    
    client = Groq(api_key=api_key)
    
    if tipo_doc == "Projeto de Lei":
        instrucao_extra = "Estruture o texto obrigatoriamente em ARTIGOS (Art. 1º, Art. 2º...), parágrafos e incisos. Linguagem normativa."
    else:
        instrucao_extra = "NÃO use Artigos. Escreva em TEXTO CORRIDO (prosa), direto e objetivo. Comece com: 'O Vereador infra-assinado requer à Secretaria competente...'"

    prompt = f"""
    Atue como um Assessor Jurídico experiente da Câmara Municipal de Espumoso/RS.
    Redija uma minuta completa de: {tipo_doc}.
    Sobre o assunto: {assunto}.
    
    REGRAS DE OURO:
    1. {instrucao_extra}
    2. Se for Pedido de Informação, liste os questionamentos de forma clara.
    3. Adicione uma Justificativa convincente ao final.
    4. Não use markdown de negrito (**) no corpo do texto.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Ops, deu erro na IA: {e}"

# --- FUNÇÃO DE BANCO DE DADOS ---
arquivo_ideias = "banco_de_ideias.csv"

def salvar_ideia(dados):
    if not os.path.exists(arquivo_ideias):
        df = pd.DataFrame(columns=[
            "Data", "Nome", "Contato", "Ideia", "Contribuição", 
            "Localização", "Áreas", "Idade", "Vereador Destino", "Concordou Termos"
        ])
    else:
        df = pd.read_csv(arquivo_ideias)
    
    nova_linha = pd.DataFrame([dados])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(arquivo_ideias, index=False)

# --- MENU LATERAL ---
if os.path.exists("brasao.png"):
    st.sidebar.image("brasao.png", width=120)

st.sidebar.title("Gabinete Digital")

# --- NOVAS INFORMAÇÕES DA CÂMARA ---
st.sidebar.markdown("**Câmara Municipal de Espumoso**")
st.sidebar.markdown("Rio Grande do Sul")
st.sidebar.markdown("[🌐 Site Oficial da Câmara](https://www.camaraespumoso.rs.gov.br)")
st.sidebar.markdown("---")

if "navegacao" not in st.session_state:
    st.session_state["navegacao"] = "🏠 Início"

modo = st.sidebar.selectbox(
    "Selecione a ferramenta:", 
    ["🏠 Início", "⚖️ Assistente de Proposições (com IA)", "💡 Banco de Ideias"],
    key="navegacao"
)

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por:")
# --- SEU NOME AGORA É UM LINK DE E-MAIL ---
st.sidebar.markdown("[**Daniel de Oliveira Colvero**](mailto:daniel.colvero@gmail.com)")
st.sidebar.caption("© 2025 Câmara de Espumoso")

# --- TELA: INÍCIO ---
if modo == "🏠 Início":
    st.title("Assistente Virtual Legislativo")
    st.write("Bem-vindo! Toque em uma das opções abaixo para começar:")
    st.divider()

    def ir_para_assistente():
        st.session_state.navegacao = "⚖️ Assistente de Proposições (com IA)"
        
    def ir_para_ideias():
        st.session_state.navegacao = "💡 Banco de Ideias"

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.info("🤖 Para Vereadores e Assessores")
        st.button("Criar Documento / Lei 📝", use_container_width=True, on_click=ir_para_assistente)
            
    with col_b:
        st.success("💡 Para a Comunidade")
        st.button("Enviar uma Ideia / Sugestão 🚀", use_container_width=True, on_click=ir_para_ideias)

    st.divider()

# --- TELA: ASSISTENTE DE PROPOSIÇÕES (RESTRITA) ---
elif modo == "⚖️ Assistente de Proposições (com IA)":
    
    def voltar_inicio():
        st.session_state.navegacao = "🏠 Início"
        
    st.button("⬅️ Voltar para o Início", on_click=voltar_inicio, key="voltar_assistente")

    if "acesso_vereador" not in st.session_state:
        st.session_state["acesso_vereador"] = False

    if not st.session_state["acesso_vereador"]:
        st.header("🔒 Acesso Restrito")
        st.warning("Esta ferramenta é exclusiva para Vereadores e Assessores.")
        
        senha_digitada = st.text_input("Digite a senha de acesso:", type="password")
        
        if st.button("Entrar"):
            if senha_digitada == "camara2025": 
                st.session_state["acesso_vereador"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    else:
        if st.button("Sair do Modo Restrito", type="secondary"):
            st.session_state["acesso_vereador"] = False
            st.rerun()
            
        st.divider()
        st.header("⚖️ Elaboração de Documentos")
        st.write("Preencha os dados abaixo e deixe a IA redigir a minuta.")
        
        tipo_doc = st.selectbox(
            "Tipo de Proposição", 
            ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"]
        )
        
        st.info("💡 Dica: Quanto mais detalhes, melhor o texto final!")
        texto_input = st.text_area("Detalhamento da solicitação:", height=150)
        
        if st.button("📝 Elaborar Proposição"):
            if texto_input:
                with st.spinner('Redigindo documento...'):
                    texto_final = gerar_documento_ia(tipo_doc, texto_input)
                    st.subheader("Minuta Gerada:")
                    st.text_area("Texto para Copiar:", value=texto_final, height=500)
            else:
                st.warning("Descreva a situação primeiro.")

# --- TELA: BANCO DE IDEIAS (PÚBLICA) ---
elif modo == "💡 Banco de Ideias":
    
    def voltar_inicio():
        st.session_state.navegacao = "🏠 Início"
        
    st.button("⬅️ Voltar para o Início", on_click=voltar_inicio, key="voltar_ideias")

    st.header("💡 Banco de Ideias da Comunidade")
    
    with st.form("form_ideia_completo", clear_on_submit=True):
        st.subheader("1. Sobre Você")
        nome = st.text_input("Seu nome completo:")
        contato = st.text_input("Seu WhatsApp/Celular (Opcional):", placeholder="(54) 99999-9999")
        idade = st.radio("Qual a sua idade?", ["-18", "18-30", "31-45", "46-60", "60+"], horizontal=True)

        st.markdown("---")
        st.subheader("2. Sua Ideia")
        ideia_desc = st.text_area("Descreva sua sugestão/ideia:", height=100)
        contribuição = st.text_area("Como isso contribui para a comunidade?", height=100)
        localizacao = st.text_input("Localização:")
        areas = st.multiselect("Áreas:", ["Saúde", "Educação", "Obras", "Lazer", "Segurança", "Trânsito", "Outros"])

        st.markdown("---")
        st.subheader("3. Destino")
        vereador = st.selectbox("Para qual vereador?", [
            "Escolha um vereador...",
            "Vereadora Dayana Soares de Camargo (PDT)",
            "Vereador Denner Fernando Duarte Senhor (PL)",
            "Vereador Eduardo Signor (União Brasil)",
            "Vereadora Fabiana Dolci Otoni (PP)",
            "Vereadora Ivone Maria Capitanio Missio (PP)",
            "Vereador Leandro Keller Colleraus (PDT)",
            "Vereador Marina Machado (PL)",
            "Vereador Paulo Flores de Moraes (PDT)",
            "Vereador Tomas Fiuza (PP)"
        ])

        st.markdown("---")
        termos = st.checkbox("Eu li e concordo com os termos.")
        
        if st.form_submit_button("🚀 Enviar Sugestão"):
            if not termos:
                st.error("Aceite os termos para enviar.")
            elif not ideia_desc:
                st.error("Descreva sua ideia.")
            elif vereador == "Escolha um vereador...":
                st.error("Escolha um vereador.")
            else:
                dados_salvar = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Nome": nome,
                    "Contato": contato,
                    "Ideia": ideia_desc,
                    "Contribuição": contribuição,
                    "Localização": localizacao,
                    "Áreas": ", ".join(areas),
                    "Idade": idade,
                    "Vereador Destino": vereador,
                    "Concordou Termos": "Sim"
                }
                salvar_ideia(dados_salvar)
                st.balloons()
                st.success("Ideia enviada com sucesso!")

    st.divider()
    st.subheader("🔐 Área Administrativa")
    senha = st.text_input("Senha ADM:", type="password")
    
    if senha == "Camesp1955":
        st.success("Acesso Liberado!")
        if os.path.exists(arquivo_ideias):
            df = pd.read_csv(arquivo_ideias)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Relatório", data=csv, file_name="ideias.csv", mime="text/csv")
        else:
            st.info("Nenhuma ideia ainda.")
    elif senha:
        st.error("Senha incorreta.")