import os
import shutil
import sys
from core.ingestion import create_vector_store
from core.delta_ingestion import process_changed_files, get_changed_files_from_git
from core.rag_pipeline import setup_rag_chain, generate_test_plan
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Caminhos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CODE_FILE = os.path.join(DATA_DIR, "code_example.py")
DOC_FILE = os.path.join(DATA_DIR, "doc_example.md")
DB_DIR = os.path.join(PROJECT_ROOT, "chroma_db")

def run_ingestion(force_clean: bool = True):
    """
    Executa a fase de Descoberta e Indexação.
    
    Args:
        force_clean: Se True, limpa o DB antes de reingerir
    """
    print("=" * 80)
    print("FASE 1: INGESTÃO E INDEXAÇÃO")
    print("=" * 80)
    
    # Limpa o DB anterior para garantir um teste limpo
    if force_clean and os.path.exists(DB_DIR):
        print(f"\n🗑️  Limpando diretório do DB: {DB_DIR}")
        shutil.rmtree(DB_DIR)
        
    try:
        print(f"\n📂 Arquivos de entrada:")
        print(f"   - Código: {CODE_FILE}")
        print(f"   - Documentação: {DOC_FILE}")
        print(f"\n🎯 Destino: {DB_DIR}\n")
        
        create_vector_store(CODE_FILE, DOC_FILE, DB_DIR)
        
        print("\n" + "=" * 80)
        print("✅ INGESTÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        return True
    except Exception as e:
        print(f"\n❌ ERRO durante a ingestão: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_generation(query: str):
    """
    Executa a fase de Geração Aumentada (RAG).
    
    Args:
        query: Pergunta/solicitação para gerar o plano de testes
    """
    print("\n" + "=" * 80)
    print("FASE 2: GERAÇÃO DE TESTES (RAG)")
    print("=" * 80)
    
    if not os.path.exists(DB_DIR):
        print("\n❌ ERRO: Banco de Dados Vetorial não encontrado.")
        print("Execute a ingestão primeiro.")
        return False

    try:
        print(f"\n🔍 Query: {query}\n")
        
        qa_chain, retriever = setup_rag_chain(DB_DIR)
        plan_result = generate_test_plan(query, qa_chain, retriever)
        
        print("=" * 80)
        print("RESULTADO DA GERAÇÃO")
        print("=" * 80)
        
        print(f"\n📌 Consulta: {plan_result['query']}")
        
        print("\n🔗 REGRAS DE NEGÓCIO UTILIZADAS (CONTEXTO RAG):")
        print("-" * 80)
        for i, rule in enumerate(plan_result['source_rules'], 1):
            print(f"\n{i}. {rule}")
            
        print("\n\n📋 PLANO DE TESTES BDD GERADO:")
        print("=" * 80)
        print(plan_result['test_plan'])
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO durante a geração de testes: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_multiple_scenarios():
    """
    Roda múltiplos cenários de teste para validar o sistema.
    """
    print("\n" + "=" * 80)
    print("TESTE DE MÚLTIPLOS CENÁRIOS")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Cálculo de Frete Regional",
            "query": "Gere cenários de teste BDD para o cálculo de frete considerando diferentes regiões do Brasil e clientes Prime."
        },
        {
            "name": "Validação de Cupons",
            "query": "Gere cenários de teste BDD para validação de cupons promocionais (BLACKFRIDAY, NEWUSER, VIP10)."
        },
        {
            "name": "Parcelamento de Pedidos",
            "query": "Gere cenários de teste BDD para o sistema de parcelamento, incluindo regras de juros e parcela mínima."
        },
        {
            "name": "Cadastro de Cliente",
            "query": "Gere cenários de teste BDD para validação de cadastro de novos clientes, incluindo CPF, idade, email e telefone."
        },
        {
            "name": "Programa de Fidelidade",
            "query": "Gere cenários de teste BDD para o acúmulo de pontos no programa de fidelidade considerando diferentes tiers de clientes."
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'=' * 80}")
        print(f"CENÁRIO {i}/{len(scenarios)}: {scenario['name']}")
        print(f"{'=' * 80}")
        
        run_generation(scenario['query'])
        
        if i < len(scenarios):
            print("\n\n⏸️  Pressione Enter para continuar para o próximo cenário...")
            input()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Cérebro de QA - Sistema RAG para Geração de Testes')
    parser.add_argument('--skip-ingestion', action='store_true', 
                        help='Pula a etapa de ingestão (usa DB existente)')
    parser.add_argument('--delta', action='store_true',
                        help='Modo delta: processa apenas arquivos alterados (git diff)')
    parser.add_argument('--files', nargs='+',
                        help='Lista de arquivos específicos para ingestão delta')
    parser.add_argument('--multi-scenario', action='store_true',
                        help='Executa múltiplos cenários de teste')
    parser.add_argument('--query', type=str,
                        help='Query personalizada para geração de testes')
    
    args = parser.parse_args()
    
    # 1. Executa a Ingestão (se não for pulada)
    if not args.skip_ingestion:
        if args.delta:
            # Modo delta: processa apenas alterações
            print("\n🔄 MODO DELTA: Processando apenas arquivos alterados")
            
            if args.files:
                # Arquivos especificados manualmente
                changed_files = args.files
                print(f"📁 Arquivos especificados: {len(changed_files)}")
            else:
                # Detecta via git diff
                changed_files = get_changed_files_from_git()
            
            if changed_files:
                stats = process_changed_files(changed_files)
                if stats['errors'] > 0:
                    print("\n⚠️  Ingestão delta concluída com erros.")
            else:
                print("\n⚠️  Nenhum arquivo alterado detectado.")
        else:
            # Modo completo: reingestão total
            if not run_ingestion():
                print("\n❌ Falha na ingestão. Encerrando.")
                sys.exit(1)
    else:
        print("\n⏭️  Pulando ingestão (usando DB existente)")
    
    # 2. Executa a Geração de Testes
    if args.multi_scenario:
        # Múltiplos cenários
        run_multiple_scenarios()
    elif args.query:
        # Query personalizada
        run_generation(args.query)
    else:
        # Query padrão
        test_query = "Gere cenários de teste BDD para o cálculo de frete e aplicação de cupons, incluindo o caso de cliente Prime e diferentes regiões."
        run_generation(test_query)
    
    print("\n" + "=" * 80)
    print("✅ EXECUÇÃO CONCLUÍDA!")
    print("=" * 80)
    print("\n💡 O sistema 'Cérebro de QA' demonstrou capacidade de:")
    print("   1. ✅ Traduzir código Python em regras de negócio")
    print("   2. ✅ Indexar regras (código + documentação)")
    print("   3. ✅ Gerar planos de teste BDD aumentados por RAG")
    print("\n" + "=" * 80)
