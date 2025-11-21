import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components
import json
from datetime import datetime
from groq import Groq

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Legislativo Digital", page_icon="🏛️", layout="wide")

# --- CONFIGURAÇÃO DA IA ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = ""

# --- LISTAS DE ACESSO ---
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

LISTA_JURIDICO = [
    "Assessoria Jurídica"
]

# Lista unificada para o Login
LISTA_LOGIN = LISTA_VEREADORES + LISTA_JURIDICO

# --- ARQUIVOS DE DADOS ---
arquivo_ideias = "banco_de_ideias.csv"
arquivo_mural = "mural_posts.csv"
arquivo_historico = "historico_proposicoes.csv"

# --- FUNÇÕES ÚTEIS ---

def obter_avatar_simples(nome):
    if nome.startswith("Vereadora"):
        return "👩"
    else:
        return "👨"

def salvar_historico(autor, tipo, assunto, texto_minuta, versao_id, revisao_num):
    """Salva a versão atual da minuta no histórico em CSV."""
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
    """Salva uma nova ideia no Banco de Ideias."""
    if not os.path.exists(arquivo_ideias):
        df = pd.DataFrame(columns=["Data", "Nome", "Contato", "Ideia", "Contribuição", "Localização", "Áreas", "Idade", "Vereador Destino", "Concordou Termos"])
    else:
        df = pd.read_csv(arquivo_ideias)
    nova_linha = pd.DataFrame([dados])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(arquivo_ideias, index=False)

def salvar_post_mural(dados):
    """Salva uma nova postagem no Mural de Notícias."""
    if not os.path.exists(arquivo_mural):
        df = pd.DataFrame(columns=["Data", "Vereador", "Titulo", "Mensagem"])
    else:
        df = pd.read_csv(arquivo_mural)
    nova_linha = pd.DataFrame([dados])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(arquivo_mural, index=False)

# --- FUNÇÕES IA ---

