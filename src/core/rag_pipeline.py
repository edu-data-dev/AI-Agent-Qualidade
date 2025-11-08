import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do LLM para Geração de Testes
# Usamos um modelo de alta capacidade para raciocínio e geração de texto estruturado (BDD)
llm_generator = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Prompt para a Geração Aumentada (RAG)
# O prompt instrui o LLM a agir como um especialista em QA e usar o contexto fornecido
QA_GENERATION_PROMPT = """
Você é um Analista de QA Sênior, especialista em regras de negócio e na metodologia BDD (Behavior-Driven Development).
Sua tarefa é gerar um Plano de Testes completo e detalhado no formato Gherkin (Given/When/Then) para a PERGUNTA do usuário.

O Plano de Testes DEVE ser baseado EXCLUSIVAMENTE nas REGRAS DE NEGÓCIO fornecidas no CONTEXTO.
Garanta que o plano cubra o "caminho feliz" (happy path) e todos os "caminhos de exceção" (edge cases) implícitos nas regras.
Para cada Cenário, indique a Regra de Negócio que ele está testando.

---
CONTEXTO (Regras de Negócio Relevantes):
{context}
---
PERGUNTA DO USUÁRIO:
{question}
---
PLANO DE TESTES BDD (Formato Gherkin):
"""

def setup_rag_chain(db_path: str = "chroma_db"):
    """
    Configura a cadeia RAG (Retrieval-Augmented Generation) para consultas.
    """
    # 1. Configurar Embeddings e Vector Store
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    # 2. Carregar o Banco de Dados Vetorial persistido
    print(f"Carregando Banco de Dados Vetorial de: {db_path}")
    vector_store = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )
    
    # 3. Configurar o Retriever
    # O retriever busca as regras mais relevantes (k=5)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # 4. Configurar a Cadeia RAG (LCEL)
    prompt = PromptTemplate.from_template(QA_GENERATION_PROMPT)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm_generator
    )
    
    return qa_chain, retriever

def generate_test_plan(query: str, qa_chain, retriever) -> dict:
    """
    Executa a consulta e gera o plano de testes.
    """
    print(f"\nExecutando consulta: '{query}'")
    
    # Executa a cadeia RAG
    result = qa_chain.invoke(query)
    
    # Recupera os documentos de origem separadamente para o relatório
    source_docs = retriever.invoke(query)
    
    # Formata o resultado
    test_plan = {
        "query": query,
        "test_plan": result.content,
        "source_rules": [doc.page_content for doc in source_docs]
    }
    
    return test_plan

if __name__ == "__main__":
    # Exemplo de uso (requer que o ingestion.py tenha sido executado antes)
    DB_DIR = os.path.join("..", "..", "chroma_db")
    
    # 1. Configura a cadeia RAG
    qa_chain, retriever = setup_rag_chain(DB_DIR)
    
    # 2. Executa uma consulta
    test_query = "Gere cenários de teste BDD para o cálculo de frete e aplicação de cupons."
    
    plan_result = generate_test_plan(test_query, qa_chain, retriever)
    
    print("\n--- RESULTADO DA GERAÇÃO DE TESTES ---")
    print(f"Consulta: {plan_result['query']}")
    print("\n--- REGRAS DE NEGÓCIO UTILIZADAS (CONTEXTO) ---")
    for rule in plan_result['source_rules']:
        print(f"- {rule}")
        
    print("\n--- PLANO DE TESTES BDD GERADO ---")
    print(plan_result['test_plan'])
