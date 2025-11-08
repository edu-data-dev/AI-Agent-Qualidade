# Cérebro de QA - MVP (Minimum Viable Product)

## 1. Visão Geral do Projeto

O **Cérebro de QA** é um sistema de Geração Aumentada por Recuperação (RAG) projetado para resolver a dor crítica de **regras de negócio não documentadas** ("Regras Fantasmas") em projetos de software.

Este MVP demonstra a capacidade do sistema de:
1.  **Descobrir Regras:** Analisar código-fonte e documentação para extrair regras de negócio explícitas e implícitas.
2.  **Indexar Conhecimento:** Armazenar essas regras em um Banco de Dados Vetorial pesquisável.
3.  **Gerar Testes Aumentados:** Utilizar o conhecimento indexado para gerar Planos de Teste BDD (Given/When/Then) completos e baseados na "verdade" do código.
4.  **Interface Interativa:** Fornecer uma interface simples para o Analista de QA.

## 2. Arquitetura do MVP (LangChain RAG Pipeline)

O MVP utiliza a arquitetura RAG e é dividido em três módulos principais: **Ingestão**, **Geração** e **Interface**.

| Módulo | Componentes Principais | Função |
| :--- | :--- | :--- |
| **Ingestão** (`ingestion.py`) | `TextLoader`, `CharacterTextSplitter`, `ChatOpenAI` (Tradutor), `OpenAIEmbeddings`, `Chroma` (Vector Store) | **Fase de Descoberta e Indexação.** Lê o código e a documentação, usa um LLM para traduzir trechos de código em regras de negócio em linguagem natural, cria embeddings dessas regras e as armazena no ChromaDB. |
| **Geração** (`rag_pipeline.py`) | `Chroma` (Retriever), `ChatOpenAI` (Gerador), `PromptTemplate`, **LCEL** (LangChain Expression Language) | **Fase de Consulta e Geração.** Recebe uma consulta do QA, busca as regras mais relevantes no ChromaDB (Retrieval), injeta essas regras no prompt (Augmentation) e usa um LLM para gerar o Plano de Testes BDD (Generation). |
| **Interface** (`app.py`) | **Streamlit** | Interface web simples para o Analista de QA interagir com o sistema (iniciar ingestão e gerar testes). |

## 3. Pilha de Tecnologia

| Tecnologia | Uso no MVP |
| :--- | :--- |
| **Linguagem** | Python 3.11+ |
| **Orquestração** | LangChain (usando LCEL) |
| **Interface** | Streamlit |
| **LLM (Tradução/Geração)** | OpenAI (via `langchain-openai`): `gpt-4.1-mini` (Configurável) |
| **Embeddings** | OpenAI (via `langchain-openai`): `text-embedding-ada-002` (Configurável) |
| **Banco de Dados Vetorial** | ChromaDB (persistido localmente) |
| **Gerenciamento de Dependências** | `requirements.txt` |

## 4. Implementação e Configuração

### 4.1. Pré-requisitos

1.  **Python 3.11+**
2.  **Chave de API OpenAI:** O projeto requer uma chave de API válida para acessar os modelos de LLM e Embeddings.

### 4.2. Estrutura de Diretórios

```
/cerebro_qa_mvp
├── src/
│   ├── core/
│   │   ├── ingestion.py       # Lógica de Ingestão e Indexação
│   │   └── rag_pipeline.py    # Lógica do Pipeline RAG e Geração de Testes
│   └── main.py              # Script de linha de comando (obsoleto, mantido para referência)
├── data/
│   ├── code_example.py      # Código-fonte simulado (Fonte da Verdade)
│   └── doc_example.md       # Documentação simulada
├── chroma_db/               # Diretório persistido do Banco de Dados Vetorial (criado após a 1ª execução)
├── app.py                   # Interface Streamlit
├── requirements.txt         # Dependências Python
└── README.md                # Esta documentação
```

### 4.3. Instalação

