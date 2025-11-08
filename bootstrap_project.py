"""
Módulo de Bootstrap - Ingestão Inicial Completa
================================================

Este módulo é responsável pela PRIMEIRA INGESTÃO do projeto,
processando TODO o código-fonte e documentação para criar
a base de conhecimento inicial do Cérebro de QA.

Diferença entre Bootstrap e Delta:
- Bootstrap: Primeira vez, processa TUDO
- Delta: Execuções posteriores, processa apenas mudanças

Uso:
    python bootstrap_project.py --project-path /caminho/do/projeto
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import argparse

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

# Extensões de arquivo suportadas
SUPPORTED_EXTENSIONS = {
    'code': ['.py', '.java', '.js', '.ts', '.jsx', '.tsx', '.cs', '.cpp', '.c', '.go', '.rb', '.php'],
    'doc': ['.md', '.txt', '.rst', '.adoc'],
    'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.xml']
}

# Diretórios a ignorar
IGNORE_DIRS = {
    '__pycache__', 'node_modules', '.git', '.venv', 'venv', 
    'env', 'build', 'dist', 'target', '.pytest_cache', 
    '.mypy_cache', 'coverage', '.idea', '.vscode', 'chroma_db'
}


# ================================
# PROMPT DE TRADUÇÃO
# ================================
CODE_TO_RULE_PROMPT = PromptTemplate(
    template="""Você é um analista de negócios especializado em extrair regras de negócio de código-fonte.

Analise o seguinte trecho de código e extraia TODAS as regras de negócio (explícitas e implícitas).

Arquivo: {filename}
Tipo: {filetype}

Código:
{code}

Para cada regra identificada, retorne no formato:
"Regra [N]: [Descrição clara da regra em português]"