# --- FUNÇÃO: REDATOR IA (Para a primeira geração) ---
def gerar_documento_ia(autor, tipo_doc, assunto):
    """Gera a primeira minuta do documento com base nas regras de técnica legislativa."""
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
        1. Inicie com: 'O Vereador que este subscreve, no uso de suas atribuições legais e regimentais...'
        2. Texto corrido, sem artigos.
        3. Seja direto na solicitação.
        """

    prompt = f"""
    Atue como um Procurador Jurídico Sênior da Câmara Municipal de Espumoso/RS.
    Redija uma minuta de {tipo_doc} com alto rigor técnico e seja formal.
    
    AUTOR: {autor}.
    ASSUNTO: {assunto}.
    
    ORDEM OBRIGATÓRIA DO DOCUMENTO (NÃO INVERTA):
    
    1. CABEÇALHO: "EXCELENTÍSSIMO SENHOR PRESIDENTE DA CÂMARA MUNICIPAL DE ESPUMOSO – RS"
    
    2. PREÂMBULO: "{autor}, integrante da Bancada [Extrair Partido], no uso de suas atribuições legais e regimentais, submete à apreciação do Plenário o seguinte {tipo_doc.upper()}:"
    
    3. EMENTA: (Resumo do assunto em caixa alta, negrito e centralizado).
    
    4. TEXTO DA PROPOSIÇÃO (AQUI ENTRAM OS ARTIGOS OU O PEDIDO):
       {regras_especificas}
    
    5. JUSTIFICATIVA (SOMENTE DEPOIS DO TEXTO DA LEI):
       Título: "JUSTIFICATIVA" (em negrito)
       Escreva um texto dissertativo-argumentativo formal defendendo a proposta.
       Foque na relevância social, jurídica e no interesse público.
    
    6. FECHAMENTO:
       "Plenário Agostinho Somavilla, {datetime.now().strftime('%d de %B de %Y').replace('January', 'Janeiro').replace('February', 'Fevereiro').replace('March', 'Março').replace('April', 'Abril').replace('May', 'Maio').replace('June', 'Junho').replace('July', 'Julho').replace('August', 'Agosto').replace('September', 'Setembro').replace('October', 'Outubro').replace('November', 'Novembro').replace('December', 'Dezembro')}."
       (Espaço para assinatura)
       {autor}
       
    IMPORTANTE: Adicione um mínimo de Duas LINHAS EM BRANCO entre cada seção principal para garantir a leitura clara em dispositivos móveis. Não use markdown de negrito (**).
    **PROIBIDO:** Não gere NENHUMA tag HTML, CSS, ou formatação de código (como `<font>`, `<div>`, etc.). Gere apenas texto puro.
    """

    try:
        chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.3)
        return chat.choices[0].message.content
    except Exception as e: return f"Erro IA: {e}"

def gerar_documento_ia(autor, tipo_doc, assunto):
    if not api_key: return "⚠️ ERRO: Chave API não encontrada!"
    client = Groq(api_key=api_key)
    
    regras = ""
    if tipo_doc == "Projeto de Lei":
        regras = "Divida em ARTIGOS numerados. Use 'Fica o Poder Executivo AUTORIZADO...' para evitar vício de iniciativa em despesas. Inclua cláusula de vigência."
    else:
        regras = "Texto corrido, sem artigos. Seja direto e formal."

    prompt = f"""
    Atue como um Procurador Jurídico Sênior da Câmara de Espumoso/RS.
    Redija minuta de {tipo_doc}.
    AUTOR: {autor}. ASSUNTO: {assunto}.
    
    ESTRUTURA OBRIGATÓRIA:
    1. CABEÇALHO: "EXCELENTÍSSIMO SENHOR PRESIDENTE..."
    2. PREÂMBULO: "{autor}, integrante da Bancada [Partido], submete..."
    3. EMENTA: (Caixa alta, resumo. Revise a ortografia).
    4. TEXTO: {regras}
    5. JUSTIFICATIVA: Título 'JUSTIFICATIVA' (em negrito). Texto dissertativo.
    6. FECHAMENTO: "Plenário Agostinho Somavilla, [Data]." Assinatura.
    
    IMPORTANTE: Adicione TRÊS LINHAS EM BRANCO entre seções para leitura no celular.
    PROIBIDO: Não gere NENHUMA tag HTML, CSS ou formatação de código. Apenas texto puro.
    """
    try:
        chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.2)
        return chat.choices[0].message.content
    except Exception as e: return f"Erro IA: {e}"


# --- MENU LATERAL ---
if os.path.exists("brasao.png"):
    st.sidebar.image("brasao.png", width=120)

st.sidebar.title("Legislativo Digital")
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
st.sidebar.markdown(f"""<a href="{link_whatsapp}" target="_blank" style="text-decoration: none;"><div style="background-color: #128C7E; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-family: sans-serif; margin-bottom: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.2);">💬 Falar no WhatsApp</div></a>""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por:")
st.sidebar.markdown("[**Daniel de Oliveira Colvero**](mailto:daniel.colvero@gmail.com)")
st.sidebar.caption("©2025 Câmara de Espumoso")

# --- TELA: INÍCIO ---
if modo == "🏠 Início":
    st.title("Legislativo Digital")
    st.write("Bem-vindo ao ambiente digital do Poder Legislativo de Espumoso!")
    st.divider()

    def ir_para_assistente(): st.session_state.navegacao = "🔐 Área do Vereador"
    def ir_para_ideias(): st.session_state.navegacao = "💡 Banco de Ideias"
    def ir_para_gabinete(): st.session_state.navegacao = "👤 Gabinete Virtual"

    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        with st.container(border=True): 
            st.markdown("## 🔐")
            st.markdown("#### Área do Vereador")
            st.caption("Acesso à IA para proposições e gestão do Mural.")
            st.button("Acessar Área Restrita 📝", use_container_width=True, on_click=ir_para_assistente)
    with col_b:
        with st.container(border=True):
            st.markdown("## 💡")
            st.markdown("#### Banco de Ideias")
            st.caption("Canal direto para sugestões da comunidade.")
            st.button("Enviar Ideia 🚀", use_container_width=True, on_click=ir_para_ideias)
    with col_c:
        with st.container(border=True):
            st.markdown("## 🏛️")
            st.markdown("#### Mural de Notícias")
            st.caption("Acompanhe as atividades dos vereadores.")
            st.button("Visitar Mural 👤", use_container_width=True, on_click=ir_para_gabinete)

    st.divider()
    st.markdown("### Acompanhe-nos nas Redes Sociais")
    
    # URLs para referência
    url_fb = "https://facebook.com/camaraespumoso"
    url_ig = "https://instagram.com/camaraespumoso"
    url_yt = "https://youtube.com/camaraespumoso"
    url_dc = "https://discord.gg/a7dGZJUx"
    url_site = "https://www.camaraespumoso.rs.gov.br"

    # Estilo sem sublinhado
    estilo = "text-decoration: none; color: #FAFAFA;"

    col_fb, col_ig, col_yt, col_dc, col_wa_site = st.columns(5)
    
    with col_fb:
        st.markdown(f'<a href="{url_fb}" style="{estilo}">📘 Facebook</a>', unsafe_allow_html=True)
    with col_ig:
        st.markdown(f'<a href="{url_ig}" style="{estilo}">📸 Instagram</a>', unsafe_allow_html=True)
    with col_yt:
        st.markdown(f'<a href="{url_yt}" style="{estilo}">▶️ YouTube</a>', unsafe_allow_html=True)
    with col_dc:
        st.markdown(f'<a href="{url_dc}" style="{estilo}">💬 Discord</a>', unsafe_allow_html=True) 
    with col_wa_site:
        st.markdown(f'<a href="{url_site}" style="{estilo}">🌐 Site Oficial</a>', unsafe_allow_html=True) 

