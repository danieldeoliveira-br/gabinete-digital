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
       "Plenário Agostinho Somavilla, [Data de Hoje]."
       (Espaço para assinatura)
       {autor}
       Vereador(a)
       
    IMPORTANTE: Adicione um mínimo de TRÊS LINHAS EM BRANCO entre cada seção principal para garantir a leitura clara em dispositivos móveis. Não use markdown de negrito (**).
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

# --- FUNÇÕES DE BANCO DE DADOS E SALVAMENTO ---
arquivo_ideias = "banco_de_ideias.csv"
arquivo_mural = "mural_posts.csv"
arquivo_historico = "historico_proposicoes.csv"

def salvar_historico(autor, tipo, assunto, texto_minuta, versao_id, revisao_num):
    if not os.path.exists(arquivo_historico):
        df = pd.DataFrame(columns=["ID_PROPOSICAO", "VEREADOR", "TIPO_DOC", "ASSUNTO", "VERSAO_NUM", "DATA_HORA", "MINUTA_TEXTO"])
    else:
        df = pd.read_csv(arquivo_historico)
    
    nova_linha = pd.DataFrame([{
        "ID_PROPOSICAO": versao_id, 
        "VEREADOR": autor, 
        "TIPO_DOC": tipo, 
        "ASSUNTO": assunto, 
        "VERSAO_NUM": revisao_num,
        "DATA_HORA": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 
        "MINUTA_TEXTO": texto_minuta
    }])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(arquivo_historico, index=False)

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

def obter_avatar_simples(nome):
    if nome.startswith("Vereadora"):
        return "👩"
    else:
        return "👨"

