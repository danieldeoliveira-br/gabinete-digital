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

# --- LISTA DE VEREADORES ---
LISTA_VEREADORES = [
    "Vereadora Dayana Soares de Camargo (PDT)",
    "Vereador Denner Fernando Duarte Senhor (PL)",
    "Vereador Eduardo Signor (UNIÃO BRASIL)",
    "Vereadora Fabiana Dolci Otoni (PROGRESSISTAS)",
    "Vereadora Ivone Maria Capitanio Missio (PROGRESSISTAS)",
    "Vereador Leandro Keller Colleraus (PDT)",
    "Vereadora Marina Camera Machado (PL)",
    "Vereador Paulo Flores de Moraes (PDT)",
    "Vereador Tomas Fiuza (PROGRESSISTAS)"
]

# --- FUNÇÃO: REDATOR IA ---
def gerar_documento_ia(autor, tipo_doc, assunto):
    if not api_key:
        return "⚠️ ERRO: A chave da API não foi encontrada nos Secrets!"
    
    client = Groq(api_key=api_key)
    
    if tipo_doc == "Projeto de Lei":
        regras_especificas = """
        TÉCNICA LEGISLATIVA (OBRIGATÓRIO):
        1. O texto da lei deve vir IMEDIATAMENTE após a Ementa.
        2. Use Artigos (Art. 1º, Art. 2º...), Parágrafos (§ 1º) e Incisos (I, II).
        3. Linguagem: Formal, Impessoal e Imperativa.
        4. VÍCIO DE INICIATIVA: Se o assunto gerar despesa ou envolver gestão interna da prefeitura, use 'Fica o Poder Executivo AUTORIZADO a instituir...'.
        5. CLÁUSULAS PADRÃO:
           - Penúltimo Artigo: 'O Poder Executivo regulamentará a presente Lei no que couber.'
           - Último Artigo: 'Esta Lei entra em vigor na data de sua publicação.'
        """
    else:
        regras_especificas = """
        ESTRUTURA DE TEXTO CORRIDO (Para Indicações/Pedidos):
        1. Inicie com: 'O Vereador que este subscreve, no uso de suas atribuições legais...'
        2. Texto corrido, sem artigos.
        3. Seja direto na solicitação.
        """

    prompt = f"""
    Atue como um Procurador Jurídico Sênior da Câmara Municipal de Espumoso/RS.
    Redija uma minuta de {tipo_doc} com alto rigor técnico.
    
    AUTOR: {autor}.
    ASSUNTO: {assunto}.
    
    ORDEM OBRIGATÓRIA DO DOCUMENTO (NÃO INVERTA):
    
    1. CABEÇALHO: "EXCELENTÍSSIMO SENHOR PRESIDENTE DA CÂMARA MUNICIPAL DE ESPUMOSO – RS"
    
    2. PREÂMBULO: "{autor}, integrante da Bancada [Extrair Partido], no uso de suas atribuições legais e regimentais, submete à apreciação do Plenário o seguinte {tipo_doc.upper()}:"
    
    3. EMENTA: (Resumo do assunto em caixa alta, negrito e centralizado).
    
    4. TEXTO DA PROPOSIÇÃO (AQUI ENTRAM OS ARTIGOS OU O PEDIDO):
       {regras_especificas}
    
    5. JUSTIFICATIVA (SOMENTE DEPOIS DO TEXTO DA LEI):
       Título: "JUSTIFICATIVA"
       Escreva um texto dissertativo-argumentativo formal defendendo a proposta.
       Foque na relevância social, jurídica e no interesse público.
    
    6. FECHAMENTO:
       "Sala das Sessões, Espumoso – RS, [Data de Hoje]."
       (Espaço para assinatura)
       {autor}
       Vereador(a)
       
    IMPORTANTE: Não use markdown de negrito (**) no corpo dos artigos.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
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

st.sidebar.markdown("**Câmara Municipal de Espumoso**")
st.sidebar.markdown("Rio Grande do Sul")
st.sidebar.markdown("[🌐 Site Oficial](https://www.camaraespumoso.rs.gov.br)")
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
        
        autor_selecionado = st.selectbox("Autor da Proposição:", LISTA_VEREADORES)

        tipo_doc = st.selectbox(
            "Tipo de Proposição", 
            ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"]
        )
        
        if tipo_doc == "Projeto de Lei":
            st.warning("⚠️ Atenção: A IA tentará evitar Vício de Iniciativa criando leis 'Autorizativas' quando necessário.")
        
        st.info("💡 Dica: Quanto mais detalhes, melhor o texto final!")
        texto_input = st.text_area("Detalhamento da solicitação:", height=150)
        
        if st.button("📝 Elaborar Proposição"):
            if texto_input:
                with st.spinner('Redigindo documento com rigor técnico...'):
                    texto_final = gerar_documento_ia(autor_selecionado, tipo_doc, texto_input)
                    st.subheader("Minuta Gerada:")
                    st.text_area("Texto para Copiar:", value=texto_final, height=500)
            else:
                st.warning("Descreva a situação primeiro.")

# --- TELA: BANCO DE IDEIAS (PÚBLICA) ---
elif modo == "💡 Banco de Ideias":
    
    def voltar_inicio():
        st.session_state.navegacao = "🏠 Início"
        
    st.button("⬅️ Voltar para o Início", on_click=voltar_inicio, key="voltar_ideias")

    # --- CABEÇALHO EXPLICATIVO (IGUAL AO GOOGLE FORMS) ---
    st.title("Banco de Ideias - Espumoso/RS")
    
    st.info("""
    **Bem-vindo(a) ao Banco de Ideias da Câmara de Espumoso!**
    Este é o seu canal direto para enviar PROPOSTAS e SUGESTÕES CONSTRUTIVAS focadas em melhorar a nossa cidade.
    """)
    
    with st.expander("ℹ️ PARA QUE SERVE ESTE FORMULÁRIO (Clique para ler)"):
        st.markdown("""
        Use este espaço para enviar IDEIAS de competência MUNICIPAL, tais como:
        * **Sugestões** para novos Projetos de Lei municipais.
        * **Indicações** (Ex: "Pedir a instalação de um quebra-molas na frente da escola Y").
        * **Pedidos de Providência** (Ex: "Solicitar o conserto do buraco na Rua X").
        
        **IMPORTANTE: FOCO EM ESPUMOSO**
        Este formulário NÃO é o canal para manifestações gerais sobre política, nem para Reclamações ou Denúncias (para estes, use o canal de Ouvidoria).
        Se você tem uma IDEIA ou SUGESTÃO para Espumoso, você está no lugar certo!
        """)
    
    st.divider()

    with st.form("form_ideia_completo", clear_on_submit=True):
        
        # --- DADOS PESSOAIS ---
        st.subheader("1. Sobre Você")
        nome = st.text_input("Seu nome completo:", help="Precisamos dos seus dados apenas para que o Vereador possa, se necessário, entrar em contato para entender melhor a sua ideia. Seus dados estarão protegidos.")
        contato = st.text_input("Seu número de celular:")
        
        # --- DADOS DA IDEIA ---
        st.subheader("2. Sua Ideia")
        ideia_desc = st.text_area(
            "Descreva sua sugestão/ideia:", 
            height=150,
            help='Dica: Não se preocupe em escrever bonito. Apenas nos diga o que você gostaria que fosse feito. Ex: "Sugiro colocar um quebra-molas na Rua X..." ou "Aulas de violão no bairro Y..."'
        )
        
        contribuição = st.text_area(
            "Como isso pode contribuir para a comunidade?", 
            height=100,
            help='Dica: Nos diga por que sua ideia é importante. Ex: "Isso evitaria acidentes com as crianças..." ou "Ajudaria a tirar os jovens da rua..."'
        )
        
        localizacao = st.text_input(
            "Localização:",
            help='Dica: Nos diga onde o problema está. Ex: "No bairro Centro, na Rua...", "Em frente à Praça...", "Próximo ao número X..."'
        )
        
        # --- ÁREAS ---
        st.markdown("**Em qual(is) área(s) você acha que sua ideia pode melhorar?**")
        st.caption("Pode marcar mais de uma! Isso nos ajuda a organizar todas as ideias recebidas.")
        areas = st.multiselect("Selecione as áreas:", [
            "Agricultura e Zona Rural", "Cultura e Lazer", "Educação", 
            "Empregabilidade", "Infraestrutura", "Meio Ambiente", 
            "Mobilidade Urbana", "Saúde", "Segurança", "Tecnologia", "Trânsito"
        ])

        st.markdown("---")
        
        # --- IDADE ---
        st.markdown("**Qual a sua idade?**")
        st.caption("Esta informação nos ajuda muito para estatística (de forma anônima), para sabermos se as necessidades dos mais jovens são diferentes das necessidades dos mais experientes.")
        idade = st.radio("Faixa etária:", ["Menos de 18 anos", "18 a 30 anos", "31 a 45 anos", "46 a 60 anos", "Acima de 60 anos"], horizontal=True)

        st.markdown("---")
        
        # --- DESTINO ---
        st.subheader("3. Destino")
        st.markdown("**Enviar sugestão para qual vereador(a)?**")
        st.caption("A Secretaria da Câmara vai receber sua ideia e encaminhá-la ao vereador que você selecionar.")
        vereador = st.selectbox("Escolha o vereador:", ["Escolha um vereador..."] + LISTA_VEREADORES)

        st.markdown("---")
        
        # --- TERMOS ---
        st.caption("""
        Ao enviar sua sugestão, você concorda que ela será analisada.
        Você confirma que sua proposta é uma sugestão construtiva focada em Espumoso.
        O envio não garante a implementação da ideia.
        """)
        termos = st.checkbox("Eu li e concordo com os termos e o foco desta ferramenta.")
        
        if st.form_submit_button("🚀 Enviar Sugestão"):
            if not termos:
                st.error("Você precisa concordar com os termos para enviar.")
            elif not ideia_desc:
                st.error("Por favor, descreva sua ideia.")
            elif vereador == "Escolha um vereador...":
                st.error("Por favor, escolha um vereador para receber a ideia.")
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
                st.success("Sua ideia foi enviada com sucesso! Agradecemos sua participação.")

    st.divider()
    st.subheader("🔐 Área Administrativa")
    senha = st.text_input("Senha ADM:", type="password")
    
    if senha == "admin123":
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