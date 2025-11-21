import streamlit as st
import pandas as pd
import os
from datetime import datetime
from groq import Groq

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Legislativo Digital", page_icon="🏛️", layout="wide")

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
    "Vereador Marina Camera Machado (PL)",
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
       "Plenário Agostinho Somavilla, [Data de Hoje]."
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

# --- FUNÇÕES DE BANCO DE DADOS ---
arquivo_ideias = "banco_de_ideias.csv"
arquivo_mural = "mural_posts.csv"

def salvar_ideia(dados):
    if not os.path.exists(arquivo_ideias):
        df = pd.DataFrame(columns=["Data", "Nome", "Contato", "Ideia", "Contribuição", "Localização", "Áreas", "Idade", "Vereador Destino", "Concordou Termos"])
    else:
        df = pd.read_csv(arquivo_ideias)
    nova_linha = pd.DataFrame([dados])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(arquivo_ideias, index=False)

def salvar_post_mural(dados):
    if not os.path.exists(arquivo_mural):
        df = pd.DataFrame(columns=["Data", "Vereador", "Titulo", "Mensagem"])
    else:
        df = pd.read_csv(arquivo_mural)
    nova_linha = pd.DataFrame([dados])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(arquivo_mural, index=False)

# --- FUNÇÃO PARA DEFINIR AVATAR ---
def obter_avatar_simples(nome):
    if nome.startswith("Vereadora"):
        return "👩"
    else:
        return "👨"

# --- MENU LATERAL ---
if os.path.exists("brasao.png"):
    st.sidebar.image("brasao.png", width=120)

st.sidebar.title("Legislativo Digital | Espumoso")
st.sidebar.markdown("**Câmara Municipal de Espumoso**")
st.sidebar.markdown("Rio Grande do Sul")
st.sidebar.markdown("[🌐 Site Oficial](https://www.camaraespumoso.rs.gov.br)")
st.sidebar.markdown("---")

if "navegacao" not in st.session_state:
    st.session_state["navegacao"] = "🏠 Início"

modo = st.sidebar.selectbox(
    "Selecione a ferramenta:", 
    ["🏠 Início", "👤 Gabinete Virtual", "🔐 Área do Vereador", "💡 Banco de Ideias"],
    key="navegacao"
)

