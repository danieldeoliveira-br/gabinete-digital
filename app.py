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
    # Tenta obter a chave da API dos secrets do Streamlit
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = "" # Deixa vazio se não encontrar

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

# --- NOVAS LISTAS DE ACESSO ---
LISTA_JURIDICO = [
    "Assessoria Jurídica" # Adicione quantos forem necessários
]

# LISTA UNIFICADA PARA O LOGIN
LISTA_LOGIN = LISTA_VEREADORES + LISTA_JURIDICO

# --- ARQUIVOS DE DADOS GLOBAIS ---
arquivo_ideias = "banco_de_ideias.csv"
arquivo_mural = "mural_posts.csv"
arquivo_historico = "historico_proposicoes.csv" # ARQUIVO DE HISTÓRICO

# --- FUNÇÕES DE BANCO DE DADOS E SALVAMENTO ---

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

def obter_avatar_simples(nome):
    """Retorna um emoji de avatar baseado no nome do vereador."""
    if nome.startswith("Vereadora"):
        return "👩"
    else:
        return "👨"

# --- FUNÇÃO: REVISOR IA (Para revisões e novas versões) ---
def gerar_revisao_ia(texto_base, pedido_revisao, autor, tipo_doc):
    """Gera uma nova versão da minuta com base no pedido de revisão."""
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
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Ops, deu erro na IA: {e}"

def botao_copiar_para_clipboard(texto, label="📋 Copiar texto", height=70):
    """
    Insere botão que copia 'texto' para a área de transferência no navegador.
    """
    # Usa json.dumps para escapar corretamente aspas e quebras de linha complexas.
    safe_text = json.dumps(texto)
    
    html = f"""
    <div style='display: flex; align-items: center;'>
      <button id="st_copy_btn" style="
          background-color:#128C7E;
          color:white;
          border:none;
          padding:8px 12px;
          border-radius:6px;
          font-size:14px;
          cursor:pointer;
          margin-right: 10px;
      ">{label}</button>
      <span id="st_copy_msg" style="font-family: sans-serif; color: white;"></span>
    </div>

    <script>
    const btn = document.getElementById("st_copy_btn");
    const msg = document.getElementById("st_copy_msg");
    const text = {safe_text};

    async function copiarParaClipboard(t) {{
      // Try modern API first
      try {{
        await navigator.clipboard.writeText(t);
        return true;
      }} catch(e) {{
        // Fallback (older browsers/restrictions)
        try {{
          const ta = document.createElement("textarea");
          ta.value = t;
          document.body.appendChild(ta);
          ta.select();
          const ok = document.execCommand('copy');
          document.body.removeChild(ta);
          return ok;
        }} catch(err) {{
          return false;
        }}
      }}
    }}

    btn.addEventListener("click", async () => {{
      const ok = await copiarParaClipboard(text);
      if (ok) {{
        msg.innerText = "Copiado!";
        setTimeout(()=> msg.innerText = "", 2000);
        btn.innerText = "✔ Copiado";
        setTimeout(()=> btn.innerText = "{label}", 1500);
      }} else {{
        msg.innerText = "Falha ao copiar. Selecione e copie manualmente.";
      }}
    }});
    </script>
    """
    components.html(html, height=height, scrolling=False)

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
st.sidebar.caption("©2025 Câmara de Espumoso")

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
            st.markdown("#### Mural de Atividades")
            st.caption("Acompanhe as atividades e postagens dos vereadores da Câmara.")
            st.button("Visitar Gabinete Virtual 👤", use_container_width=True, on_click=ir_para_gabinete)

    st.divider()

