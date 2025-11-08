"""
Módulo de Ingestão Delta - Processa apenas arquivos alterados
=============================================================

Este módulo implementa a funcionalidade de aprendizado contínuo,
processando apenas os arquivos que foram modificados (git diff).

Ideal para integração CI/CD onde apenas deltas são ingeridos.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# ================================
# CONFIGURAÇÕES
# ================================
CHROMA_PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL = "text-embedding-ada-002"
TRANSLATION_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# ================================
# PROMPT DE TRADUÇÃO (REUTILIZADO)
# ================================
CODE_TO_RULE_PROMPT = PromptTemplate(
    template="""Você é um analista de negócios especializado em extrair regras de negócio de código-fonte.

Analise o seguinte trecho de código Python e extraia TODAS as regras de negócio (explícitas e implícitas).

Código:
{code}

Para cada regra identificada, retorne no formato:
"Regra [N]: [Descrição clara da regra em português]"

Regras:""",
    input_variables=["code"]
)


# ================================
# FUNÇÕES AUXILIARES
# ================================
def get_file_type(file_path: str) -> str:
    """Determina o tipo do arquivo (code ou doc)."""
    if file_path.endswith('.py'):
        return 'code'
    elif file_path.endswith('.md'):
        return 'doc'
    else:
        return 'unknown'


def load_document(file_path: str) -> str:
    """Carrega o conteúdo de um arquivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Erro ao carregar {file_path}: {e}")
        return ""


def translate_code_to_rules(code: str, llm: ChatOpenAI) -> str:
    """Traduz código Python em regras de negócio usando LLM."""
    try:
        chain = CODE_TO_RULE_PROMPT | llm
        response = chain.invoke({"code": code})
        return response.content
    except Exception as e:
        print(f"❌ Erro na tradução: {e}")
        return code


def process_single_file(file_path: str, llm: ChatOpenAI, splitter: CharacterTextSplitter) -> Tuple[List[str], str]:
    """Processa um único arquivo e retorna os chunks e o tipo."""
    print(f"  📄 Processando: {file_path}")
    
    file_type = get_file_type(file_path)
    content = load_document(file_path)
    
    if not content:
        return [], file_type
    
    # Se for código, traduz primeiro
    if file_type == 'code':
        print(f"    🔄 Traduzindo código em regras de negócio...")
        content = translate_code_to_rules(content, llm)
    
    # Divide em chunks
    chunks = splitter.split_text(content)
    
    # Adiciona metadados aos chunks
    chunks_with_metadata = []
    for i, chunk in enumerate(chunks):
        metadata_prefix = f"[Fonte: {os.path.basename(file_path)} | Tipo: {file_type} | Chunk: {i+1}]\n"
        chunks_with_metadata.append(metadata_prefix + chunk)
    
    print(f"    ✅ {len(chunks_with_metadata)} chunks criados")
    return chunks_with_metadata, file_type