Regras:""",
    input_variables=["code", "filename", "filetype"]
)


# ================================
# FUNÇÕES DE DESCOBERTA
# ================================
def discover_files(project_path: str, extensions: List[str]) -> List[str]:
    """
    Descobre recursivamente todos os arquivos relevantes no projeto.
    
    Args:
        project_path: Caminho raiz do projeto
        extensions: Lista de extensões para buscar (ex: ['.py', '.md'])
        
    Returns:
        Lista de caminhos absolutos dos arquivos encontrados
    """
    discovered_files = []
    project_path = Path(project_path).resolve()
    
    print(f"🔍 Escaneando diretório: {project_path}")
    print(f"📋 Extensões: {', '.join(extensions)}")
    print(f"🚫 Ignorando: {', '.join(IGNORE_DIRS)}\n")
    
    for root, dirs, files in os.walk(project_path):
        # Remove diretórios ignorados da busca
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                discovered_files.append(file_path)
    
    return discovered_files


def categorize_files(files: List[str]) -> Dict[str, List[str]]:
    """
    Categoriza arquivos por tipo (código, documentação, configuração).
    
    Args:
        files: Lista de caminhos de arquivos
        
    Returns:
        Dicionário com categorias e listas de arquivos
    """
    categorized = {
        'code': [],
        'doc': [],
        'config': []
    }
    
    for file_path in files:
        ext = Path(file_path).suffix.lower()
        
        for category, extensions in SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                categorized[category].append(file_path)
                break
    
    return categorized


# ================================
# FUNÇÕES DE PROCESSAMENTO
# ================================
def translate_code_to_rules(code: str, filename: str, filetype: str, llm: ChatOpenAI) -> str:
    """Traduz código em regras de negócio usando LLM."""
    try:
        chain = CODE_TO_RULE_PROMPT | llm
        response = chain.invoke({
            "code": code,
            "filename": filename,
            "filetype": filetype
        })
        return response.content
    except Exception as e:
        print(f"  ⚠️  Erro na tradução de {filename}: {e}")
        return code  # Fallback: usa o código original


def process_file(
    file_path: str, 
    category: str,
    llm: ChatOpenAI, 
    splitter: CharacterTextSplitter
) -> Tuple[List[str], List[Dict]]:
    """
    Processa um único arquivo e retorna chunks + metadados.
    
    Args:
        file_path: Caminho do arquivo
        category: Categoria (code, doc, config)
        llm: Modelo LLM para tradução
        splitter: Divisor de texto
        
    Returns:
        Tupla (chunks, metadados)
    """
    try:
        # Ler conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not content.strip():
            return [], []
        
        filename = os.path.basename(file_path)
        filetype = Path(file_path).suffix
        
        # Se for código, traduz em regras
        if category == 'code':
            print(f"    🔄 Traduzindo {filename}...")
            content = translate_code_to_rules(content, filename, filetype, llm)
        
        # Divide em chunks
        chunks = splitter.split_text(content)
        
        # Cria metadados para cada chunk
        chunks_with_metadata = []
        metadatas = []
        
        relative_path = file_path.replace('\\', '/')
        
        for i, chunk in enumerate(chunks):
            # Adiciona cabeçalho ao chunk
            header = f"[Arquivo: {filename} | Tipo: {category} | Chunk: {i+1}/{len(chunks)}]\n"
            full_chunk = header + chunk
            
            # Metadados
            metadata = {
                'source': relative_path,
                'filename': filename,
                'type': category,
                'filetype': filetype,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'timestamp': datetime.now().isoformat()
            }
            
            chunks_with_metadata.append(full_chunk)
            metadatas.append(metadata)
        
        print(f"    ✅ {filename}: {len(chunks)} chunks")
        return chunks_with_metadata, metadatas
        
    except Exception as e:
        print(f"    ❌ Erro ao processar {file_path}: {e}")
        return [], []


# ================================
# FUNÇÃO PRINCIPAL DE BOOTSTRAP
# ================================
def bootstrap_project(
    project_path: str,
    db_path: str = CHROMA_PERSIST_DIR,
    include_code: bool = True,
    include_docs: bool = True,
    include_config: bool = False
) -> Dict[str, int]:
    """
    Executa a ingestão inicial completa do projeto.
    
    Args:
        project_path: Caminho raiz do projeto a ser analisado
        db_path: Caminho do banco de dados ChromaDB
        include_code: Processar arquivos de código
        include_docs: Processar arquivos de documentação
        include_config: Processar arquivos de configuração
        
    Returns:
        Dicionário com estatísticas da ingestão
    """
    print("\n" + "="*80)
    print("🧠 CÉREBRO DE QA - BOOTSTRAP (INGESTÃO INICIAL COMPLETA)")
    print("="*80)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Projeto: {project_path}")
    print(f"💾 Banco de dados: {db_path}")
    print("="*80 + "\n")
    
    # Validar projeto
    if not os.path.exists(project_path):
        raise ValueError(f"❌ Projeto não encontrado: {project_path}")
    
    # Estatísticas
    stats = {
        'total_files': 0,
        'processed_files': 0,
        'code_files': 0,
        'doc_files': 0,
        'config_files': 0,
        'total_chunks': 0,
        'code_chunks': 0,
        'doc_chunks': 0,
        'config_chunks': 0,
        'errors': 0
    }
    
    # 1. Descobrir arquivos
    print("1️⃣ DESCOBRINDO ARQUIVOS DO PROJETO...")
    print("-" * 80)
    
    all_extensions = []
    if include_code:
        all_extensions.extend(SUPPORTED_EXTENSIONS['code'])
    if include_docs:
        all_extensions.extend(SUPPORTED_EXTENSIONS['doc'])
    if include_config:
        all_extensions.extend(SUPPORTED_EXTENSIONS['config'])
    
    discovered_files = discover_files(project_path, all_extensions)
    categorized_files = categorize_files(discovered_files)
    
    print(f"\n📊 Arquivos descobertos:")
    print(f"   💻 Código: {len(categorized_files['code'])} arquivos")
    print(f"   📄 Documentação: {len(categorized_files['doc'])} arquivos")
    print(f"   ⚙️  Configuração: {len(categorized_files['config'])} arquivos")
    print(f"   📦 TOTAL: {len(discovered_files)} arquivos\n")
    
    stats['total_files'] = len(discovered_files)
    
    if len(discovered_files) == 0:
        print("⚠️  Nenhum arquivo encontrado para processar!")
        return stats
    
    # 2. Inicializar componentes LangChain
    print("2️⃣ INICIALIZANDO COMPONENTES LANGCHAIN...")
    print("-" * 80)
    
    llm = ChatOpenAI(model=TRANSLATION_MODEL, temperature=0.1)
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    print(f"   ✅ LLM: {TRANSLATION_MODEL}")
    print(f"   ✅ Embeddings: {EMBEDDING_MODEL}")
    print(f"   ✅ Chunk size: {CHUNK_SIZE} (overlap: {CHUNK_OVERLAP})\n")
    
    # 3. Processar arquivos
    print("3️⃣ PROCESSANDO ARQUIVOS...")
    print("-" * 80 + "\n")
    
    all_chunks = []
    all_metadatas = []
    
    # Processar cada categoria
    for category, files in categorized_files.items():
        if not files:
            continue
            
        # Pular se categoria não incluída
        if category == 'code' and not include_code:
            continue
        if category == 'doc' and not include_docs:
            continue
        if category == 'config' and not include_config:
            continue
        
        print(f"📂 Processando {category.upper()} ({len(files)} arquivos):")
        
        for file_path in files:
            try:
                chunks, metadatas = process_file(file_path, category, llm, splitter)
                
                if chunks:
                    all_chunks.extend(chunks)
                    all_metadatas.extend(metadatas)
                    
                    stats['processed_files'] += 1
                    stats[f'{category}_files'] += 1
                    stats[f'{category}_chunks'] += len(chunks)
                    
            except Exception as e:
                print(f"    ❌ Erro: {e}")
                stats['errors'] += 1
        
        print()  # Linha em branco entre categorias
    
    stats['total_chunks'] = len(all_chunks)
    
    # 4. Criar banco vetorial
    print("4️⃣ CRIANDO BANCO DE DADOS VETORIAL...")
    print("-" * 80 + "\n")
    
    if all_chunks:
        try:
            # Remove banco antigo se existir
            if os.path.exists(db_path):
                print(f"   🗑️  Removendo banco existente: {db_path}")
                import shutil
                shutil.rmtree(db_path)
            
            print(f"   💾 Criando ChromaDB com {len(all_chunks)} chunks...")
            
            vector_store = Chroma.from_texts(
                texts=all_chunks,
                embedding=embeddings,
                metadatas=all_metadatas,
                persist_directory=db_path
            )
            
            print(f"   ✅ Banco criado com sucesso!")
            print(f"   📍 Localização: {db_path}\n")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar banco: {e}\n")
            stats['errors'] += 1
    else:
        print("   ⚠️  Nenhum chunk gerado. Banco não criado.\n")
    
    # 5. Relatório final
    print("="*80)
    print("📊 RELATÓRIO DE BOOTSTRAP")
    print("="*80)
    print(f"✅ Arquivos descobertos: {stats['total_files']}")
    print(f"✅ Arquivos processados: {stats['processed_files']}")
    print(f"   └─ 💻 Código: {stats['code_files']} ({stats['code_chunks']} chunks)")
    print(f"   └─ 📄 Docs: {stats['doc_files']} ({stats['doc_chunks']} chunks)")
    print(f"   └─ ⚙️  Config: {stats['config_files']} ({stats['config_chunks']} chunks)")
    print(f"\n📦 Total de chunks: {stats['total_chunks']}")
    
    if stats['errors'] > 0:
        print(f"❌ Erros: {stats['errors']}")
    
    print(f"\n⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Resumo de próximos passos
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. ✅ Banco de conhecimento inicial criado!")
    print("2. 🔍 Valide com: python validate_ingestion.py")
    print("3. 🎨 Teste no Streamlit: streamlit run app.py")
    print("4. 🔄 A partir de agora, use ingestão DELTA (automática via CI/CD)")
    print("5. 📚 O sistema aprenderá incrementalmente a cada commit\n")
    
    return stats


# ================================
# MAIN
# ================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Bootstrap - Ingestão inicial completa do projeto',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Bootstrap do projeto atual
  python bootstrap_project.py --project-path .

  # Bootstrap de outro projeto
  python bootstrap_project.py --project-path /caminho/do/projeto

  # Apenas código (sem docs)
  python bootstrap_project.py --project-path . --no-docs

  # Incluir arquivos de configuração
  python bootstrap_project.py --project-path . --include-config
        """
    )
    
    parser.add_argument(
        '--project-path',
        type=str,
        required=True,
        help='Caminho raiz do projeto a ser analisado'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default=CHROMA_PERSIST_DIR,
        help=f'Caminho do banco ChromaDB (padrão: {CHROMA_PERSIST_DIR})'
    )
    
    parser.add_argument(
        '--no-code',
        action='store_true',
        help='Não processar arquivos de código'
    )
    
    parser.add_argument(
        '--no-docs',
        action='store_true',
        help='Não processar arquivos de documentação'
    )
    
    parser.add_argument(
        '--include-config',
        action='store_true',
        help='Incluir arquivos de configuração (JSON, YAML, etc.)'
    )
    
    args = parser.parse_args()
    
    try:
        stats = bootstrap_project(
            project_path=args.project_path,
            db_path=args.db_path,
            include_code=not args.no_code,
            include_docs=not args.no_docs,
            include_config=args.include_config
        )
        
        # Exit code baseado em sucesso
        if stats['errors'] == 0 and stats['total_chunks'] > 0:
            print("✅ Bootstrap concluído com sucesso!")
            sys.exit(0)
        else:
            print("⚠️  Bootstrap concluído com problemas.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
