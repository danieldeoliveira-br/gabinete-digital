import streamlit as st
import pandas as pd
import os
from datetime import datetime
from groq import Groq  # O Cérebro novo

# --- ⚠️ CONFIGURAÇÃO DA IA (COLOQUE SUA CHAVE AQUI) ---
api_key = st.secrets["GROQ_API_KEY"]

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gabinete Digital", page_icon="🏛️")

# --- FUNÇÃO: REDATOR IA (AGORA MAIS ESPERTO) ---
def gerar_documento_ia(tipo_doc, assunto):
    if "SUA_CHAVE" in api_key:
        return "⚠️ ERRO: Você esqueceu de colocar a chave da API no código (linha 8)!"
    
    client = Groq(api_key=api_key)
    
    # AQUI TÁ O SEGREDO: A gente muda a ordem dependendo do documento
    if tipo_doc == "Projeto de Lei":
        instrucao_extra = "Estruture o texto obrigatoriamente em ARTIGOS (Art. 1º, Art. 2º...), parágrafos e incisos. Linguagem normativa."
    else:
        # Serve para Pedidos, Indicações e Moções
        instrucao_extra = "NÃO use Artigos. Escreva em TEXTO CORRIDO (prosa), direto e objetivo. Comece com: 'O Vereador infra-assinado requer à Secretaria competente...'"

    prompt = f"""
    Atue como um Assessor Jurídico experiente da Câmara Municipal de Espumoso/RS.
    Redija uma minuta completa de: {tipo_doc}.
    Sobre o assunto: {assunto}.
    
    REGRAS DE OURO:
    1. {instrucao_extra}
    2. Se for Pedido de Providência, seja prático.
    3. Adicione uma Justificativa convincente ao final.
    4. Não use markdown de negrito (**) no corpo do texto pra facilitar o copy-paste.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", # O motor novo e potente
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Ops, deu erro na IA: {e}"

# --- FUNÇÃO DE BANCO DE DADOS ---
arquivo_ideias = "banco_de_ideias.csv"

def salvar_ideia(nome, ideia, tipo):
    if not os.path.exists(arquivo_ideias):
        df = pd.DataFrame(columns=["Data", "Nome", "Tipo", "Ideia"])
    else:
        df = pd.read_csv(arquivo_ideias)
    
    nova_linha = pd.DataFrame({
        "Data": [datetime.now().strftime("%d/%m/%Y %H:%M")],
        "Nome": [nome],
        "Tipo": [tipo],
        "Ideia": [ideia]
    })
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(arquivo_ideias, index=False)

# --- MENU LATERAL ---
st.sidebar.title("Gabinete Digital")
modo = st.sidebar.radio("Ir para:", ["🏠 Início", "🤖 Redator IA (Real)", "💡 Banco de Ideias"])

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por:")
st.sidebar.markdown("**Daniel de Oliveira Colvero**")
st.sidebar.caption("© 2025 Câmara de Espumoso")

# --- TELA: INÍCIO ---
if modo == "🏠 Início":
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("brasao.png"):
            st.image("brasao.png", width=100)
        else:
            st.header("🏛️")
    with col2:
        st.title("Câmara Municipal de Espumoso")
        st.write("Sistema Integrado de Gestão Legislativa")
    
    st.info("👈 Escolha uma opção no menu ao lado para começar.")

# --- TELA: REDATOR IA (REAL) ---
elif modo == "🤖 Redator IA (Real)":
    st.header("🤖 Assistente Legislativo (IA)")
    st.write("Agora a IA escreve de verdade. Teste com qualquer assunto!")
    
    tipo_doc = st.selectbox("Tipo de Documento", ["Pedido de Providência", "Indicação", "Projeto de Lei", "Moção de Aplauso"])
    texto_input = st.text_area("Descreva a situação (pode ser informal):", height=100, placeholder="Ex: Pedir para pintar a faixa de pedestre na frente da escola...")
    
    if st.button("✨ Escrever Minuta"):
        if texto_input:
            with st.spinner('Consultando a IA e redigindo o texto jurídico...'):
                texto_final = gerar_documento_ia(tipo_doc, texto_input)
                st.subheader("Minuta Gerada:")
                st.text_area("Copie e cole no Word:", value=texto_final, height=500)
        else:
            st.warning("Escreva o assunto primeiro!")

# --- TELA: BANCO DE IDEIAS ---
elif modo == "💡 Banco de Ideias":
    st.header("💡 Banco de Ideias Legislativas")
    
    with st.form("form_ideia", clear_on_submit=True):
        nome = st.text_input("Seu Nome (Opcional)")
        tipo = st.selectbox("Área", ["Saúde", "Obras", "Educação", "Lazer", "Outros"])
        ideia = st.text_area("Qual é a sua ideia?")
        
        if st.form_submit_button("🚀 Enviar Ideia"):
            if ideia:
                salvar_ideia(nome, ideia, tipo)
                st.balloons()
                st.success("Ideia registrada!")
            else:
                st.error("Escreva algo!")

    st.divider()
    st.subheader("Últimas contribuições")
    if os.path.exists(arquivo_ideias):
        df = pd.read_csv(arquivo_ideias)
        st.dataframe(df.tail(5), use_container_width=True)
    else:
        st.write("Nenhuma ideia enviada ainda.")