"""
Script de validação da ingestão de dados no ChromaDB.
Este script testa se os chunks estão sendo salvos corretamente e exibe estatísticas.
"""

import os
import sys
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(PROJECT_ROOT, "chroma_db")

def validate_vector_store():
    """
    Valida o conteúdo do vector store e exibe estatísticas detalhadas.
    """
    print("=" * 80)
    print("VALIDAÇÃO DO BANCO DE DADOS VETORIAL (ChromaDB)")
    print("=" * 80)
    
    # Verifica se o diretório existe
    if not os.path.exists(DB_DIR):
        print(f"\n❌ ERRO: Diretório do banco de dados não encontrado: {DB_DIR}")
        print("Execute a ingestão primeiro usando o botão no Streamlit ou rodando:")
        print("  python src/core/ingestion.py")
        return False
    
    print(f"\n✅ Diretório do banco de dados encontrado: {DB_DIR}")
    
    try:
        # Carrega o vector store
        print("\n📂 Carregando o vector store...")
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vector_store = Chroma(
            persist_directory=DB_DIR,
            embedding_function=embeddings
        )
        
        # Obtém a coleção
        collection = vector_store._collection
        
        # Estatísticas gerais
        total_docs = collection.count()
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   Total de documentos/chunks: {total_docs}")
        
        if total_docs == 0:
            print("\n⚠️  AVISO: Nenhum documento encontrado no banco de dados!")
            print("Execute a ingestão primeiro.")
            return False
        
        # Busca todos os documentos
        print("\n📄 Buscando todos os documentos...")
        all_docs = collection.get(
            include=['documents', 'metadatas', 'embeddings']
        )
        
        # Análise de tipos de regras
        print("\n🔍 ANÁLISE POR TIPO DE REGRA:")
        code_rules = 0
        doc_rules = 0
        
        for doc in all_docs['documents']:
            if '[TIPO: CÓDIGO]' in doc:
                code_rules += 1
            elif '[TIPO: DOC]' in doc:
                doc_rules += 1
        
        print(f"   Regras extraídas do CÓDIGO: {code_rules}")
        print(f"   Regras da DOCUMENTAÇÃO: {doc_rules}")
        
        # Análise de tamanho dos chunks
        print("\n📏 ANÁLISE DE TAMANHO DOS CHUNKS:")
        chunk_sizes = [len(doc) for doc in all_docs['documents']]
        if chunk_sizes:
            print(f"   Tamanho mínimo: {min(chunk_sizes)} caracteres")
            print(f"   Tamanho máximo: {max(chunk_sizes)} caracteres")
            print(f"   Tamanho médio: {sum(chunk_sizes) // len(chunk_sizes)} caracteres")
        
        # Exibição de exemplos
        print("\n📋 EXEMPLOS DE REGRAS ARMAZENADAS:")
        print("-" * 80)
        
        # Exemplos de regras de código
        print("\n🔹 REGRAS EXTRAÍDAS DO CÓDIGO (primeiras 5):")
        code_count = 0
        for doc in all_docs['documents']:
            if '[TIPO: CÓDIGO]' in doc and code_count < 5:
                print(f"\n   {code_count + 1}. {doc[:200]}..." if len(doc) > 200 else f"\n   {code_count + 1}. {doc}")
                code_count += 1
        
        # Exemplos de regras de documentação
        print("\n\n🔹 REGRAS DA DOCUMENTAÇÃO (primeiras 5):")
        doc_count = 0
        for doc in all_docs['documents']:
            if '[TIPO: DOC]' in doc and doc_count < 5:
                print(f"\n   {doc_count + 1}. {doc[:200]}..." if len(doc) > 200 else f"\n   {doc_count + 1}. {doc}")
                doc_count += 1
        
        # Teste de busca semântica
        print("\n\n🔍 TESTE DE BUSCA SEMÂNTICA:")
        print("-" * 80)
        
        test_queries = [
            "Como funciona o frete?",
            "Quais são as regras de cupom?",
            "Como é o parcelamento?",
            "Validação de CPF",
            "Programa de fidelidade"
        ]
        
        for query in test_queries:
            print(f"\n📌 Query: '{query}'")
            results = vector_store.similarity_search(query, k=3)
            print(f"   Resultados encontrados: {len(results)}")
            for i, result in enumerate(results, 1):
                content_preview = result.page_content[:150].replace('\n', ' ')
                print(f"   {i}. {content_preview}...")
        
        # Validação de embeddings
        print("\n\n🔬 VALIDAÇÃO DE EMBEDDINGS:")
        print("-" * 80)
        embeddings_list = all_docs.get('embeddings', [])
        if embeddings_list is not None and len(embeddings_list) > 0 and embeddings_list[0] is not None:
            print(f"   ✅ Embeddings estão sendo gerados corretamente")
            print(f"   Dimensão dos embeddings: {len(embeddings_list[0])} dimensões")
            print(f"   Exemplo de primeiros 10 valores: {embeddings_list[0][:10]}")
        else:
            print("   ⚠️  AVISO: Embeddings não encontrados!")
        
        print("\n" + "=" * 80)
        print("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO durante a validação: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_retrieval():
    """
    Testa o retrieval do RAG com queries específicas.
    """
    print("\n\n" + "=" * 80)
    print("TESTE DE RETRIEVAL RAG")
    print("=" * 80)
    
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vector_store = Chroma(
            persist_directory=DB_DIR,
            embedding_function=embeddings
        )
        
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        
        test_scenarios = [
            {
                "name": "Cenário de Frete Regional",
                "query": "Quais são as regras de frete para diferentes regiões do Brasil?",
            },
            {
                "name": "Cenário de Parcelamento",
                "query": "Como funciona o parcelamento e quais são as taxas de juros?",
            },
            {
                "name": "Cenário de Validação de Cliente",
                "query": "Quais validações são feitas no cadastro de novos clientes?",
            },
            {
                "name": "Cenário de Cupons Promocionais",
                "query": "Quais cupons estão disponíveis e suas regras de aplicação?",
            },
            {
                "name": "Cenário de Programa de Fidelidade",
                "query": "Como funciona o acúmulo de pontos no programa de fidelidade?",
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n🎯 {scenario['name']}")
            print(f"Query: {scenario['query']}")
            print("-" * 80)
            
            docs = retriever.invoke(scenario['query'])
            print(f"Documentos recuperados: {len(docs)}\n")
            
            for i, doc in enumerate(docs, 1):
                content_preview = doc.page_content[:200].replace('\n', ' ')
                print(f"{i}. {content_preview}...")
        
        print("\n" + "=" * 80)
        print("✅ TESTE DE RETRIEVAL CONCLUÍDO!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERRO durante teste de retrieval: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Iniciando validação do sistema de ingestão...")
    
    # Valida o vector store
    if validate_vector_store():
        # Se a validação passou, testa o retrieval
        test_rag_retrieval()
    else:
        print("\n⚠️  Execute a ingestão primeiro antes de validar.")
        sys.exit(1)