# --- NOVO BLOCO: REDES SOCIAIS ---
    st.markdown("### Acompanhe-nos nas Redes Sociais")
    col_fb, col_ig, col_yt, col_wa_site = st.columns(4)
    
    # OBS: Substitua os links abaixo pelos endereços reais da Câmara!
    
    with col_fb:
        st.markdown("[📘 Facebook](https://facebook.com/camaraespumoso)")
    with col_ig:
        st.markdown("[📸 Instagram](https://instagram.com/camaraespumoso)")
    with col_yt:
        st.markdown("[▶️ YouTube](https://youtube.com/@camaraespumoso)")
    with col_wa_site:
        st.markdown("[🌐 Site Oficial](https://www.camaraespumoso.rs.gov.br)") # Mantém o link para o site aqui também
    
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
        contribuicao = st.text_area("Como isso ajuda a comunidade?", height=100)
        localizacao = st.text_input("Localização:", help='Dica: Bairro, Rua, Próximo a qual local, Número...')
        areas = st.multiselect("Áreas:", ["Saúde", "Educação & Cultura", "Obras", "Lazer", "Segurança", "Trânsito", "Empregabilidade", "Tecnologia", "Outros"])

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
                    "Contribuição": contribuicao, "Localização": localizacao,
                    "Áreas": ", ".join(areas), "Vereador Destino": vereador, "Concordou Termos": "Sim"
                }
                salvar_ideia(dados)
                st.balloons()
                st.success("Enviado com sucesso!")
                st.rerun() # Recarrega para limpar formulário
            else:
                st.error("Preencha os campos obrigatórios e aceite os termos.")

    # --- ÁREA ADMINISTRATIVA ---
    st.divider()
    st.subheader("🔐 Área Administrativa")
    
    # Inicializa o estado de login do admin
    if "admin_logado" not in st.session_state:
        st.session_state["admin_logado"] = False

    # --- Se NÃO estiver logado, mostra o FORMULÁRIO DE LOGIN ---
    if not st.session_state["admin_logado"]:
        with st.form("admin_login_form"):
            # Usando type="password" para mascarar, mas a senha é numérica: 123321
            senha = st.text_input("Senha ADM (Somente números):", type="password") 
            enviou = st.form_submit_button("Acessar")

        if enviou:
            if senha == "123321":
                st.session_state["admin_logado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    
    # --- Se JÁ estiver logado, mostra os dados ---
    else:
        st.success("🔓 Acesso Liberado!")
        
        if st.button("Sair do Painel ADM"):
            st.session_state["admin_logado"] = False
            st.rerun()

        if os.path.exists(arquivo_ideias):
            df = pd.read_csv(arquivo_ideias)
            st.dataframe(df, use_container_width=True)
            
            # Botão de Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Relatório", data=csv, file_name="ideias.csv", mime="text/csv")
        else:
            st.info("Nenhuma ideia registrada ainda.")

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

        # ATUALIZAÇÃO CRÍTICA: Usar a lista combinada LISTA_LOGIN
        usuario_identificado = st.selectbox("Eu sou:", ["Selecione seu nome..."] + LISTA_LOGIN) 
        senha_digitada = st.text_input("Digite a senha de acesso:", type="password")

        if st.button("Entrar"):
            # Verifica se o usuário foi selecionado
            if usuario_identificado != "Selecione seu nome..." and senha_digitada == "1955":
                st.session_state["acesso_vereador"] = True
                # CRÍTICO: Armazena o usuário logado, que pode ser Jurídico ou Vereador
                st.session_state["vereador_logado"] = usuario_identificado 
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
            autor_sessao = st.session_state["vereador_logado"]
            
            # --- LÓGICA DE PERMISSÃO DO JURÍDICO (NOVA) ---
            # 1. Verifica se o usuário logado está na lista de Jurídicos
            is_juridico = autor_sessao in LISTA_JURIDICO
            
            # 2. Define o comportamento do selectbox
            if is_juridico:
                st.info(f"Usuário logado: **{autor_sessao}**. Selecione o Vereador autor da matéria.")
                autor_list = LISTA_VEREADORES # Jurídico vê a lista de todos os vereadores
                autor_disabled = False
            else:
                st.info(f"Usuário logado: **{autor_sessao}**. Você é o autor da proposição.")
                autor_list = [autor_sessao] # Vereador só se vê na lista
                autor_disabled = True

            # O selectbox agora é dinâmico, baseado na permissão
            autor_selecionado = st.selectbox("Autor da Proposição:", autor_list, disabled=autor_disabled)
            # --- FIM DA LÓGICA DE PERMISSÃO ---

            tipo_doc = st.selectbox("Tipo:", ["Pedido de Providência", "Pedido de Informação", "Indicação", "Projeto de Lei", "Moção de Aplauso", "Moção de Pesar"])
            
            if tipo_doc == "Projeto de Lei":
                st.warning("⚠️ Atenção: A IA evitará Vício de Iniciativa criando leis 'Autorizativas' quando necessário.")
            
            texto_input = st.text_area("Detalhamento da solicitação:", height=150)
            
            if st.button("📝 Elaborar Proposição"):
                if texto_input:
                    with st.spinner('Redigindo documento com rigor técnico...'):
                        # CRÍTICO: A função usa o autor_SELECIONADO, não o autor_sessao (o logado)
                        texto_final = gerar_documento_ia(autor_selecionado, tipo_doc, texto_input) 
                        
                        prop_id_novo = datetime.now().strftime("PROP_%Y%m%d%H%M%S")
                        st.session_state['prop_id'] = prop_id_novo
                        st.session_state['prop_version_num'] = 1
                        st.session_state['minuta_pronta'] = texto_final
                        st.session_state['assunto_atual'] = texto_input
                        st.session_state['tipo_doc_atual'] = tipo_doc
                        
                        salvar_historico(
                            autor_selecionado, # CRÍTICO: Salva o autor SELECIONADO (o Vereador)
                            tipo_doc, 
                            texto_input, 
                            texto_final, 
                            prop_id_novo, 
                            1
                        )
                        st.rerun() # Rerun para exibir a minuta gerada
            
            # 2. SAÍDA (Onde a Minuta é Gerada)
            if 'minuta_pronta' in st.session_state:
                
                # --- 1. AVISO LEGAL CRÍTICO ---
                st.error("🚨 AVISO LEGAL: Este texto é uma sugestão preliminar gerada por Inteligência Artificial (IA) e pode conter erros. Não possui validade jurídica. A responsabilidade pela análise, correção, adequação formal e constitucionalidade final é integralmente do Vereador(a) autor e de sua assessoria.")
                
                # 2. MINUTA ATUAL
                st.subheader("Minuta Gerada:")

                current_version = st.session_state['prop_version_num']
                st.caption(f"Versão Atual: **V{current_version}** (Proposição ID: {st.session_state['prop_id']})")

                minuta_para_copia = st.session_state['minuta_pronta']
                st.text_area("Texto Final da Minuta:", value=minuta_para_copia, height=800, label_visibility="collapsed")
                
                # 3. INSTRUÇÃO E BOTÕES DE AÇÃO
                st.info("💡  Para copiar o texto pelo celular: Toque Longo dentro do campo - Selecionar tudo - Copiar. Depois use o botão Softcam para ir ao sistema e colar seu texto.")
                
                st.markdown("---")

                # --- 4. ÁREA DE REVISÃO E HISTÓRICO ---
                st.subheader("🔄 Revisão e Histórico")

                # REVISÃO IA
                with st.form("form_revisao_ia", clear_on_submit=False):
                    st.write(f"Peça uma revisão ou melhoria para a **Versão V{current_version}**:")
                    pedido_revisao = st.text_input("Instrução de Revisão (Ex: 'Aumente a justificativa', 'Mude a ementa', 'Melhore a linguagem'):")
                    
                    if st.form_submit_button("🔁 Gerar Nova Versão"):
                        if pedido_revisao:
                            with st.spinner('Revisando o documento com IA...'):
                                
                                # 1. Chama a IA para revisão
                                nova_minuta = gerar_revisao_ia(
                                    st.session_state['minuta_pronta'], 
                                    pedido_revisao, 
                                    autor_sessao, 
                                    st.session_state['tipo_doc_atual']
                                )
                                
                                # 2. Atualiza a versão e ID
                                nova_versao_num = st.session_state['prop_version_num'] + 1
                                prop_id_atual = st.session_state['prop_id']
                                
                                # 3. Salva a nova versão
                                salvar_historico(
                                    autor_sessao, 
                                    st.session_state['tipo_doc_atual'], 
                                    st.session_state['assunto_atual'], 
                                    nova_minuta, 
                                    prop_id_atual, 
                                    nova_versao_num
                                )
                                
                                # 4. Atualiza o estado da sessão para exibir a nova minuta
                                st.session_state['prop_version_num'] = nova_versao_num
                                st.session_state['minuta_pronta'] = nova_minuta
                                st.success(f"Nova Versão V{nova_versao_num} gerada com sucesso!")
                                st.rerun()
                        else:
                            st.error("Por favor, insira uma instrução para a revisão.")

                # HISTÓRICO DE VERSÕES (Com botão para carregar versões antigas)
                st.markdown("---")
                with st.expander(f"Histórico de Versões para Proposição {st.session_state['prop_id']}"):
                    if os.path.exists(arquivo_historico):
                        df_hist = pd.read_csv(arquivo_historico)
                        
                        # Filtra apenas o histórico desta proposição e inverte a ordem (mais novo primeiro)
                        df_prop = df_hist[df_hist["ID_PROPOSICAO"] == st.session_state['prop_id']].sort_values(by="VERSAO_NUM", ascending=False)
                        
                        for index, row in df_prop.iterrows():
                            if row['VERSAO_NUM'] == current_version:
                                st.markdown(f"**V{row['VERSAO_NUM']} - ATUAL** ({row['DATA_HORA']})")
                            else:
                                col1, col2 = st.columns([1, 4])
                                with col1:
                                    # Botão para recarregar uma versão antiga
                                    if st.button(f"↩️ Carregar V{row['VERSAO_NUM']}", key=f"load_{row['ID_PROPOSICAO']}_{row['VERSAO_NUM']}"):
                                        st.session_state['minuta_pronta'] = row['MINUTA_TEXTO']
                                        st.session_state['prop_version_num'] = row['VERSAO_NUM']
                                        st.rerun()
                                with col2:
                                    st.write(f"Versão {row['VERSAO_NUM']} de {row['DATA_HORA']}")
                    else:
                        st.caption("Nenhum histórico encontrado para esta proposição.")

                # Botão Softcam (Repetido no final da aba para acesso fácil)
                st.markdown("---")
                st.link_button(
                    "🌐 Ir para o Softcam", 
                    "https://www.camaraespumoso.rs.gov.br/softcam/", 
                    type="primary", 
                    use_container_width=True
                )
            else:
                st.info("Aguardando a elaboração da minuta. Preencha o detalhamento acima.")
        
        # --- ABA MURAL (Com correção do NameError) ---
        with aba_mural:
            st.header("📢 Publicar no Gabinete Virtual")
            
            # O autor do POST é o USUÁRIO LOGADO, não um vereador
            st.write(f"Você está postando como **{autor_sessao}**.") 
            
            with st.form("form_post_mural"):
                # O CAMPO AUTOR POST DEVE ESTAR TRAVADO NO NOME DO USUÁRIO LOGADO
                autor_post = st.selectbox("Quem está postando?", [autor_sessao], disabled=True) 
                titulo_post = st.text_input("Título da Publicação (Ex: Visita à Escola X)")
                mensagem_post = st.text_area("Texto da Publicação", height=150)
                
                if st.form_submit_button("Publicar no Mural 🚀"):
                    if titulo_post and mensagem_post:
                        dados_post = {
                            "Data": datetime.now().strftime("%d/%m/%Y"),
                            "Vereador": autor_sessao, # Postagem usa o nome logado
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
                # Carrega o DataFrame COMPLETO para permitir a separação
                df_full = pd.read_csv(arquivo_mural) 
                
                # Filtra apenas as postagens do Vereador logado para edição
                df_vereador = df_full[df_full["Vereador"] == autor_sessao].copy()
                
                if df_vereador.empty:
                    st.info("Você ainda não tem postagens no mural.")
                else:
                    df_editado = st.data_editor(df_vereador, num_rows="dynamic", use_container_width=True, key="editor_mural")
                    
                    if st.button("💾 Salvar Alterações no Mural"):
                        # 1. Separa as postagens de OUTROS vereadores
                        df_others = df_full[df_full["Vereador"] != autor_sessao] # df_full está disponível
                        
                        # 2. Concatena os posts de outros com os posts editados
                        df_combined = pd.concat([df_others, df_editado], ignore_index=True)
                        
                        # 3. Salva o DataFrame combinado
                        df_combined.to_csv(arquivo_mural, index=False)
                        st.success("Mural atualizado com sucesso!")
                        st.rerun()