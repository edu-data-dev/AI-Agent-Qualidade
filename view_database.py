"""
Visualizador interativo do banco de dados ChromaDB.
Permite explorar todos os documentos, embeddings e metadados salvos.
"""

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import pandas as pd

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(PROJECT_ROOT, "chroma_db")

def view_all_documents():
    """
    Visualiza todos os documentos salvos no ChromaDB de forma estruturada.
    """
    print("=" * 100)
    print("VISUALIZADOR DO BANCO DE DADOS VETORIAL (ChromaDB)")
    print("=" * 100)
    
    if not os.path.exists(DB_DIR):
        print(f"\n❌ ERRO: Banco de dados não encontrado em: {DB_DIR}")
        print("Execute a ingestão primeiro!")
        return
    
    try:
        # Carrega o vector store
        print(f"\n📂 Carregando banco de dados de: {DB_DIR}\n")
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vector_store = Chroma(
            persist_directory=DB_DIR,
            embedding_function=embeddings
        )
        
        # Obtém a coleção
        collection = vector_store._collection
        
        # Busca todos os documentos
        all_docs = collection.get(
            include=['documents', 'metadatas', 'embeddings']
        )
        
        total = len(all_docs['documents'])
        print(f"📊 TOTAL DE DOCUMENTOS NO BANCO: {total}\n")
        
        if total == 0:
            print("⚠️ Nenhum documento encontrado!")
            return
        
        # Criar DataFrame para visualização
        data = []
        for i, (doc, metadata) in enumerate(zip(all_docs['documents'], all_docs['metadatas'] or [{}]*total)):
            # Identifica o tipo
            if '[TIPO: CÓDIGO]' in doc:
                tipo = "CÓDIGO"
                content = doc.replace('- [TIPO: CÓDIGO] Regra de Negócio: ', '')
            elif '[TIPO: DOC]' in doc:
                tipo = "DOCUMENTAÇÃO"
                content = doc.replace('- [TIPO: DOC] Regra Documentada: ', '')
            else:
                tipo = "OUTRO"
                content = doc
            
            data.append({
                'ID': i + 1,
                'Tipo': tipo,
                'Conteúdo': content[:100] + '...' if len(content) > 100 else content,
                'Tamanho': len(doc),
                'Conteúdo_Completo': content
            })
        
        df = pd.DataFrame(data)
        
        # Menu interativo
        while True:
            print("\n" + "=" * 100)
            print("MENU DE VISUALIZAÇÃO")
            print("=" * 100)
            print("\n1. Ver RESUMO de todos os documentos")
            print("2. Ver apenas regras de CÓDIGO")
            print("3. Ver apenas regras de DOCUMENTAÇÃO")
            print("4. Ver documento COMPLETO por ID")
            print("5. Buscar por palavra-chave")
            print("6. Estatísticas do banco")
            print("7. Exportar para CSV")
            print("0. Sair")
            
            choice = input("\n👉 Escolha uma opção: ").strip()
            
            if choice == '1':
                print("\n" + "=" * 100)
                print("RESUMO DE TODOS OS DOCUMENTOS")
                print("=" * 100 + "\n")
                print(df[['ID', 'Tipo', 'Conteúdo', 'Tamanho']].to_string(index=False))
                
            elif choice == '2':
                code_df = df[df['Tipo'] == 'CÓDIGO']
                print("\n" + "=" * 100)
                print(f"REGRAS EXTRAÍDAS DO CÓDIGO ({len(code_df)} regras)")
                print("=" * 100 + "\n")
                for _, row in code_df.iterrows():
                    print(f"ID {row['ID']}: {row['Conteúdo_Completo']}\n")
                
            elif choice == '3':
                doc_df = df[df['Tipo'] == 'DOCUMENTAÇÃO']
                print("\n" + "=" * 100)
                print(f"REGRAS DA DOCUMENTAÇÃO ({len(doc_df)} regras)")
                print("=" * 100 + "\n")
                for _, row in doc_df.iterrows():
                    print(f"ID {row['ID']}: {row['Conteúdo_Completo']}\n")
                
            elif choice == '4':
                doc_id = input("Digite o ID do documento (1-{}): ".format(total)).strip()
                try:
                    doc_id = int(doc_id)
                    if 1 <= doc_id <= total:
                        row = df[df['ID'] == doc_id].iloc[0]
                        print("\n" + "=" * 100)
                        print(f"DOCUMENTO ID: {doc_id}")
                        print("=" * 100)
                        print(f"\n📌 Tipo: {row['Tipo']}")
                        print(f"📏 Tamanho: {row['Tamanho']} caracteres")
                        print(f"\n📄 Conteúdo Completo:")
                        print("-" * 100)
                        print(row['Conteúdo_Completo'])
                        print("-" * 100)
                        
                        # Mostra embedding (primeiros 20 valores)
                        if all_docs['embeddings'] and len(all_docs['embeddings']) >= doc_id:
                            embedding = all_docs['embeddings'][doc_id - 1]
                            print(f"\n🔬 Embedding (primeiros 20 valores):")
                            print(embedding[:20])
                    else:
                        print(f"❌ ID inválido! Use um valor entre 1 e {total}")
                except ValueError:
                    print("❌ Por favor, digite um número válido!")
                
            elif choice == '5':
                keyword = input("Digite a palavra-chave para buscar: ").strip().lower()
                matches = df[df['Conteúdo_Completo'].str.lower().str.contains(keyword, na=False)]
                print("\n" + "=" * 100)
                print(f"RESULTADOS DA BUSCA: '{keyword}' ({len(matches)} encontrados)")
                print("=" * 100 + "\n")
                if len(matches) > 0:
                    for _, row in matches.iterrows():
                        print(f"ID {row['ID']} [{row['Tipo']}]: {row['Conteúdo_Completo']}\n")
                else:
                    print("Nenhum resultado encontrado.")
                
            elif choice == '6':
                print("\n" + "=" * 100)
                print("ESTATÍSTICAS DO BANCO DE DADOS")
                print("=" * 100)
                print(f"\n📊 Total de documentos: {total}")
                print(f"🔹 Regras de CÓDIGO: {len(df[df['Tipo'] == 'CÓDIGO'])}")
                print(f"📄 Regras de DOCUMENTAÇÃO: {len(df[df['Tipo'] == 'DOCUMENTAÇÃO'])}")
                print(f"\n📏 Tamanho dos documentos:")
                print(f"   - Mínimo: {df['Tamanho'].min()} caracteres")
                print(f"   - Máximo: {df['Tamanho'].max()} caracteres")
                print(f"   - Médio: {df['Tamanho'].mean():.0f} caracteres")
                
                if all_docs['embeddings']:
                    print(f"\n🔬 Embeddings:")
                    print(f"   - Dimensão: {len(all_docs['embeddings'][0])} dimensões")
                    print(f"   - Total de vetores: {len(all_docs['embeddings'])}")
                
            elif choice == '7':
                output_file = "database_export.csv"
                df[['ID', 'Tipo', 'Conteúdo_Completo', 'Tamanho']].to_csv(output_file, index=False, encoding='utf-8-sig')
                print(f"\n✅ Dados exportados para: {output_file}")
                
            elif choice == '0':
                print("\n👋 Até logo!")
                break
                
            else:
                print("\n❌ Opção inválida! Tente novamente.")
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    view_all_documents()
