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

# --- MENU LATERAL (COM CHAVE DE CONTROLE) ---
# Se não tiver nada na memória ainda, começa no Início
if "navegacao" not in st.session_state:
    st.session_state["navegacao"] = "🏠 Início"

modo = st.sidebar.selectbox(
    "Selecione a ferramenta:", 
    ["🏠 Início", "⚖️ Assistente de Proposições (com IA)", "💡 Banco de Ideias"],
    key="navegacao" # ISSO AQUI É O SEGREDO pra conectar com os botões
)

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por:")
st.sidebar.markdown("**Daniel de Oliveira Colvero**")
st.sidebar.caption("© 2025 Câmara de Espumoso")

# --- TELA: INÍCIO (AGORA COM BOTÕES GRANDES) ---
if modo == "🏠 Início":
    st.title("Assistente Virtual Legislativo")
    st.write("Bem-vindo! Toque em uma das opções abaixo para começar:")
    st.divider()

    # Cria duas colunas para os botões não ficarem gigantes
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Botão para o Assistente
        st.info("🤖 Para Vereadores e Assessores")
        if st.button("Criar Documento / Lei 📝", use_container_width=True):
            st.session_state["navegacao"] = "⚖️ Assistente de Proposições (com IA)"
            st.rerun() # Recarrega a página indo pro destino
            
    with col_b:
        # Botão para o Banco de Ideias
        st.success("💡 Para a Comunidade")
        if st.button("Enviar uma Ideia / Sugestão 🚀", use_container_width=True):
            st.session_state["navegacao"] = "💡 Banco de Ideias"
            st.rerun() # Recarrega a página indo pro destino

    st.divider()
    st.caption("Ou utilize o menu lateral (seta no canto superior esquerdo) para mais opções.")

# --- TELA: ASSISTENTE DE PROPOSIÇÕES (COM SENHA) ---
elif modo == "⚖️ Assistente de Proposições (com IA)":
    
    # Verifica se já está logado na sessão
    if "acesso_vereador" not in st.session_state:
        st.session_state["acesso_vereador"] = False

    # Se NÃO estiver logado, mostra a tela de bloqueio
    if not st.session_state["acesso_vereador"]:
        st.header("🔒 Acesso Restrito")
        st.warning("Esta ferramenta é exclusiva para Vereadores e Assessores.")
        
        senha_digitada = st.text_input("Digite a senha de acesso:", type="password")
        
        if st.button("Entrar"):
            # --- DEFINA A SENHA AQUI ---
            if senha_digitada == "camara@9": 
                st.session_state["acesso_vereador"] = True
                st.rerun() # Atualiza a página pra liberar
            else:
                st.error("Senha incorreta.")
                
    # Se JÁ estiver logado, mostra a ferramenta normal
    else:
        # Botãozinho discreto pra sair (Logout)
        if st.button("Sair do Modo Restrito", type="secondary"):
            st.session_state["acesso_vereador"] = False
            st.rerun()
            
        st.divider()
        st.header("⚖️ Elaboração de Documentos Legislativos")
        st.write("Preencha os dados abaixo e deixe a Inteligência Artificial redigir a minuta inicial.")
        
        tipo_doc = st.selectbox(
            "Tipo de Proposição", 
            ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"]
        )
        
        st.info("💡 **Dica:** Escreva aqui qual o problema, como vc imagina a solução e quais os motivos da sua solicitação. Quanto mais detalhes, melhor!")
        
        texto_input = st.text_area(
            "Detalhamento da solicitação:", 
            height=150, 
            placeholder="Ex: Solicito informações sobre o custo da obra na rua X, pois a comunidade relata paralisação..."
        )
        
        if st.button("📝 Elaborar Proposição"):
            if texto_input:
                with st.spinner('A IA está consultando as leis e redigindo o texto...'):
                    texto_final = gerar_documento_ia(tipo_doc, texto_input)
                    st.subheader("Minuta Gerada:")
                    st.success("Documento criado com sucesso! Copie abaixo:")
                    st.text_area("Texto para Copiar:", value=texto_final, height=500)
            else:
                st.warning("Por favor, descreva a situação antes de pedir para elaborar.")
    
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
    # --- ÁREA RESTRITA DO ADMINISTRADOR 🔐 ---
    st.divider()
    st.subheader("🔐 Área Administrativa")
    
    # Campo de senha (o type="password" esconde as letras com bolinhas)
    senha = st.text_input("Digite a senha de administrador para ver as ideias:", type="password")
    
    # CONFIGURE A SUA SENHA AQUI (Pode mudar "admin123" pelo que quiser)
    SENHA_SECRETA = "camesp1955"
    
    if senha == SENHA_SECRETA:
        st.success("Acesso Liberado!")
        
        if os.path.exists(arquivo_ideias):
            df = pd.read_csv(arquivo_ideias)
            
            # Mostra a tabela só pra quem tem a senha
            st.dataframe(df, use_container_width=True)
            st.metric("Total de Ideias Recebidas", len(df))
            
            # Botão para baixar a planilha pro teu computador
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Planilha Completa (Excel/CSV)",
                data=csv,
                file_name="relatorio_ideias_camara.csv",
                mime="text/csv",
            )
        else:
            st.info("Nenhuma ideia registrada ainda no banco de dados.")
            
    elif senha:
        st.error("Senha incorreta. Acesso negado.")