st.sidebar.markdown("---")
link_whatsapp = "https://wa.me/555433834488" 
st.sidebar.markdown(f"""
    <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #128C7E; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-family: sans-serif; margin-bottom: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.2); transition: 0.3s;">
            💬 Falar no WhatsApp
        </div>
    </a>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por:")
st.sidebar.markdown("[**Daniel de Oliveira Colvero**](mailto:daniel.colvero@gmail.com)")
st.sidebar.caption("© 2025 Câmara de Espumoso")

# --- TELA: INÍCIO ---
if modo == "🏠 Início":
    st.title("Legislativo Digital")
    st.write("Bem-vindo ao ambiente digital do Poder Legislativo de Espumoso! Toque em uma das opções abaixo para começar:")
    st.divider()

    def ir_para_assistente():
        st.session_state.navegacao = "🔐 Área do Vereador"
    def ir_para_ideias():
        st.session_state.navegacao = "💡 Banco de Ideias"
    def ir_para_gabinete():
        st.session_state.navegacao = "👤 Gabinete Virtual"

    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.info("🤖 Para Vereadores")
        st.button("Criar Lei / Documentos 📝", use_container_width=True, on_click=ir_para_assistente)
            
    with col_b:
        st.success("💡 Para a Comunidade")
        st.button("Enviar Ideia / Sugestão 🚀", use_container_width=True, on_click=ir_para_ideias)

    with col_c:
        st.warning("🏛️ Gabinetes")
        st.button("Visitar Gabinete Virtual 👤", use_container_width=True, on_click=ir_para_gabinete)

    st.divider()

# --- TELA: GABINETE VIRTUAL ---
elif modo == "👤 Gabinete Virtual":
    def voltar_inicio():
        st.session_state.navegacao = "🏠 Início"
    st.button("⬅️ Voltar para o Início", on_click=voltar_inicio, key="voltar_gabinete")
    
    st.header("👤 Gabinetes Virtuais")
    
    vereador_selecionado = st.selectbox("Selecione um vereador para ver o perfil completo ou veja o Feed Geral abaixo:", ["Selecione..."] + LISTA_VEREADORES)
    
    # --- MODO 1: FEED GERAL ---
    if vereador_selecionado == "Selecione...":
        st.divider()
        st.subheader("📢 Feed de Notícias - Últimas Atividades da Câmara")
        
        if os.path.exists(arquivo_mural):
            df_mural = pd.read_csv(arquivo_mural)
            if not df_mural.empty:
                ultimas_postagens = df_mural.iloc[::-1].head(10)
                
                for index, row in ultimas_postagens.iterrows():
                    with st.container(border=True):
                        # Define avatar para o feed geral
                        avatar_feed = obter_avatar_simples(row['Vereador'])

                        col_avatar, col_texto = st.columns([1, 6])
                        with col_avatar:
                            st.markdown(f"### {avatar_feed}")
                        with col_texto:
                            st.markdown(f"**{row['Vereador']}**")
                            st.caption(f"Publicado em: {row['Data']}")
                        
                        st.markdown(f"#### {row['Titulo']}")
                        st.write(row['Mensagem'])
            else:
                st.info("Ainda não há publicações no mural.")
        else:
            st.info("Mural ainda não foi iniciado.")

    # --- MODO 2: PERFIL INDIVIDUAL ---
    else:
        avatar_perfil = obter_avatar_simples(vereador_selecionado) # Usa a função para o perfil individual

        st.divider()
        col_foto, col_info = st.columns([1, 3])
        
        with col_foto:
            # Usa o avatar definido acima no tamanho grande, sem customização complexa
            st.markdown(f"<div style='font-size: 100px; text-align: center;'>{avatar_perfil}</div>", unsafe_allow_html=True)
        
        with col_info:
            st.subheader(vereador_selecionado)
            st.write("Câmara Municipal de Espumoso - RS")
            st.link_button("💬 Enviar mensagem no WhatsApp", "https://wa.me/555433834488", type="primary")
        
        st.divider()
        st.subheader(f"📰 Mural de Atividades - {vereador_selecionado}")
        
        if os.path.exists(arquivo_mural):
            df_mural = pd.read_csv(arquivo_mural)
            posts_vereador = df_mural[df_mural["Vereador"] == vereador_selecionado]
            
            if not posts_vereador.empty:
                for index, row in posts_vereador.iloc[::-1].iterrows():
                    with st.container(border=True):
                        st.caption(f"🗓️ Publicado em: {row['Data']}")
                        st.markdown(f"### {row['Titulo']}")
                        st.write(row['Mensagem'])
            else:
                st.info(f"Ainda não há publicações no mural de {vereador_selecionado}.")
        else:
            st.info("Mural ainda não foi iniciado.")

# --- TELA: ÁREA DO VEREADOR (RESTRITA) ---
elif modo == "🔐 Área do Vereador":
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
        
        aba_ia, aba_mural = st.tabs(["⚖️ Criar Documentos (IA)", "📢 Gerenciar Mural"])
        
        with aba_ia:
            st.header("Elaboração de Documentos")
            autor_selecionado = st.selectbox("Autor da Proposição:", LISTA_VEREADORES)
            tipo_doc = st.selectbox("Tipo:", ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"])
            
            if tipo_doc == "Projeto de Lei":
                st.warning("⚠️ Atenção: A IA evitará Vício de Iniciativa criando leis 'Autorizativas' quando necessário.")
            
            texto_input = st.text_area("Detalhamento da solicitação:", height=150)
            
            if st.button("📝 Elaborar Proposição"):
                if texto_input:
                    with st.spinner('Redigindo documento com rigor técnico...'):
                        texto_final = gerar_documento_ia(autor_selecionado, tipo_doc, texto_input)
                        st.session_state['minuta_pronta'] = texto_final
            
            # 2. SAÍDA (Aparece somente se houver texto gerado)
            if 'minuta_pronta' in st.session_state:
                st.subheader("Minuta Gerada:")
                
                # Exibe a minuta na caixa de texto
                minuta_para_copia = st.session_state['minuta_pronta']
                st.text_area("Texto Final da Minuta:", value=minuta_para_copia, height=500, label_visibility="collapsed")
                
                # Botões de Ação Final
                col_copy, col_softcam = st.columns([1, 1])
                
                with col_copy:
                    # O BOTÃO FINAL DE DOWNLOAD/COPIA SIMULADA (O mais robusto)
                    st.download_button(
                        label="📋 COPIAR TEXTO", 
                        data=minuta_para_copia.encode('utf-8'),
                        file_name="Minuta_Legislativa.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col_softcam:
                    # Botão para o Softcam
                    st.link_button(
                        "🌐 Ir para o Softcam", 
                        "https://www.camaraespumoso.rs.gov.br/softcam/", 
                        type="primary", 
                        use_container_width=True
                    )
            else:
                st.info("Aguardando a elaboração da minuta. Preencha o detalhamento acima.")

# --- TELA: BANCO DE IDEIAS (PÚBLICA) ---
elif modo == "💡 Banco de Ideias":
    def voltar_inicio():
        st.session_state.navegacao = "🏠 Início"
    st.button("⬅️ Voltar para o Início", on_click=voltar_inicio, key="voltar_ideias")

    st.title("Banco de Ideias - Espumoso/RS")
    st.info("Bem-vindo(a)! Envie suas sugestões construtivas para a cidade.")
    
    with st.form("form_ideia_completo", clear_on_submit=True):
        st.subheader("1. Sobre Você")
        nome = st.text_input("Seu nome completo:", help="Precisamos dos seus dados apenas para que o Vereador possa, se necessário, entrar em contato para entender melhor a sua ideia. Seus dados estarão protegidos.")
        contato = st.text_input("Seu número de celular:")
        
        st.subheader("2. Sua Ideia")
        ideia_desc = st.text_area("Descreva sua sugestão:", height=150, help='Dica: Não se preocupe em escrever bonito.')
        contribuição = st.text_area("Como isso ajuda a comunidade?", height=100)
        localizacao = st.text_input("Localização:")
        areas = st.multiselect("Áreas:", ["Saúde", "Educação", "Obras", "Lazer", "Segurança", "Trânsito", "Outros"])

        st.markdown("---")
        st.subheader("3. Destino")
        vereador = st.selectbox("Para qual vereador?", ["Escolha um vereador..."] + LISTA_VEREADORES)

        st.markdown("---")
        termos = st.checkbox("Li e concordo com os termos.")
        
        if st.form_submit_button("🚀 Enviar"):
            if termos and ideia_desc and vereador != "Escolha um vereador...":
                dados = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Nome": nome, "Contato": contato, "Ideia": ideia_desc,
                    "Contribuição": contribuição, "Localização": localizacao,
                    "Áreas": ", ".join(areas), "Vereador Destino": vereador, "Concordou Termos": "Sim"
                }
                salvar_ideia(dados)
                st.balloons()
                st.success("Enviado com sucesso!")
            else:
                st.error("Preencha os campos obrigatórios e aceite os termos.")

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