# --- TELA: GABINETE VIRTUAL ---
elif modo == "👤 Gabinete Virtual":
    def voltar_inicio(): st.session_state.navegacao = "🏠 Início"
    st.button("⬅️ Voltar", on_click=voltar_inicio)
    
    st.header("👤 Gabinetes Virtuais")
    vereador_selecionado = st.selectbox("Selecione um vereador ou veja o Feed Geral:", ["Selecione..."] + LISTA_VEREADORES)
    
    if vereador_selecionado == "Selecione...":
        st.divider()
        st.subheader("📢 Feed de Notícias")
        if os.path.exists(arquivo_mural):
            df_mural = pd.read_csv(arquivo_mural)
            if not df_mural.empty:
                for index, row in df_mural.iloc[::-1].head(10).iterrows():
                    with st.container(border=True):
                        avatar = obter_avatar_simples(row['Vereador'])
                        c1, c2 = st.columns([1, 6])
                        with c1: st.markdown(f"### {avatar}")
                        with c2: 
                            st.markdown(f"**{row['Vereador']}**")
                            st.caption(f"Publicado em: {row['Data']}")
                        st.markdown(f"#### {row['Titulo']}")
                        st.write(row['Mensagem'])
            else: st.info("Sem publicações.")
        else: st.info("Sem publicações.")
    else:
        avatar = obter_avatar_simples(vereador_selecionado)
        st.divider()
        c1, c2 = st.columns([1, 3])
        with c1: st.markdown(f"<div style='font-size:100px;text-align:center;'>{avatar}</div>", unsafe_allow_html=True)
        with c2:
            st.subheader(vereador_selecionado)
            st.write("Câmara Municipal de Espumoso - RS")
            st.link_button("💬 WhatsApp", "https://wa.me/555433834488", type="primary")
        
        st.divider()
        st.subheader("📰 Mural de Atividades")
        if os.path.exists(arquivo_mural):
            df_mural = pd.read_csv(arquivo_mural)
            posts = df_mural[df_mural["Vereador"] == vereador_selecionado]
            if not posts.empty:
                for index, row in posts.iloc[::-1].iterrows():
                    with st.container(border=True):
                        st.caption(f"🗓️ {row['Data']}")
                        st.markdown(f"### {row['Titulo']}")
                        st.write(row['Mensagem'])
            else: st.info("Sem publicações deste vereador.")