# ================================
# FUNÇÃO PRINCIPAL DE INGESTÃO DELTA
# ================================
def process_changed_files(
    changed_files: List[str],
    db_path: str = CHROMA_PERSIST_DIR,
    force_recreate: bool = False
) -> Dict[str, int]:
    """
    Processa apenas os arquivos alterados e atualiza o banco vetorial.
    
    Args:
        changed_files: Lista de caminhos dos arquivos alterados
        db_path: Caminho do banco de dados ChromaDB
        force_recreate: Se True, recria o DB do zero
        
    Returns:
        Dicionário com estatísticas da ingestão
    """
    print("\n" + "="*60)
    print("🧠 CÉREBRO DE QA - INGESTÃO DELTA")
    print("="*60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Banco de dados: {db_path}")
    print(f"📝 Arquivos a processar: {len(changed_files)}")
    print("="*60 + "\n")
    
    # Estatísticas
    stats = {
        'total_files': len(changed_files),
        'processed_files': 0,
        'code_chunks': 0,
        'doc_chunks': 0,
        'total_chunks': 0,
        'errors': 0
    }
    
    # Inicializar componentes
    print("🔧 Inicializando componentes LangChain...")
    llm = ChatOpenAI(model=TRANSLATION_MODEL, temperature=0.1)
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    # Carregar ou criar banco vetorial
    if force_recreate or not os.path.exists(db_path):
        print("🆕 Criando novo banco de dados vetorial...")
        vector_store = None
    else:
        print("📚 Carregando banco de dados existente...")
        try:
            vector_store = Chroma(
                persist_directory=db_path,
                embedding_function=embeddings
            )
            print(f"   ✅ Banco carregado: {vector_store._collection.count()} documentos existentes")
        except Exception as e:
            print(f"   ⚠️  Erro ao carregar banco: {e}")
            print("   🆕 Criando novo banco...")
            vector_store = None
    
    # Processar cada arquivo alterado
    all_chunks = []
    all_metadatas = []
    
    print(f"\n📥 Processando {len(changed_files)} arquivo(s)...")
    
    for file_path in changed_files:
        # Ignorar arquivos que não existem mais (deletados)
        if not os.path.exists(file_path):
            print(f"  ⏭️  Ignorando arquivo deletado: {file_path}")
            continue
        
        # Ignorar arquivos de tipos não suportados
        file_type = get_file_type(file_path)
        if file_type == 'unknown':
            print(f"  ⏭️  Ignorando tipo não suportado: {file_path}")
            continue
        
        try:
            chunks, chunk_type = process_single_file(file_path, llm, splitter)
            
            if chunks:
                # Criar metadados para cada chunk
                for chunk in chunks:
                    all_chunks.append(chunk)
                    all_metadatas.append({
                        'source': file_path,
                        'type': chunk_type,
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Atualizar estatísticas
                stats['processed_files'] += 1
                if chunk_type == 'code':
                    stats['code_chunks'] += len(chunks)
                else:
                    stats['doc_chunks'] += len(chunks)
                
        except Exception as e:
            print(f"  ❌ Erro ao processar {file_path}: {e}")
            stats['errors'] += 1
    
    stats['total_chunks'] = len(all_chunks)
    
    # Adicionar chunks ao banco vetorial
    if all_chunks:
        print(f"\n💾 Adicionando {len(all_chunks)} chunks ao banco vetorial...")
        
        try:
            if vector_store is None:
                # Criar novo banco
                vector_store = Chroma.from_texts(
                    texts=all_chunks,
                    embedding=embeddings,
                    metadatas=all_metadatas,
                    persist_directory=db_path
                )
                print("   ✅ Novo banco criado com sucesso!")
            else:
                # Adicionar ao banco existente
                vector_store.add_texts(
                    texts=all_chunks,
                    metadatas=all_metadatas
                )
                print("   ✅ Chunks adicionados ao banco existente!")
            
        except Exception as e:
            print(f"   ❌ Erro ao salvar no banco: {e}")
            stats['errors'] += 1
    else:
        print("\n⚠️  Nenhum chunk foi gerado. Nada para adicionar ao banco.")
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO DA INGESTÃO DELTA")
    print("="*60)
    print(f"✅ Arquivos processados: {stats['processed_files']}/{stats['total_files']}")
    print(f"📦 Total de chunks: {stats['total_chunks']}")
    print(f"   └─ Código: {stats['code_chunks']} chunks")
    print(f"   └─ Docs:   {stats['doc_chunks']} chunks")
    if stats['errors'] > 0:
        print(f"❌ Erros: {stats['errors']}")
    print(f"⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    return stats


# ================================
# FUNÇÃO DE DETECÇÃO GIT DIFF
# ================================
def get_changed_files_from_git(base_ref: str = "HEAD^", compare_ref: str = "HEAD") -> List[str]:
    """
    Detecta arquivos alterados usando git diff.
    
    Args:
        base_ref: Referência base (ex: HEAD^, main)
        compare_ref: Referência de comparação (ex: HEAD)
        
    Returns:
        Lista de caminhos de arquivos alterados
    """
    import subprocess
    
    try:
        print(f"🔍 Detectando alterações: {base_ref}..{compare_ref}")
        
        result = subprocess.run(
            ['git', 'diff', '--name-only', base_ref, compare_ref],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        
        # Filtrar apenas .py e .md
        relevant_files = [f for f in files if f.endswith(('.py', '.md'))]
        
        print(f"   ✅ {len(relevant_files)} arquivo(s) Python/Markdown alterado(s)")
        for f in relevant_files:
            print(f"      - {f}")
        
        return relevant_files
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar git diff: {e}")
        return []


# ================================
# MAIN (para testes)
# ================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingestão Delta - Processa apenas arquivos alterados")
    parser.add_argument('--files', nargs='+', help='Lista de arquivos para processar')
    parser.add_argument('--git-diff', action='store_true', help='Detectar arquivos via git diff')
    parser.add_argument('--base', default='HEAD^', help='Referência base para git diff')
    parser.add_argument('--recreate', action='store_true', help='Recriar banco do zero')
    
    args = parser.parse_args()
    
    # Determinar arquivos a processar
    if args.git_diff:
        files = get_changed_files_from_git(base_ref=args.base)
    elif args.files:
        files = args.files
    else:
        print("❌ Erro: Especifique --files ou --git-diff")
        sys.exit(1)
    
    if not files:
        print("⚠️  Nenhum arquivo para processar")
        sys.exit(0)
    
    # Executar ingestão delta
    stats = process_changed_files(
        changed_files=files,
        force_recreate=args.recreate
    )
    
    # Exit code baseado em sucesso
    sys.exit(0 if stats['errors'] == 0 else 1)
