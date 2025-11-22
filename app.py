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
        # Adicionei "Contribuição" na lista de colunas
        df = pd.DataFrame(columns=["Data", "Nome", "Contato", "Idade", "Ideia", "Contribuição", "Localização", "Áreas", "Vereador Destino", "Concordou Termos"])
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

# --- FUNÇÕES IA ---
def gerar_revisao_ia(texto_base, pedido_revisao, autor, tipo_doc):
    if not api_key: return "⚠️ ERRO: Chave API não encontrada!"
    client = Groq(api_key=api_key)
    prompt = f"""
    Você é um Procurador Jurídico Sênior. REVISE a minuta abaixo.
    Vereador: {autor} | Tipo: {tipo_doc} | Pedido: {pedido_revisao}
    ---
    TEXTO ATUAL:
    {texto_base}
    ---
    Gere a NOVA VERSÃO mantendo a estrutura formal. Correção gramatical impecável.
    Adicione TRÊS LINHAS EM BRANCO entre seções para leitura.
    PROIBIDO USAR HTML.
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
        regras = """
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
        regras = """
        ESTRUTURA DE TEXTO CORRIDO (Para Indicações/Pedidos):
        1. Inicie com: 'O Vereador que este subscreve, no uso de suas atribuições legais e regimentais...'
        2. Texto corrido, sem artigos.
        3. Seja direto na solicitação.
        """


    prompt = f"""
    Atue como um Procurador Jurídico Sênior da Câmara Municipal de Espumoso/RS.
    Redija minuta de {tipo_doc} com alto rigor técnico e seja formal.
    AUTOR: {autor}. 
    ASSUNTO: {assunto}.
    
    ESTRUTURA OBRIGATÓRIA:
    1. CABEÇALHO: "EXCELENTÍSSIMO SENHOR PRESIDENTE..."
    2. PREÂMBULO: "{autor}, integrante da Bancada [Extrair Partido], no uso de suas atribuições legais e regimentais, submete à apreciação do Plenário o seguinte {tipo_doc.upper()}:"
    3. EMENTA: (Caixa alta, resumo. Revise a ortografia).
    4. TEXTO (AQUI ENTRAM OS ARTIGOS OU O PEDIDO): {regras}
    5. JUSTIFICATIVA (SOMENTE DEPOIS DO TEXTO DA LEI): 
    Título 'JUSTIFICATIVA' (em negrito). Escreva um texto dissertativo-argumentativo formal defendendo a proposta. Foque na relevância social, jurídica e no interesse público
    6. FECHAMENTO: "Plenário Agostinho Somavilla, [Data]." Assinatura.
    
    IMPORTANTE: Adicione DUAS LINHAS EM BRANCO entre seções para leitura no celular.
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
    
    estilo = "text-decoration:none;color:#FAFAFA;"
    cf, ci, cy, cd, cs = st.columns(5)
    with cf: st.markdown(f'<a href="https://facebook.com/camaraespumoso" style="{estilo}">📘 Facebook</a>', unsafe_allow_html=True)
    with ci: st.markdown(f'<a href="https://instagram.com/camaraespumoso" style="{estilo}">📸 Instagram</a>', unsafe_allow_html=True)
    with cy: st.markdown(f'<a href="https://youtube.com/camaraespumoso" style="{estilo}">▶️ YouTube</a>', unsafe_allow_html=True)
    with cd: st.markdown(f'<a href="https://discord.gg/a7dGZJUx" style="{estilo}">💬 Discord</a>', unsafe_allow_html=True)
    with cs: st.markdown(f'<a href="https://www.camaraespumoso.rs.gov.br" style="{estilo}">🌐 Site Oficial</a>', unsafe_allow_html=True)

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
        
        with tab1:
            st.header("Elaboração de Documentos")
            
            if autor_sessao in LISTA_JURIDICO:
                st.info("Modo Jurídico: Selecione o autor.")
                autor_selecionado = st.selectbox("Autor:", LISTA_VEREADORES)
            else:
                autor_selecionado = st.selectbox("Autor:", [autor_sessao], disabled=True)

            tipo_doc = st.selectbox("Tipo:", ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"])
            if tipo_doc == "Projeto de Lei": st.warning("⚠️ Cuidado com Vício de Iniciativa.")
            texto_input = st.text_area("Detalhamento:", height=150)
            
            if st.button("📝 Elaborar"):
                if texto_input:
                    with st.spinner('Redigindo...'):
                        texto_final = gerar_documento_ia(autor_selecionado, tipo_doc, texto_input)
                        st.session_state['minuta_pronta'] = texto_final
                        prop_id = datetime.now().strftime("%Y%m%d%H%M%S")
                        st.session_state['prop_id'] = prop_id
                        st.session_state['prop_ver'] = 1
                        st.session_state['tipo_atual'] = tipo_doc
                        st.session_state['assunto_atual'] = texto_input
                        salvar_historico(autor_selecionado, tipo_doc, texto_input, texto_final, prop_id, 1)
                        st.rerun()
            
            if 'minuta_pronta' in st.session_state:
                st.error("🚨 AVISO LEGAL: Este texto é uma sugestão preliminar gerada por Inteligência Artificial (IA) e pode conter erros. Não possui validade jurídica. A responsabilidade pela análise, correção, adequação formal e constitucionalidade final é integralmente do Vereador(a) autor e de sua assessoria.")
                st.subheader("Minuta Gerada:")
                
                st.text_area("Texto Final:", value=st.session_state['minuta_pronta'], height=800)
                st.info("💡 Selecione todo o texto acima e copie manualmente.")
                
                st.link_button("🌐 Ir para Softcam", "https://www.camaraespumoso.rs.gov.br/softcam/", type="primary", use_container_width=True)
                
                # --- ÁREA DE REVISÃO E HISTÓRICO ---
                
                st.markdown("---")
                st.subheader("🔄 Revisão e Histórico")
                with st.form("revisao"):
                    msg_rev = st.text_input("O que melhorar? Peça uma revisão ou melhoria. Ex: 'Aumente a justificativa', 'Mude a ementa', 'Melhore a linguagem' ")
                    if st.form_submit_button("🔁 Revisar/Refazer"):
                        nova_minuta = gerar_revisao_ia(st.session_state['minuta_pronta'], msg_rev, autor_selecionado, st.session_state['tipo_atual'])
                        st.session_state['prop_ver'] += 1
                        st.session_state['minuta_pronta'] = nova_minuta
                        salvar_historico(autor_selecionado, st.session_state['tipo_atual'], st.session_state['assunto_atual'], nova_minuta, st.session_state['prop_id'], st.session_state['prop_ver'])
                        st.rerun()
            
                if 'prop_id' in st.session_state:
                    with st.expander("Histórico"):
                         if os.path.exists(arquivo_historico):
                            df_h = pd.read_csv(arquivo_historico)
                            df_p = df_h[df_h["ID_PROPOSICAO"] == st.session_state['prop_id']].sort_values(by="VERSAO_NUM", ascending=False)
                            for i, r in df_p.iterrows():
                                if st.button(f"Carregar V{r['VERSAO_NUM']}", key=f"hist_{r['VERSAO_NUM']}"):
                                    st.session_state['minuta_pronta'] = r['MINUTA_TEXTO']
                                    st.rerun()

        with tab2:
            st.header("📢 Gerenciar Mural")
            with st.form("post"):
                if autor_sessao in LISTA_JURIDICO:
                    autor_post = st.selectbox("Autor:", LISTA_VEREADORES)
                else:
                    autor_post = st.selectbox("Autor:", [autor_sessao], disabled=True)
                
                titulo = st.text_input("Título")
                msg = st.text_area("Mensagem")
                if st.form_submit_button("Publicar no Mural"):
                    salvar_post_mural({"Data": datetime.now().strftime("%d/%m/%Y"), "Vereador": autor_post, "Titulo": titulo, "Mensagem": msg})
                    st.success("Publicado!"); st.rerun()
            
            st.divider()
            st.subheader("🗑️ Editar/Excluir")
            
            if os.path.exists(arquivo_mural):
                df_full = pd.read_csv(arquivo_mural)
                
                # Filtro: Se for Jurídico vê tudo, se não, vê só o seu
                if autor_sessao in LISTA_JURIDICO:
                     df_filter = df_full
                else:
                     df_filter = df_full[df_full["Vereador"] == autor_sessao]
                
                # CORREÇÃO: Capturamos o resultado da edição na variável 'df_edit'
                df_edit = st.data_editor(df_filter, num_rows="dynamic", key="editor_mural_key", use_container_width=True)
                
                if st.button("💾 Salvar Alterações Mural"):
                    # CORREÇÃO: Usamos 'df_edit' (a tabela pronta) para salvar
                    if autor_sessao in LISTA_JURIDICO:
                        df_edit.to_csv(arquivo_mural, index=False)
                    else:
                        # Pega os posts dos outros (que não mexemos)
                        df_others = df_full[df_full["Vereador"] != autor_sessao]
                        # Junta com os nossos editados
                        pd.concat([df_others, df_edit]).to_csv(arquivo_mural, index=False)
                    
                    st.success("Salvo com sucesso!")
                    st.rerun()
            else:
                st.info("Mural vazio.")

# --- TELA: BANCO DE IDEIAS ---
elif modo == "💡 Banco de Ideias":
    def voltar_inicio(): st.session_state.navegacao = "🏠 Início"
    st.button("⬅️ Voltar", on_click=voltar_inicio)
    st.title("Banco de Ideias - Espumoso/RS"); 
    st.success("""
    **Bem-vindo(a) ao Banco de Ideias da Câmara de Espumoso!**
    Este é o seu canal direto para enviar PROPOSTAS e SUGESTÕES CONSTRUTIVAS focadas em melhorar a nossa cidade.
    Se tiver dúvidas, clique na interrogação (?) no canto de cada campo.           
    """)
    
    with st.expander("ℹ️ PARA QUE SERVE ESTE FORMULÁRIO (Clique para ler as instruções)"):
        st.markdown("""
        Use este espaço para enviar **IDEIAS de competência MUNICIPAL**, tais como:
        * **Sugestões** para novos Projetos de Lei municipais.
        * **Indicações** (Ex: "Pedir a instalação de um quebra-molas na frente da escola Y" ou "Pedir mais horários de ônibus para a localidade Z").
        * **Pedidos de Providência** (Ex: "Solicitar o conserto do buraco na Rua X").
        
        **IMPORTANTE: FOCO EM ESPUMOSO**
        Este formulário **NÃO é o canal** para manifestações gerais sobre política, nem para Reclamações ou Denúncias (para estes, use o canal de Ouvidoria).
        
        Se você tem uma **IDEIA** ou **SUGESTÃO** para Espumoso, você está no lugar certo!
        """)

    if 'sucesso_ideia' not in st.session_state: st.session_state['sucesso_ideia'] = False
    if st.session_state['sucesso_ideia']:
        st.success("✅ Enviado com sucesso!"); st.session_state['sucesso_ideia'] = False

    with st.form("ideia", clear_on_submit=False):
        nome = st.text_input("Nome:")
        contato = st.text_input("Contato (Celular/Whatsapp):", help='Utilizado caso o vereador queira entrar em contato para entender melhor a sua ideia')
        idade = st.radio("Sua Faixa Etária (Idade):", ["Menos de 18 anos", "18-30 anos", "31-45 anos", "46-60 anos", "60+"], horizontal=True)
        
        ideia = st.text_area("Descreva sua sugestão:", height=150, help='Dica: Não se preocupe em escrever bonito. Apenas nos diga o que você gostaria que fosse feito. Por exemplo: "Eu sugiro colocar um quebra-molas na Rua X..." ou "Gostaria de um projeto de aulas de violão para jovens no bairro Y..." ou "Poderiam consertar a ponte da localidade Z..."')
        
        # --- NOVO CAMPO ADICIONADO AQUI ---
        contribuicao = st.text_area("Como isso pode contribuir para a comunidade?", height=100, help='Dica: Nos diga por que sua ideia é importante. Por exemplo: "Isso evitaria acidentes com as crianças da escola..." ou "Ajudaria a tirar os jovens da rua..." ou "Melhoraria o transporte da produção..."')
        # ----------------------------------

        local = st.text_input("Localização:", help='Dica: Bairro, Rua, Próximo a qual local, Número...')
        area = st.multiselect("Área:", ["Saúde", "Agricultura & Zona Rural", "Meio Ambiente", "Educação & Cultura", "Obras", "Lazer", "Segurança", "Trânsito", "Empregabilidade", "Tecnologia", "Outros"])
        dest = st.selectbox("Enviar sugestão para qual vereador(a)?", ["Escolha um vereador..."] + LISTA_VEREADORES)

        st.markdown("### Termos de Uso")
        st.caption("""
        Ao enviar sua sugestão, você concorda que ela será, primeiramente, analisada.
        Você confirma que sua proposta é uma sugestão construtiva ou ideia focada na melhoria de Espumoso (competência municipal), e não uma reclamação, denúncia ou manifestação sobre assuntos gerais.
        No entanto, o envio não garante a implementação da ideia. As sugestões serão avaliadas de acordo com sua viabilidade, impacto e prioridades do município. Agradecemos sua participação!
        """)
        termos = st.checkbox("Li e concordo com os termos acima.")
        
        if st.form_submit_button("Enviar"):
            if termos and ideia and dest != "Escolha um vereador...":
                # Adicionei o campo "Contribuição" no dicionário de salvamento
                salvar_ideia({
                    "Data": datetime.now().strftime("%d/%m %H:%M"), 
                    "Nome": nome, 
                    "Contato": contato, 
                    "Idade": idade, 
                    "Ideia": ideia, 
                    "Contribuição": contribuicao, # <--- AQUI
                    "Localização": local, 
                    "Áreas": ", ".join(area), 
                    "Vereador Destino": dest, 
                    "Concordou Termos": "Sim"
                })
                st.session_state['sucesso_ideia'] = True; st.rerun()
            else: st.error("Preencha os campos obrigatórios (Ideia e Destino) e aceite os termos.")

    st.divider()
    st.subheader("🔐 Área Administrativa")
    
    # Verifica login
    if "admin_logado" not in st.session_state:
        st.session_state["admin_logado"] = False

    # TELA DE LOGIN (Formulário único para não duplicar senha)
    if not st.session_state["admin_logado"]:
        with st.form("login_admin_form"):
            senha = st.text_input("Senha ADM (Somente números):", type="password")
            if st.form_submit_button("Acessar"):
                if senha == "12345":
                    st.session_state["admin_logado"] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
    
    # TELA LOGADA (Tabela Editável)
    else:
        if st.button("Sair Admin"):
            st.session_state["admin_logado"] = False
            st.rerun()
            
        if os.path.exists(arquivo_ideias):
            df = pd.read_csv(arquivo_ideias)
            
            st.info("📝 Para apagar uma linha: Selecione-a e aperte DELETE no teclado. Depois clique em SALVAR.")
            
            # --- TABELA EDITÁVEL (Igual ao Mural) ---
            df_editado = st.data_editor(
                df, 
                num_rows="dynamic", # ISSO PERMITE ADICIONAR/REMOVER LINHAS
                key="editor_ideias_admin", 
                use_container_width=True
            )
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Salvar Alterações na Tabela", use_container_width=True):
                    # Salva o que você viu na tela (df_editado) no arquivo
                    df_editado.to_csv(arquivo_ideias, index=False)
                    st.success("Tabela atualizada com sucesso!")
                    st.rerun()
            with c2:
                st.download_button(
                    "📥 Baixar CSV", 
                    data=df.to_csv(index=False).encode('utf-8'), 
                    file_name="ideias.csv", 
                    mime="text/csv", 
                    use_container_width=True
                )
        else:
            st.info("Nenhuma ideia registrada ainda.")