# --- TELA: ÁREA DO VEREADOR (RESTRITA) ---
# --- TELA: ÁREA DO VEREADOR (RESTRITA) ---
elif modo == "🔐 Área do Vereador":
    def voltar_inicio():
        st.session_state.navegacao = "🏠 Início"
    st.button("⬅️ Voltar para o Início", on_click=voltar_inicio, key="voltar_assistente")

    # Inicializa ou mantém o estado de acesso
    if "acesso_vereador" not in st.session_state:
        st.session_state["acesso_vereador"] = False
    if "vereador_logado" not in st.session_state:
        st.session_state["vereador_logado"] = None 

    # --- LÓGICA DE LOGIN ---
    if not st.session_state["acesso_vereador"]:
        st.header("🔒 Acesso Restrito - Identificação")
        st.warning("Selecione seu nome e insira a senha de acesso da assessoria.")

        vereador_identificado = st.selectbox("Eu sou:", ["Selecione seu nome..."] + LISTA_LOGIN)
        senha_digitada = st.text_input("Digite a senha de acesso:", type="password")

        if st.button("Entrar"):
            if vereador_identificado != "Selecione seu nome..." and senha_digitada == "camara2025":
                st.session_state["acesso_vereador"] = True
                st.session_state["vereador_logado"] = vereador_identificado 
                st.rerun()
            else:
                st.error("Falha na autenticação. Verifique a senha e se o nome foi selecionado.")

    # --- ÁREA LOGADA (Acesso Liberado) ---
    else:
        autor_sessao = st.session_state["vereador_logado"]

        if st.button("Sair do Modo Restrito", type="secondary"):
            st.session_state["acesso_vereador"] = False
            st.session_state["vereador_logado"] = None
            st.rerun()

        st.divider()
        st.success(f"Acesso Liberado para **{autor_sessao}**.")
        
        # AQUI DEFINIMOS OS NOMES CERTOS: aba_ia e aba_mural
        aba_ia, aba_mural = st.tabs(["⚖️ Criar Documentos (IA)", "📢 Gerenciar Mural"])
        
        # --- ABA 1: INTELIGÊNCIA ARTIFICIAL ---
        with aba_ia:
            st.header("Elaboração de Documentos")
            
            # --- ÁREA DE CRIAÇÃO ---
            autor_selecionado = st.selectbox("Autor da Proposição:", [autor_sessao], disabled=True)
            tipo_doc = st.selectbox("Tipo:", ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"])
            
            if tipo_doc == "Projeto de Lei":
                st.warning("⚠️ Atenção: A IA evitará Vício de Iniciativa criando leis 'Autorizativas' quando necessário.")
            
            texto_input = st.text_area("Detalhamento da solicitação:", height=150)
            
            # O BOTÃO APENAS PROCESSA E SALVA. NÃO EXIBE NADA.
            if st.button("📝 Elaborar Proposição"):
                if texto_input:
                    with st.spinner('Redigindo documento com rigor técnico...'):
                        texto_final = gerar_documento_ia(autor_sessao, tipo_doc, texto_input)
                        
                        # Salva tudo no estado
                        prop_id_novo = datetime.now().strftime("PROP_%Y%m%d%H%M%S")
                        st.session_state['prop_id'] = prop_id_novo
                        st.session_state['prop_version_num'] = 1
                        st.session_state['minuta_pronta'] = texto_final
                        st.session_state['assunto_atual'] = texto_input
                        st.session_state['tipo_doc_atual'] = tipo_doc
                        
                        # Salva no histórico
                        salvar_historico(
                            autor_sessao, 
                            tipo_doc, 
                            texto_input, 
                            texto_final, 
                            prop_id_novo, 
                            1
                        )
                        st.rerun() # Reinicia para limpar a tela e mostrar apenas o resultado abaixo
            
            # --- ÁREA DE EXIBIÇÃO (Só aparece se existir minuta no estado) ---
            if 'minuta_pronta' in st.session_state:
                
                st.divider() # Separação visual clara
                
                # 1. AVISO LEGAL
                st.error("🚨 AVISO LEGAL: Este texto é uma sugestão preliminar gerada por Inteligência Artificial (IA). A responsabilidade pela análise e correção é do Vereador(a).")
                
                # 2. MINUTA ATUAL
                st.subheader("Minuta Gerada:")
                minuta_para_copia = st.session_state['minuta_pronta']
                
                # Exibição em Text Area (Para leitura correta no celular)
                st.text_area("Texto Final:", value=minuta_para_copia, height=800)
                
                # 3. INSTRUÇÃO DE CÓPIA
                st.info("💡 Para copiar: Selecione todo o texto acima (Long Press no celular / Ctrl+A no PC) e copie manualmente.")
                
                # Botão Softcam
                st.link_button(
                    "🌐 Ir para o Softcam", 
                    "https://www.camaraespumoso.rs.gov.br/softcam/", 
                    type="primary", 
                    use_container_width=True
                )

                # --- ÁREA DE REVISÃO ---
                st.markdown("---")
                st.subheader("🔄 Revisão e Melhoria")
                
                with st.form("revisao_form"):
                    st.write(f"Revisando Versão V{st.session_state['prop_version_num']}")
                    pedido_revisao = st.text_input("O que você quer mudar?")
                    if st.form_submit_button("🔁 Gerar Nova Versão"):
                        if pedido_revisao:
                            with st.spinner('Revisando...'):
                                nova_minuta = gerar_revisao_ia(
                                    st.session_state['minuta_pronta'], 
                                    pedido_revisao, 
                                    autor_sessao, 
                                    st.session_state['tipo_doc_atual']
                                )
                                
                                # Atualiza versão
                                nova_versao = st.session_state['prop_version_num'] + 1
                                st.session_state['prop_version_num'] = nova_versao
                                st.session_state['minuta_pronta'] = nova_minuta
                                
                                salvar_historico(
                                    autor_sessao, 
                                    st.session_state['tipo_doc_atual'], 
                                    st.session_state['assunto_atual'], 
                                    nova_minuta, 
                                    st.session_state['prop_id'], 
                                    nova_versao
                                )
                                st.rerun()

                # --- HISTÓRICO ---
                if 'prop_id' in st.session_state:
                    with st.expander("Ver Histórico de Versões"):
                         if os.path.exists(arquivo_historico):
                            df_hist = pd.read_csv(arquivo_historico)
                            df_prop = df_hist[df_hist["ID_PROPOSICAO"] == st.session_state['prop_id']].sort_values(by="VERSAO_NUM", ascending=False)
                            
                            for index, row in df_prop.iterrows():
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    if st.button(f"Carregar V{row['VERSAO_NUM']}", key=f"load_{row['VERSAO_NUM']}"):
                                        st.session_state['minuta_pronta'] = row['MINUTA_TEXTO']
                                        st.session_state['prop_version_num'] = row['VERSAO_NUM']
                                        st.rerun()
                                with col2:
                                    st.caption(f"{row['DATA_HORA']}")
            else:
                st.info("Preencha os dados acima para gerar uma nova minuta.")

        # --- ABA 2: MURAL DE NOTÍCIAS ---
        with aba_mural:
            st.header("📢 Gerenciar Mural")
            with st.form("post"):
                # Lógica para Jurídico postar em nome de vereadores
                if autor_sessao in LISTA_JURIDICO:
                    autor_post = st.selectbox("Quem está postando?", LISTA_VEREADORES)
                else:
                    autor_post = st.selectbox("Quem está postando?", [autor_sessao], disabled=True)
                
                titulo = st.text_input("Título")
                msg = st.text_area("Mensagem")
                if st.form_submit_button("Publicar"):
                    salvar_post_mural({"Data": datetime.now().strftime("%d/%m/%Y"), "Vereador": autor_post, "Titulo": titulo, "Mensagem": msg})
                    st.success("Publicado!"); st.rerun()
            
            st.divider()
            st.subheader("🗑️ Editar/Excluir Postagens")
            st.info("Edite na tabela e clique em SALVAR.")
            
            if os.path.exists(arquivo_mural):
                df_full = pd.read_csv(arquivo_mural)
                
                # Filtro de visualização
                if autor_sessao in LISTA_JURIDICO:
                     df_filter = df_full
                else:
                     df_filter = df_full[df_full["Vereador"] == autor_sessao]
                
                # Editor
                df_edit = st.data_editor(df_filter, num_rows="dynamic", key="editor_mural_key", use_container_width=True)
                
                if st.button("💾 Salvar Alterações Mural"):
                    # Lógica de salvamento
                    if autor_sessao in LISTA_JURIDICO:
                        # Jurídico salva o arquivo todo (pois viu tudo)
                        df_edit.to_csv(arquivo_mural, index=False)
                    else:
                        # Vereador só salva a parte dele mesclada com o resto
                        df_others = df_full[df_full["Vereador"] != autor_sessao]
                        pd.concat([df_others, df_edit]).to_csv(arquivo_mural, index=False)
                    st.success("Salvo!"); st.rerun()