"""
Script de Simulação CI/CD Local
=================================

Este script simula o comportamento do pipeline CI/CD localmente,
permitindo testar a funcionalidade de aprendizado contínuo antes
de fazer push para o GitHub.

Uso:
    python test_cicd_local.py
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.delta_ingestion import get_changed_files_from_git, process_changed_files


def print_header(title: str):
    """Imprime um cabeçalho bonito."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def check_git_repo():
    """Verifica se estamos em um repositório git."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_current_branch():
    """Obtém o nome da branch atual."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def get_last_commit_info():
    """Obtém informações do último commit."""
    try:
        # Hash do commit
        hash_result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = hash_result.stdout.strip()
        
        # Mensagem do commit
        msg_result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            capture_output=True,
            text=True,
            check=True
        )
        commit_msg = msg_result.stdout.strip()
        
        return commit_hash, commit_msg
    except subprocess.CalledProcessError:
        return "unknown", "unknown"


def simulate_cicd_pipeline():
    """Simula o pipeline CI/CD completo."""
    print_header("🧠 SIMULAÇÃO DE PIPELINE CI/CD - CÉREBRO DE QA")
    
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Verificar se é um repo git
    print("1️⃣ Verificando repositório Git...")
    if not check_git_repo():
        print("   ❌ Este não é um repositório Git!")
        print("   💡 Inicialize com: git init")
        return False
    print("   ✅ Repositório Git detectado\n")
    
    # 2. Obter informações do repositório
    print("2️⃣ Coletando informações do repositório...")
    branch = get_current_branch()
    commit_hash, commit_msg = get_last_commit_info()
    print(f"   📌 Branch: {branch}")
    print(f"   📝 Último commit: {commit_hash}")
    print(f"   💬 Mensagem: {commit_msg}\n")
    
    # 3. Detectar arquivos alterados
    print("3️⃣ Detectando arquivos alterados (git diff HEAD^ HEAD)...")
    changed_files = get_changed_files_from_git()
    
    if not changed_files:
        print("   ⚠️  Nenhum arquivo Python ou Markdown foi alterado")
        print("   💡 Modifique um arquivo em data/ e faça commit para testar")
        return False
    
    print(f"   ✅ {len(changed_files)} arquivo(s) alterado(s) detectado(s)\n")
    
    # 4. Processar ingestão delta
    print("4️⃣ Executando ingestão delta...")
    print("   (Processando apenas os arquivos alterados)\n")
    
    stats = process_changed_files(
        changed_files=changed_files,
        force_recreate=False
    )
    
    # 5. Validar resultados
    print("\n5️⃣ Validando resultados...")
    
    if stats['errors'] > 0:
        print(f"   ⚠️  Ingestão concluída com {stats['errors']} erro(s)")
        return False
    
    if stats['total_chunks'] == 0:
        print("   ⚠️  Nenhum chunk foi criado")
        return False
    
    print("   ✅ Validação bem-sucedida!\n")
    
    # 6. Relatório final
    print_header("📊 RELATÓRIO FINAL DA SIMULAÇÃO")
    
    print(f"✅ Pipeline executado com sucesso!")
    print(f"\n📈 Estatísticas:")
    print(f"   • Arquivos processados: {stats['processed_files']}/{stats['total_files']}")
    print(f"   • Total de chunks: {stats['total_chunks']}")
    print(f"   • Chunks de código: {stats['code_chunks']}")
    print(f"   • Chunks de documentação: {stats['doc_chunks']}")
    print(f"   • Erros: {stats['errors']}")
    
    print(f"\n🧠 Base de Conhecimento:")
    print(f"   • Status: ATUALIZADA")
    print(f"   • Localização: ./chroma_db/")
    print(f"   • Pronto para gerar testes!")
    
    print(f"\n⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 70)
    print("🎉 SIMULAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    
    print("\n💡 Próximos passos:")
    print("   1. Teste a geração de testes com: streamlit run app.py")
    print("   2. Ou use o CLI: python src/main.py --skip-ingestion --query 'sua query'")
    print("   3. Quando estiver satisfeito, faça push: git push origin main")
    print("   4. O GitHub Actions executará o pipeline automaticamente!\n")
    
    return True


def quick_test():
    """Teste rápido com arquivos específicos."""
    print_header("🚀 TESTE RÁPIDO - INGESTÃO DELTA")
    
    # Arquivos padrão para teste
    test_files = [
        'data/code_example.py',
        'data/doc_example.md'
    ]
    
    # Verificar se existem
    existing_files = [f for f in test_files if os.path.exists(f)]
    
    if not existing_files:
        print("❌ Arquivos de teste não encontrados!")
        print("💡 Certifique-se de que data/code_example.py e data/doc_example.md existem\n")
        return False
    
    print(f"📁 Processando {len(existing_files)} arquivo(s) de teste...")
    for f in existing_files:
        print(f"   - {f}")
    print()
    
    stats = process_changed_files(
        changed_files=existing_files,
        force_recreate=False
    )
    
    if stats['errors'] == 0 and stats['total_chunks'] > 0:
        print("\n✅ Teste rápido bem-sucedido!")
        print(f"📊 {stats['total_chunks']} chunks processados\n")
        return True
    else:
        print("\n❌ Teste rápido falhou\n")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Simulação de Pipeline CI/CD')
    parser.add_argument('--quick', action='store_true',
                        help='Teste rápido sem usar git diff')
    
    args = parser.parse_args()
    
    try:
        if args.quick:
            success = quick_test()
        else:
            success = simulate_cicd_pipeline()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
