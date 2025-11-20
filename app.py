import streamlit as st
import pandas as pd
import os
from datetime import datetime
from groq import Groq

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gabinete Digital", page_icon="🏛️", layout="wide")

# --- CONFIGURAÇÃO DA IA (TENTA PEGAR DO COFRE, SE NÃO TIVER, AVISA) ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = "" # Deixa vazio pra não quebrar logo de cara, mas avisa depois

# --- FUNÇÃO: REDATOR IA (ATUALIZADA COM PEDIDO DE INFORMAÇÃO) ---
def gerar_documento_ia(tipo_doc, assunto):
    if not api_key:
        return "⚠️ ERRO: A chave da API não foi encontrada nos Secrets!"
    
    client = Groq(api_key=api_key)
    
    # Lógica para diferenciar Lei de Pedidos simples
    if tipo_doc == "Projeto de Lei":
        instrucao_extra = "Estruture o texto obrigatoriamente em ARTIGOS (Art. 1º, Art. 2º...), parágrafos e incisos. Linguagem normativa."
    else:
        # Serve para Pedidos de Providência, Informação, Indicações e Moções
        instrucao_extra = "NÃO use Artigos. Escreva em TEXTO CORRIDO (prosa), direto e objetivo. Comece com: 'O Vereador infra-assinado requer à Secretaria competente...'"

    prompt = f"""
    Atue como um Assessor Jurídico experiente da Câmara Municipal de Espumoso/RS.
    Redija uma minuta completa de: {tipo_doc}.
    Sobre o assunto: {assunto}.
    
    REGRAS DE OURO:
    1. {instrucao_extra}
    2. Se for Pedido de Informação, liste os questionamentos de forma clara.
    3. Adicione uma Justificativa convincente ao final.
    4. Não use markdown de negrito (**) no corpo do texto pra facilitar o copy-paste.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Ops, deu erro na IA: {e}"

# --- FUNÇÃO DE BANCO DE DADOS (ATUALIZADA COM NOVOS CAMPOS) ---
arquivo_ideias = "banco_de_ideias.csv"

def salvar_ideia(dados):
    # Se o arquivo não existe, cria com as novas colunas
    if not os.path.exists(arquivo_ideias):
        df = pd.DataFrame(columns=[
            "Data", "Nome", "Ideia", "Contribuição", "Localização", 
            "Áreas", "Idade", "Vereador Destino", "Concordou Termos"
        ])
    else:
        df = pd.read_csv(arquivo_ideias)
    
    # Adiciona a nova linha
    nova_linha = pd.DataFrame([dados])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(arquivo_ideias, index=False)

# --- MENU LATERAL (COM TEXTOS NOVOS) ---
if os.path.exists("brasao.png"):
    st.sidebar.image("brasao.png", width=120)
st.sidebar.title("Gabinete Digital")
st.sidebar.markdown("---")

modo = st.sidebar.radio(
    "Navegação:", 
    ["🏠 Início", "⚖️ Assistente de Proposições (com IA)", "💡 Banco de Ideias"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por:")
st.sidebar.markdown("**Daniel de Oliveira Colvero**")
st.sidebar.caption("© 2025 Câmara de Espumoso")

# --- TELA: INÍCIO ---
if modo == "🏠 Início":
    col1, col2 = st.columns([1, 3])
    with col2:
        st.title("Assistente Virtual Legislativo") # Título Novo
        st.write("Bem-vindo ao sistema inteligente de apoio ao mandato parlamentar.")
        st.info("👈 Utilize o menu lateral para navegar entre as ferramentas.")

# --- TELA: ASSISTENTE DE PROPOSIÇÕES (IA) ---
elif modo == "⚖️ Assistente de Proposições (com IA)":
    st.header("⚖️ Elaboração de Documentos Legislativos")
    st.write("Preencha os dados abaixo e deixe a Inteligência Artificial redigir a minuta inicial.")
    
    # Lista atualizada com Pedido de Informação
    tipo_doc = st.selectbox(
        "Tipo de Proposição", 
        ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"]
    )
    
    # Dica mais detalhada
    st.info("💡 **Dica:** Escreva aqui qual o problema, como vc imagina a solução e quais os motivos da sua solicitação. Quanto mais detalhes, melhor!")
    
    texto_input = st.text_area(
        "Detalhamento da solicitação:", 
        height=150, 
        placeholder="Ex: Solicito informações sobre o custo da obra na rua X, pois a comunidade relata paralisação..."
    )
    
    if st.button("📝 Elaborar Proposição"): # Botão com nome novo
        if texto_input:
            with st.spinner('A IA está consultando as leis e redigindo o texto...'):
                texto_final = gerar_documento_ia(tipo_doc, texto_input)
                st.subheader("Minuta Gerada:")
                st.success("Documento criado com sucesso! Copie abaixo:")
                st.text_area("Texto para Copiar:", value=texto_final, height=500)
        else:
            st.warning("Por favor, descreva a situação antes de pedir para elaborar.")

# --- TELA: BANCO DE IDEIAS (COMPLETO E NOVO) ---
elif modo == "💡 Banco de Ideias":
    st.header("💡 Banco de Ideias da Comunidade")
    st.markdown("Preencha o formulário abaixo para contribuir com o futuro de Espumoso.")
    
    with st.form("form_ideia_completo", clear_on_submit=True):
        
        # 1. Dados Pessoais
        st.subheader("1. Sobre Você")
        nome = st.text_input("Seu nome completo:", help="Seus dados estarão protegidos. É apenas para contato se necessário.")
        
        idade = st.radio(
            "Qual a sua idade?",
            ["Menos de 18 anos", "18 a 30 anos", "31 a 45 anos", "46 a 60 anos", "Acima de 60 anos"],
            horizontal=True,
            help="Usado apenas para estatística anônima."
        )

        st.markdown("---")
        
        # 2. A Ideia
        st.subheader("2. Sua Ideia")
        
        ideia_desc = st.text_area(
            "Descreva sua sugestão/ideia:",
            height=100,
            help="Não se preocupe em escrever bonito. Ex: 'Sugiro um quebra-molas na Rua X' ou 'Aulas de violão no bairro Y'."
        )
        
        contribuição = st.text_area(
            "Como isso pode contribuir para a comunidade?",
            height=100,
            help="Por que isso é importante? Ex: 'Evitaria acidentes' ou 'Tiraria jovens da rua'."
        )
        
        localizacao = st.text_input(
            "Localização (Onde deve acontecer?):",
            placeholder="Ex: No bairro Centro, na Rua...",
            help="Diga onde o problema está ou onde a ideia deve ser aplicada."
        )
        
        areas = st.multiselect(
            "Em qual(is) área(s) sua ideia se encaixa?",
            [
                "Agricultura e Zona Rural", "Cultura e Lazer", "Educação", 
                "Empregabilidade", "Infraestrutura", "Meio Ambiente", 
                "Mobilidade Urbana", "Saúde", "Segurança", "Tecnologia", "Trânsito"
            ],
            help="Pode marcar mais de uma!"
        )

        st.markdown("---")

        # 3. Encaminhamento
        st.subheader("3. Destino")
        
        vereador = st.selectbox(
            "Enviar sugestão para qual vereador(a)?",
            [
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
            ],
            help="Escolha quem você acredita que melhor representa sua ideia."
        )

        # 4. Termos
        st.markdown("---")
        st.caption("""
        Ao enviar sua sugestão, você concorda que ela será analisada.
        Confirma que é uma sugestão construtiva para Espumoso.
        O envio não garante implementação imediata, pois depende de viabilidade.
        """)
        termos = st.checkbox("Eu li e concordo com os termos e o foco desta ferramenta.")
        
        # Botão de Enviar
        enviou = st.form_submit_button("🚀 Enviar Sugestão")

        if enviou:
            # Validação simples
            if not termos:
                st.error("Você precisa concordar com os termos para enviar.")
            elif not ideia_desc:
                st.error("Por favor, descreva sua ideia.")
            elif vereador == "Escolha um vereador...":
                st.error("Por favor, escolha um vereador para receber a ideia.")
            else:
                # Prepara os dados para salvar
                dados_salvar = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Nome": nome,
                    "Ideia": ideia_desc,
                    "Contribuição": contribuição,
                    "Localização": localizacao,
                    "Áreas": ", ".join(areas), # Junta as áreas com vírgula
                    "Idade": idade,
                    "Vereador Destino": vereador,
                    "Concordou Termos": "Sim"
                }
                salvar_ideia(dados_salvar)
                st.balloons()
                st.success(f"Obrigado, {nome}! Sua ideia foi registrada e encaminhada para {vereador}.")

    # --- MOSTRAR DADOS (ADM) ---
    st.divider()
    with st.expander("Ver estatísticas das ideias enviadas (Transparência)"):
        if os.path.exists(arquivo_ideias):
            df = pd.read_csv(arquivo_ideias)
            st.dataframe(df, use_container_width=True)
            st.metric("Total de Ideias", len(df))
        else:
            st.info("Nenhuma ideia registrada ainda.")