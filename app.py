import streamlit as st
import os
import shutil
from src.core.ingestion import create_vector_store
from src.core.rag_pipeline import setup_rag_chain, generate_test_plan
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# --- Configurações de Caminho ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CODE_FILE = os.path.join(DATA_DIR, "code_example.py")
DOC_FILE = os.path.join(DATA_DIR, "doc_example.md")
DB_DIR = os.path.join(PROJECT_ROOT, "chroma_db")

# --- Funções de Estado e Cache ---

@st.cache_resource
def get_rag_components():
    """
    Configura e retorna a cadeia RAG e o retriever, usando cache para evitar reprocessamento.
    """
    if not os.path.exists(DB_DIR):
        st.error("Banco de Dados Vetorial não encontrado. Execute a Ingestão primeiro.")
        return None, None
    
    try:
        qa_chain, retriever = setup_rag_chain(DB_DIR)
        return qa_chain, retriever
    except Exception as e:
        st.error(f"Erro ao configurar a cadeia RAG: {e}")
        return None, None

def run_ingestion_ui():
    """
    Executa a fase de Descoberta e Indexação e atualiza o estado da aplicação.
    """
    st.session_state.ingestion_status = "Em andamento..."
    st.session_state.db_ready = False
    
    # Limpa o DB anterior
    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)
        
    try:
        # A função create_vector_store já faz a persistência
        create_vector_store(CODE_FILE, DOC_FILE, DB_DIR)
        st.session_state.ingestion_status = "Concluída com Sucesso!"
        st.session_state.db_ready = True
        st.cache_resource.clear() # Limpa o cache para recarregar o novo DB
    except Exception as e:
        st.session_state.ingestion_status = f"Erro: {e}"
        st.error(f"Erro durante a ingestão: {e}")

# --- Interface Streamlit ---

st.set_page_config(page_title="Cérebro de QA", layout="wide")
st.title("🧠 Cérebro de QA: Cobertura de testes ampliada com IA")

# Inicialização do estado da sessão
if 'db_ready' not in st.session_state:
    st.session_state.db_ready = os.path.exists(DB_DIR)
if 'ingestion_status' not in st.session_state:
    st.session_state.ingestion_status = "Aguardando Ingestão"

# --- Sidebar de Controle ---
st.sidebar.header("Controle do Cérebro")

# Botão de Ingestão
if st.sidebar.button("1. Iniciar Ingestão (Criar/Atualizar DB)"):
    run_ingestion_ui()

st.sidebar.markdown("---")
st.sidebar.subheader("Status do Banco de Dados Vetorial")
st.sidebar.info(f"Status: **{st.session_state.ingestion_status}**")
st.sidebar.success(f"DB Pronto: {'Sim' if st.session_state.db_ready else 'Não'}")

# --- Área Principal (Geração de Testes) ---

st.header("2. Geração de Planos de Teste BDD")

if st.session_state.db_ready:
    qa_chain, retriever = get_rag_components()
    
    if qa_chain and retriever:
        query = st.text_area(
            "Insira a funcionalidade para a qual deseja gerar o Plano de Testes:",
            "Gere cenários de teste BDD para o cálculo de frete e aplicação de cupons, incluindo o caso de cliente Prime."
        )
        
        if st.button("Gerar Plano de Testes"):
            with st.spinner("Buscando regras e gerando plano de testes..."):
                try:
                    plan_result = generate_test_plan(query, qa_chain, retriever)
                    
                    st.subheader("📋 Plano de Testes BDD Gerado")
                    st.code(plan_result['test_plan'], language='gherkin')
                    
                    st.subheader("🔗 Regras de Negócio Utilizadas (Contexto RAG)")
                    st.info(f"Total de {len(plan_result['source_rules'])} regras recuperadas do banco de dados vetorial")
                    
                    # Separar regras por tipo
                    code_rules = []
                    doc_rules = []
                    
                    for rule in plan_result['source_rules']:
                        if '[TIPO: CÓDIGO]' in rule:
                            code_rules.append(rule)
                        elif '[TIPO: DOC]' in rule:
                            doc_rules.append(rule)
                    
                    # Exibir regras de código
                    if code_rules:
                        with st.expander(f"🔹 Regras Extraídas do CÓDIGO ({len(code_rules)} regras)", expanded=True):
                            for i, rule in enumerate(code_rules, 1):
                                # Remove o prefixo para exibição mais limpa
                                clean_rule = rule.replace('- [TIPO: CÓDIGO] Regra de Negócio: ', '')
                                st.markdown(f"**{i}.** {clean_rule}")
                    
                    # Exibir regras de documentação
                    if doc_rules:
                        with st.expander(f"📄 Regras da DOCUMENTAÇÃO ({len(doc_rules)} regras)", expanded=True):
                            for i, rule in enumerate(doc_rules, 1):
                                # Remove o prefixo para exibição mais limpa
                                clean_rule = rule.replace('- [TIPO: DOC] Regra Documentada: ', '')
                                st.markdown(f"**{i}.** {clean_rule}")
                        
                except Exception as e:
                    st.error(f"Erro na Geração de Testes. Verifique a chave de API e o status do DB. Erro: {e}")
    else:
        st.warning("Não foi possível configurar a cadeia RAG. Verifique o status na barra lateral.")
else:
    st.warning("O Banco de Dados Vetorial (Cérebro) não está pronto. Por favor, clique em 'Iniciar Ingestão' na barra lateral.")
