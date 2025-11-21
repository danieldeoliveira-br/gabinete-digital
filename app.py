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

# --- FUNÇÕES IA (RESTAURADAS COM A SUA LÓGICA COMPLETA) ---

def gerar_revisao_ia(texto_base, pedido_revisao, autor, tipo_doc):
    if not api_key: return "⚠️ ERRO: Chave API não encontrada!"
    client = Groq(api_key=api_key)
    prompt = f"""
    Você é um Procurador Jurídico Sênior com foco em revisão textual.
    Vereador: {autor} | Tipo: {tipo_doc} | Pedido: {pedido_revisao}
    ---
    TEXTO ATUAL:
    {texto_base}
    ---
    Gere a NOVA VERSÃO mantendo a estrutura formal. Correção gramatical impecável.
    Adicione TRÊS LINHAS EM BRANCO entre seções. PROIBIDO HTML.
    """
    try:
        chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.3)
        return chat.choices[0].message.content
    except Exception as e: return f"Erro IA: {e}"

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
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Ops, deu erro na IA: {e}"


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
elif modo == "🔐 Área do Vereador":
    def voltar_inicio(): st.session_state.navegacao = "🏠 Início"
    st.button("⬅️ Voltar", on_click=voltar_inicio)

    if "acesso_vereador" not in st.session_state: st.session_state["acesso_vereador"] = False
    if "vereador_logado" not in st.session_state: st.session_state["vereador_logado"] = None 

    if not st.session_state["acesso_vereador"]:
        st.header("🔒 Acesso Restrito - Identificação")
        st.warning("Selecione seu nome e insira a senha de acesso.")
        
        # Lista completa para login
        usuario_identificado = st.selectbox("Eu sou:", ["Selecione..."] + LISTA_LOGIN)
        senha_digitada = st.text_input("Senha:", type="password")
        
        if st.button("Entrar"):
            if usuario_identificado != "Selecione..." and senha_digitada == "camara2025":
                st.session_state["acesso_vereador"] = True
                st.session_state["vereador_logado"] = usuario_identificado 
                st.rerun()
            else: st.error("Dados incorretos.")
    else:
        autor_sessao = st.session_state["vereador_logado"]
        if st.button("Sair", type="secondary"):
            st.session_state["acesso_vereador"] = False; st.session_state["vereador_logado"] = None; st.rerun()

        st.success(f"Logado como: **{autor_sessao}**")
        tab1, tab2 = st.tabs(["⚖️ Criar Documentos", "📢 Gerenciar Mural"])
        
        # --- ABA 1: IA ---
        with tab1:
            st.header("Elaboração de Documentos")
            
            # Campo travado
            autor_selecionado = st.selectbox("Autor:", [autor_sessao], disabled=True)

            tipo_doc = st.selectbox("Tipo:", ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"])
            if tipo_doc == "Projeto de Lei": st.warning("⚠️ Cuidado com Vício de Iniciativa.")
            texto_input = st.text_area("Detalhamento:", height=150)
            
            if st.button("📝 Elaborar"):
                if texto_input:
                    with st.spinner('Redigindo...'):
                        texto_final = gerar_documento_ia(autor_sessao, tipo_doc, texto_input)
                        st.session_state['minuta_pronta'] = texto_final
                        prop_id = datetime.now().strftime("%Y%m%d%H%M%S")
                        st.session_state['prop_id'] = prop_id
                        st.session_state['prop_ver'] = 1
                        st.session_state['tipo_atual'] = tipo_doc
                        st.session_state['assunto_atual'] = texto_input
                        salvar_historico(autor_sessao, tipo_doc, texto_input, texto_final, prop_id, 1)
                        st.rerun()
            
            if 'minuta_pronta' in st.session_state:
                st.error("🚨 AVISO LEGAL: IA pode cometer erros. Revise antes de usar.")
                st.subheader("Minuta Gerada:")
                
                # VISUALIZAÇÃO LIMPA
                st.text_area("Texto Final:", value=st.session_state['minuta_pronta'], height=800)
                
                # CÓPIA COM ÍCONE NATIVO DO ST.CODE (A única que funciona 100%)
                st.code(st.session_state['minuta_pronta'], language="markdown")
                st.info("💡 Use o ícone de cópia acima.")
                
                st.link_button("🌐 Ir para Softcam", "https://www.camaraespumoso.rs.gov.br/softcam/", type="primary", use_container_width=True)
                
                st.markdown("---")
                st.subheader("🔄 Revisão")
                with st.form("revisao"):
                    current_ver = st.session_state['prop_ver']
                    st.write(f"Revisar V{current_ver}")
                    msg_rev = st.text_input("O que melhorar?")
                    if st.form_submit_button("🔁 Revisar"):
                        nova_minuta = gerar_revisao_ia(st.session_state['minuta_pronta'], msg_rev, autor_selecionado, st.session_state['tipo_atual'])
                        st.session_state['prop_ver'] += 1
                        st.session_state['minuta_pronta'] = nova_minuta
                        salvar_historico(autor_selecionado, st.session_state['tipo_atual'], st.session_state['assunto_atual'], nova_minuta, st.session_state['prop_id'], st.session_state['prop_ver'])
                        st.rerun()
            
                # Histórico
                if 'prop_id' in st.session_state:
                    with st.expander("Histórico"):
                         if os.path.exists(arquivo_historico):
                            df_h = pd.read_csv(arquivo_historico)
                            df_p = df_h[df_h["ID_PROPOSICAO"] == st.session_state['prop_id']].sort_values(by="VERSAO_NUM", ascending=False)
                            for i, r in df_p.iterrows():
                                if st.button(f"Carregar V{r['VERSAO_NUM']}", key=f"hist_{r['VERSAO_NUM']}"):
                                    st.session_state['minuta_pronta'] = r['MINUTA_TEXTO']
                                    st.rerun()

        # --- ABA 2: MURAL ---
        with tab2:
            st.header("📢 Gerenciar Mural")
            with st.form("post"):
                autor_post = st.selectbox("Autor:", [autor_sessao], disabled=True)
                titulo = st.text_input("Título")
                msg = st.text_area("Mensagem")
                if st.form_submit_button("Publicar"):
                    salvar_post_mural({"Data": datetime.now().strftime("%d/%m/%Y"), "Vereador": autor_post, "Titulo": titulo, "Mensagem": msg})
                    st.success("Publicado!"); st.rerun()
            
            st.divider()
            st.subheader("🗑️ Editar/Excluir")
            
            if os.path.exists(arquivo_mural):
                df_full = pd.read_csv(arquivo_mural)
                # Se for Jurídico, vê tudo. Se for vereador, vê só o seu.
                if "Jurídica" in autor_sessao:
                     df_filter = df_full
                else:
                     df_filter = df_full[df_full["Vereador"] == autor_sessao]
                
                # Editor COM CHAVE DE ESTADO
                df_edit = st.data_editor(df_filter, num_rows="dynamic", key="editor_mural_key", use_container_width=True)
                
                if st.button("💾 Salvar Alterações Mural"):
                    # Salva misturando com os dados dos outros que não foram tocados
                    # Lê do estado para garantir
                    df_final_editado = st.session_state["editor_mural_key"]
                    
                    if "Jurídica" in autor_sessao:
                        df_final_editado.to_csv(arquivo_mural, index=False)
                    else:
                        df_others = df_full[df_full["Vereador"] != autor_sessao]
                        pd.concat([df_others, df_final_editado]).to_csv(arquivo_mural, index=False)
                    st.success("Salvo!"); st.rerun()

# --- TELA: BANCO DE IDEIAS ---
elif modo == "💡 Banco de Ideias":
    def voltar_inicio(): st.session_state.navegacao = "🏠 Início"
    st.button("⬅️ Voltar", on_click=voltar_inicio)
    st.title("Banco de Ideias"); st.info("Envie sua sugestão.")
    
    with st.form("ideia", clear_on_submit=False):
        nome = st.text_input("Nome:")
        contato = st.text_input("Contato:")
        idade = st.radio("Idade:", ["-18", "18-30", "31-45", "46-60", "60+"], horizontal=True)
        ideia = st.text_area("Ideia:")
        local = st.text_input("Local:")
        area = st.multiselect("Área:", ["Saúde", "Educação", "Obras", "Outros"])
        dest = st.selectbox("Para:", ["Escolha..."] + LISTA_VEREADORES)
        termos = st.checkbox("Concordo com os termos.")
        
        if st.form_submit_button("Enviar"):
            if termos and ideia and dest != "Escolha...":
                salvar_ideia({"Data": datetime.now().strftime("%d/%m %H:%M"), "Nome": nome, "Contato": contato, "Idade": idade, "Ideia": ideia, "Localização": local, "Áreas": ", ".join(area), "Vereador Destino": dest, "Concordou Termos": "Sim"})
                st.balloons()
                st.success("✅ Enviado com sucesso! Limpe os campos para novo envio.")
            else: st.error("Preencha tudo.")

    st.divider()
    st.subheader("🔐 Área Administrativa")
    senha = st.text_input("Senha ADM (Números):", type="password")
    
    if "admin_logado" not in st.session_state: st.session_state["admin_logado"] = False
    
    if not st.session_state["admin_logado"]:
        if st.button("Acessar Admin"):
            if senha == "12345": st.session_state["admin_logado"] = True; st.rerun()
            else: st.error("Senha incorreta.")
    else:
        if st.button("Sair Admin"): st.session_state["admin_logado"] = False; st.rerun()
        
        st.subheader("Gerenciar Ideias")
        st.caption("Selecione linhas e aperte Delete para apagar.")
        
        if os.path.exists(arquivo_ideias):
            df = pd.read_csv(arquivo_ideias)
            
            # Editor Admin com CHAVE DE ESTADO
            st.data_editor(df, num_rows="dynamic", key="editor_ideias_admin", use_container_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Salvar Tabela"):
                    # Salva direto do estado
                    st.session_state["editor_ideias_admin"].to_csv(arquivo_ideias, index=False)
                    st.success("Salvo!"); st.rerun()
            with c2:
                st.download_button("📥 Baixar CSV", df.to_csv(index=False).encode('utf-8'), "ideias.csv", "text/csv")
        else: st.info("Sem dados.")