def gerar_revisao_ia(texto_base, pedido_revisao, autor, tipo_doc):
    if not api_key:
        return "⚠️ ERRO: A chave da API não foi encontrada nos Secrets!"
    
    client = Groq(api_key=api_key)
    
    prompt = f"""
    Você é um Procurador Jurídico Sênior com foco em revisão textual e técnica legislativa.
    Sua tarefa é REVISAR e MELHORAR a minuta legislativa fornecida.
    
    Vereador: {autor}
    Tipo de Documento: {tipo_doc}
    Instrução de Revisão: {pedido_revisao}
    
    ---
    TEXTO ATUAL DA MINUTA:
    {texto_base}
    ---
    
    Com base no texto acima e na instrução de revisão, gere a NOVA VERSÃO da minuta. Mantenha a ESTRUTURA FORMAL e TODAS AS SEÇÕES DO DOCUMENTO.
    Garanta a correção gramatical e ortográfica em Português.
    Adicione um mínimo de TRÊS LINHAS EM BRANCO entre cada seção principal para garantir a leitura clara em dispositivos móveis.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Ops, deu erro na IA: {e}"


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
        with st.container(border=True): 
            st.markdown("## 🔐")
            st.markdown("#### Área do Vereador")
            st.caption("Acesso às ferramentas de inteligência artificial (para elaboração de documentos) e gestão do Mural de Atividades.")
            st.button("Acessar Área Restrita 📝", use_container_width=True, on_click=ir_para_assistente)
            
    with col_b:
        with st.container(border=True):
            st.markdown("## 💡")
            st.markdown("#### Banco de Ideias")
            st.caption("Canal direto para sugestões e propostas da comunidade.")
            st.button("Enviar Ideia / Sugestão 🚀", use_container_width=True, on_click=ir_para_ideias)

    with col_c:
        with st.container(border=True):
            st.markdown("## 🏛️")
            st.markdown("#### Mural de Notícias")
            st.caption("Acompanhe as atividades e postagens dos vereadores da Câmara.")
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
        avatar_perfil = obter_avatar_simples(vereador_selecionado)

        st.divider()
        col_foto, col_info = st.columns([1, 3])
        
        with col_foto:
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
    if "vereador_logado" not in st.session_state:
        st.session_state["vereador_logado"] = None 

    # --- LÓGICA DE LOGIN ---
    if not st.session_state["acesso_vereador"]:
        st.header("🔒 Acesso Restrito - Identificação")
        st.warning("Selecione seu nome e insira a senha de acesso da assessoria.")

        vereador_identificado = st.selectbox("Eu sou:", ["Selecione seu nome..."] + LISTA_VEREADORES)
        senha_digitada = st.text_input("Digite a senha de acesso:", type="password")

        if st.button("Entrar"):
            if vereador_identificado != "Selecione seu nome..." and senha_digitada == "camara2025":
                st.session_state["acesso_vereador"] = True
                st.session_state["vereador_logado"] = vereador_identificado 
                st.rerun()
            else:
                st.error("Falha na autenticação. Verifique a senha e se o nome foi selecionado.")

    # --- ÁREA LOGADA (Acesso Liberado com identidade travada) ---
    else:
        autor_sessao = st.session_state["vereador_logado"]

        if st.button("Sair do Modo Restrito", type="secondary"):
            st.session_state["acesso_vereador"] = False
            st.session_state["vereador_logado"] = None
            st.rerun()

        st.divider()
        st.success(f"Acesso Liberado para **{autor_sessao}**.")
        
        aba_ia, aba_mural = st.tabs(["⚖️ Criar Documentos (IA)", "📢 Gerenciar Mural"])
        
        with aba_ia:
            st.header("Elaboração de Documentos")
            autor_selecionado = st.selectbox("Autor da Proposição:", [autor_sessao], disabled=True)
            tipo_doc = st.selectbox("Tipo:", ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"])
            
            if tipo_doc == "Projeto de Lei":
                st.warning("⚠️ Atenção: A IA evitará Vício de Iniciativa criando leis 'Autorizativas' quando necessário.")
            
            texto_input = st.text_area("Detalhamento da solicitação:", height=150)
            
            if st.button("📝 Elaborar Proposição"):
                if texto_input:
                    with st.spinner('Redigindo documento com rigor técnico...'):
                        texto_final = gerar_documento_ia(autor_sessao, tipo_doc, texto_input)
                        st.session_state['minuta_pronta'] = texto_final
            
            # 2. SAÍDA (Onde a Minuta é Gerada)
            if 'minuta_pronta' in st.session_state:
                
                # --- AVISO LEGAL DE RESPONSABILIDADE RESTAURADO ---
                st.error("🚨 AVISO LEGAL: Este texto é uma sugestão preliminar gerada por Inteligência Artificial (IA). Não possui validade jurídica. A responsabilidade pela análise, correção, adequação formal e constitucionalidade final é integralmente do Vereador(a) autor e de sua assessoria.")
                
                st.subheader("Minuta Gerada:")
                
                minuta_para_copia = st.session_state['minuta_pronta']
                st.text_area("Texto Final da Minuta:", value=minuta_para_copia, height=500, label_visibility="collapsed")
                
                # Instrução de cópia visível
                st.info("💡 Para copiar o texto integral, selecione todo o conteúdo no campo acima (Ctrl+A no PC / Pressione e segure no celular).")
                
                # Botões de Ação Final
                st.markdown("---")
                st.link_button(
                    "🌐 Ir para o Softcam", 
                    "https://www.camaraespumoso.rs.gov.br/softcam/", 
                    type="primary", 
                    use_container_width=True
                )
            else:
                st.info("Aguardando a elaboração da minuta. Preencha o detalhamento acima.")
        
        with aba_mural:
            st.header("📢 Publicar no Gabinete Virtual")
            st.write(f"Você está postando como **{autor_sessao}**.")
            
            with st.form("form_post_mural"):
                autor_post = st.selectbox("Quem está postando?", [autor_sessao], disabled=True)
                titulo_post = st.text_input("Título da Publicação (Ex: Visita à Escola X)")
                mensagem_post = st.text_area("Texto da Publicação", height=150)
                
                if st.form_submit_button("Publicar no Mural 🚀"):
                    if titulo_post and mensagem_post:
                        dados_post = {
                            "Data": datetime.now().strftime("%d/%m/%Y"),
                            "Vereador": autor_sessao,
                            "Titulo": titulo_post,
                            "Mensagem": mensagem_post
                        }
                        salvar_post_mural(dados_post)
                        st.success("Publicado com sucesso! Veja na aba 'Gabinete Virtual'.")
                        st.rerun()
                    else:
                        st.error("Preencha título e mensagem.")
            
            st.divider()
            st.subheader("🗑️ Editar ou Excluir Postagens Antigas")
            st.info("Edite na tabela e clique em SALVAR para confirmar.")
            
            if os.path.exists(arquivo_mural):
                df_mural = pd.read_csv(arquivo_mural)
                df_vereador = df_mural[df_mural["Vereador"] == autor_sessao].copy()
                
                if df_vereador.empty:
                    st.info("Você ainda não tem postagens no mural.")
                else:
                    df_editado = st.data_editor(df_vereador, num_rows="dynamic", use_container_width=True, key="editor_mural")
                    
                    if st.button("💾 Salvar Alterações no Mural"):
                        df_others = df_full[df_full["Vereador"] != autor_sessao]
                        df_combined = pd.concat([df_others, df_editado], ignore_index=True)
                        df_combined.to_csv(arquivo_mural, index=False)
                        st.success("Mural atualizado com sucesso!")
                        st.rerun()