1.  **Clone o repositório (ou crie a estrutura acima).**
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure a Chave de API:** Crie um arquivo `.env` na raiz do projeto (`/cerebro_qa_mvp`) e adicione sua chave:
    ```
    OPENAI_API_KEY="sua_chave_aqui"
    ```

## 5. Execução do MVP

### 5.1. Execução da Interface Streamlit

Para iniciar a interface web e interagir com o Cérebro de QA:

```bash
streamlit run cerebro_qa_mvp/app.py
```

Após a execução, acesse o endereço fornecido no terminal (geralmente `http://localhost:8501`).

**Fluxo de Uso na Interface:**
1.  Clique em **"1. Iniciar Ingestão (Criar/Atualizar DB)"** na barra lateral. Isso irá processar o código e a documentação, criando o "Cérebro".
2.  Após a confirmação de que o DB está pronto, insira sua consulta na área de texto e clique em **"Gerar Plano de Testes"**.

## 6. Simulação de CI/CD (Detecção de Alteração)

Para simular o **Pipeline de Aprendizado Contínuo** (CI/CD) e a detecção de alterações (Git Diff), o módulo `ingestion.py` precisaria ser modificado para receber uma lista de arquivos alterados.

### 6.1. Estrutura de Detecção de Alteração

Em um ambiente real de CI/CD (como GitHub Actions ou Azure DevOps Pipeline), o passo seria:

1.  **Gatilho:** `on: push` na branch `main`.
2.  **Ação:** Executar `git diff --name-only <SHA_anterior> <SHA_atual>` para obter a lista de arquivos alterados.
3.  **Processamento:** Chamar uma função de ingestão que itera apenas sobre essa lista de arquivos.

### 6.2. Função de Ingestão Delta (Conceito)

A função `create_vector_store` em `ingestion.py` já é modular e pode ser adaptada. O conceito seria:

```python
# Conceito de Ingestão Delta
def create_vector_store_delta(changed_files: list[str], db_path: str):
    # 1. Carregar o DB existente (para evitar reprocessar tudo)
    vector_store = Chroma(persist_directory=db_path, ...)
    
    new_rules = []
    for file_path in changed_files:
        if file_path.endswith(".py"):
            # Processa apenas o código alterado
            new_rules.extend(process_documents(file_path, "code"))
        elif file_path.endswith(".md"):
            # Processa apenas a documentação alterada
            new_rules.extend(process_documents(file_path, "doc"))
            
    # 2. Adicionar os novos embeddings ao DB existente
    if new_rules:
        vector_store.add_texts(texts=new_rules, ...)
        vector_store.persist()
```

**No MVP atual, a simulação é feita:**
Ao clicar em **"Iniciar Ingestão"** no Streamlit, o sistema **reprocessa todos os arquivos** (`code_example.py` e `doc_example.md`). Para simular uma alteração, basta modificar o conteúdo de `data/code_example.py` e clicar em "Iniciar Ingestão" novamente. O sistema irá reindexar o novo conhecimento, simulando o aprendizado contínuo.

## 7. Próximos Passos (Evolução para Produção)

Para evoluir este MVP para um sistema de produção, as seguintes etapas são recomendadas:

| Fase | Descrição |
| :--- | :--- |
| **Integração CI/CD** | Implementar o passo de `git diff` em um pipeline real (Azure DevOps) e adaptar a função de ingestão para o modo **Delta** (conforme Seção 6.2). |
| **Banco de Dados Vetorial** | Migrar o ChromaDB local para uma solução escalável como **Pinecone** ou **PGVector** (PostgreSQL com extensão `pgvector`). |
| **Modelos LLM** | Avaliar o uso de modelos como **Gemini 1.5 Pro** ou **GPT-4o** para a tarefa de tradução de código, devido à sua alta janela de contexto e capacidade de raciocínio complexo. |
| **Fontes de Dados** | Adicionar *Loaders* para outras fontes, como Confluence (Wiki), Jira (Épicos/Histórias) e Schemas de Banco de Dados. |

---
*Documentação gerada por Manus AI.*
