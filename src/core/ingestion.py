import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Carrega variáveis de ambiente (incluindo OPENAI_API_KEY)
load_dotenv()

# Configuração do LLM para tradução de código
# Usamos um modelo de alta capacidade para entender o código e extrair regras
llm_translator = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# Prompt para a tradução de código para regra de negócio
CODE_TO_RULE_PROMPT = """
Você é um analista de negócios e um especialista em engenharia de software.
Sua tarefa é analisar o trecho de código Python fornecido e extrair todas as regras de negócio implícitas ou explícitas em linguagem natural.
Ignore detalhes técnicos de implementação, focando apenas no 'O QUÊ' e 'POR QUE' da regra de negócio.

Formato de Saída:
Para cada regra encontrada, gere uma linha no formato:
- [TIPO: CÓDIGO] Regra de Negócio: <Regra em linguagem natural>

Exemplo:
Código: if user.age < 18: block_access()
Saída: - [TIPO: CÓDIGO] Regra de Negócio: Usuários menores de 18 anos devem ter o acesso bloqueado.

---
TRECHO DE CÓDIGO:
{code_snippet}
---
REGRAS DE NEGÓCIO EXTRAÍDAS:
"""

code_to_rule_chain = (
    PromptTemplate.from_template(CODE_TO_RULE_PROMPT)
    | llm_translator
)

def process_documents(file_path: str, doc_type: str) -> list[str]:
    """
    Carrega, divide e processa um arquivo.
    Se for código, usa o LLM para traduzir trechos em regras de negócio.
    Se for documentação, apenas divide o texto.
    """
    print(f"Processando arquivo: {file_path} como {doc_type}...")
    loader = TextLoader(file_path)
    documents = loader.load()

    # Divisor de texto para dividir o conteúdo em pedaços gerenciáveis
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    processed_rules = []
    
    if doc_type == "code":
        print(f"Traduzindo {len(chunks)} trechos de código para regras de negócio...")
        for i, chunk in enumerate(chunks):
            print(f"  -> Traduzindo trecho {i+1}/{len(chunks)}...")
            try:
                # Chama o LLM para traduzir o trecho de código
                result = code_to_rule_chain.invoke({"code_snippet": chunk.page_content})
                rules_text = result.content.strip()
                
                # Adiciona as regras extraídas
                if rules_text:
                    processed_rules.extend(rules_text.split('\n'))
            except Exception as e:
                print(f"Erro ao processar chunk de código: {e}")
                
    elif doc_type == "doc":
        print(f"Processando {len(chunks)} trechos de documentação...")
        for chunk in chunks:
            # Para documentação, apenas adicionamos um prefixo para identificação
            processed_rules.append(f"- [TIPO: DOC] Regra Documentada: {chunk.page_content.strip()}")
            
    return processed_rules

def create_vector_store(code_path: str, doc_path: str, db_path: str = "chroma_db") -> Chroma:
    """
    Cria e popula o Banco de Dados Vetorial (ChromaDB) com as regras de negócio.
    """
    # 1. Processar Código e Documentação
    code_rules = process_documents(code_path, "code")
    doc_rules = process_documents(doc_path, "doc")
    
    all_rules = code_rules + doc_rules
    
    if not all_rules:
        raise ValueError("Nenhuma regra de negócio foi extraída. Verifique os arquivos de entrada.")

    # 2. Criar Embeddings
    print(f"\nTotal de {len(all_rules)} regras extraídas. Criando embeddings...")
    # Usamos o modelo de embeddings do OpenAI (ou outro compatível)
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    # 3. Armazenar no ChromaDB
    print(f"Armazenando no ChromaDB em: {db_path}")
    vector_store = Chroma.from_texts(
        texts=all_rules,
        embedding=embeddings,
        persist_directory=db_path
    )
    # O ChromaDB agora persiste automaticamente quando persist_directory é fornecido
    print("Ingestão concluída com sucesso!")
    
    return vector_store

if __name__ == "__main__":
    # Exemplo de uso
    CODE_FILE = os.path.join("..", "..", "data", "code_example.py")
    DOC_FILE = os.path.join("..", "..", "data", "doc_example.md")
    DB_DIR = os.path.join("..", "..", "chroma_db")
    
    # Limpa o diretório do DB para um novo teste
    if os.path.exists(DB_DIR):
        import shutil
        shutil.rmtree(DB_DIR)
        
    create_vector_store(CODE_FILE, DOC_FILE, DB_DIR)
    print("\nTeste de ingestão concluído. O banco de dados vetorial está pronto.")
