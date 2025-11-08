# 🧠 Cérebro de QA - MVP (Minimum Viable Product)

Sistema RAG (Retrieval-Augmented Generation) para descobrir regras de negócio não documentadas ("Regras Fantasmas") e gerar Planos de Teste BDD automaticamente.

## 🎯 Objetivo

O **Cérebro de QA** automatiza a geração de planos de teste BDD (Behavior-Driven Development) através da análise inteligente de:
- **Código-fonte** (traduzido em regras de negócio via LLM)
- **Documentação** (regras documentadas)

### Capacidades do Sistema:
1. ✅ **Descobrir Regras:** Analisar código Python e extrair regras de negócio implícitas
2. ✅ **Indexar Conhecimento:** Armazenar regras em Banco de Dados Vetorial pesquisável
3. ✅ **Gerar Testes Aumentados:** Criar Planos de Teste BDD baseados no contexto recuperado
4. ✅ **Interface Interativa:** Streamlit para Analistas de QA
5. ✅ **Rastreabilidade:** Identificar origem de cada regra (código ou documentação)

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Código Python  │────▶│  Tradução via    │────▶│   ChromaDB      │
│  + Documentação │     │  GPT-4o-mini     │     │  (Vector Store) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Plano de Testes│◀────│  Geração via     │◀────│   Retrieval     │
│      BDD        │     │  GPT-4o-mini     │     │   (Top-5 docs)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Módulos Principais

| Módulo | Componentes | Função |
| :--- | :--- | :--- |
| **Ingestão** (`src/core/ingestion.py`) | `TextLoader`, `CharacterTextSplitter`, `ChatOpenAI`, `OpenAIEmbeddings`, `Chroma` | Lê código e documentação, traduz em regras via LLM, cria embeddings e armazena no ChromaDB |
| **RAG Pipeline** (`src/core/rag_pipeline.py`) | `Chroma` (Retriever), `ChatOpenAI`, `PromptTemplate`, LCEL | Busca regras relevantes, injeta no prompt e gera Plano de Testes BDD |
| **Interface** (`app.py`) | Streamlit | Interface web para Analistas de QA |
| **CLI** (`src/main.py`) | argparse | Script de linha de comando com múltiplos cenários |
| **Validação** (`validate_ingestion.py`) | pandas, ChromaDB | Valida chunks, embeddings e busca semântica |
| **Visualizador** (`view_database.py`) | pandas, ChromaDB | Explorador interativo do banco de dados |

## 🔧 Pilha de Tecnologia

| Tecnologia | Uso no MVP | Versão |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.10+ | 3.10.0 |
| **Orquestração** | LangChain (LCEL) | latest |
| **Interface** | Streamlit | latest |
| **LLM** | OpenAI GPT-4o-mini | via `langchain-openai` |
| **Embeddings** | text-embedding-ada-002 | 1536 dimensões |
| **Vector Store** | ChromaDB (local) | via `langchain-chroma` |
| **CI/CD** | GitHub Actions | Aprendizado contínuo |
| **Gerenciamento** | `requirements.txt` | - |
| **Embeddings** | text-embedding-ada-002 | 1536 dimensões |
| **Vector Store** | ChromaDB (local) | via `langchain-chroma` |
| **Análise de Dados** | pandas | latest |
| **Env Management** | python-dotenv | latest |

## 📦 Estrutura do Projeto

```
cerebro_qa_mvp/
├── app.py                      # Interface Streamlit (principal)
├── validate_ingestion.py       # Script de validação completa
├── view_database.py            # Visualizador interativo do ChromaDB
├── requirements.txt            # Dependências Python
├── .env                        # Chave de API OpenAI (NÃO COMMITAR!)
├── .gitignore                  # Proteção de arquivos sensíveis
├── README.md                   # Esta documentação
├── README_NOVO.md              # Backup da documentação
├── data/
│   ├── code_example.py         # Código Python simulado (22 regras)
│   └── doc_example.md          # Documentação simulada (30+ regras)
├── src/
│   ├── main.py                 # Script CLI com múltiplos cenários
│   └── core/
│       ├── ingestion.py        # Módulo de ingestão e tradução
│       ├── rag_pipeline.py     # Pipeline RAG de geração
│       └── __pycache__/        # Cache Python
├── chroma_db/                  # Banco de dados vetorial (gerado)
│   └── chroma.sqlite3          # SQLite do ChromaDB
└── docs/                       # Documentação adicional
    ├── Briefing.md
    └── Cérebro de QA - MVP.md
```

## 🚀 Instalação e Configuração

### Pré-requisitos

1. **Python 3.10+**
2. **Chave de API OpenAI** válida
3. **Git** (para clonar o repositório)

### Instalação Passo a Passo

#### 1. Clone o repositório

```bash
git clone https://github.com/edu-data-dev/AI-Agent-Qualidade.git
cd AI-Agent-Qualidade
```

#### 2. Criar ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

**Dependências instaladas:**
- `langchain` - Framework RAG
- `langchain-community` - Loaders e integrações
- `langchain-openai` - Integração OpenAI
- `langchain-text-splitters` - Divisão de textos
- `langchain-chroma` - Vector store
- `chromadb` - Banco de dados vetorial
- `pydantic` - Validação de dados
- `python-dotenv` - Variáveis de ambiente
- `streamlit` - Interface web
- `pandas` - Análise de dados

#### 4. Configurar chave de API

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sk-proj-sua_chave_aqui
```

⚠️ **IMPORTANTE:** Nunca commite o arquivo `.env` no Git!

## 📊 Dados de Teste Inclusos

### 📄 `code_example.py` (Código Python)
Contém **22 regras de negócio** implementadas em 6 funções:

1. `calculate_shipping()` - 4 regras de frete (regional, Prime, frete grátis)
2. `validate_coupon()` - 5 regras de cupons (BLACKFRIDAY, NEWUSER, VIP10)
3. `calculate_installments()` - 7 regras de parcelamento (juros, parcela mínima)
4. `validate_customer_registration()` - 5 regras de cadastro (CPF, idade, email, telefone)
5. `apply_loyalty_points()` - 3 regras de fidelidade (tiers, bônus, multiplicadores)

### 📝 `doc_example.md` (Documentação)
Contém **30+ regras documentadas** em 6 seções:

1. Processamento de Pedidos (validação, cupons)
2. Frete e Logística (cálculo, prazos)
3. Parcelamento (condições, taxas)
4. Programa de Fidelidade (tiers, pontos)
5. Cancelamento e Devolução (prazos, estornos)
6. Segurança e Fraudes (validações, proteção)

## 🎮 Como Usar

### Opção 1: Interface Streamlit (Recomendado)

```bash
streamlit run app.py
```

Acesse: **http://localhost:8501**

**Fluxo de uso:**
1. ✅ Clique em **"1. Iniciar Ingestão"** na sidebar
2. ⏳ Aguarde o processamento (tradução do código → embeddings → ChromaDB)
3. ✏️ Digite sua query ou use a padrão
4. 🚀 Clique em **"Gerar Plano de Testes"**
5. 📋 Visualize o resultado BDD + fontes separadas por tipo (código/doc)

**Recursos da Interface:**
- Status do banco de dados em tempo real
- Geração de planos BDD em formato Gherkin
- **Rastreabilidade de fontes** (regras de código vs documentação)
- Expanders para organizar informações

### Opção 2: Script CLI

**Execução padrão (ingestão + geração):**
```bash
python src/main.py
```

**Pular ingestão (usar DB existente):**
```bash
python src/main.py --skip-ingestion
```

**Query personalizada:**
```bash
python src/main.py --query "Gere testes para validação de CPF e email no cadastro"
```

**Múltiplos cenários de teste:**
```bash
python src/main.py --multi-scenario
```

**Modo Delta (apenas arquivos alterados):**
```bash
# Via git diff (detecta automaticamente)
python src/main.py --delta

# Arquivos específicos
python src/main.py --delta --files data/code_example.py data/doc_example.md
```

### Opção 3: Validação dos Chunks

Para verificar se a ingestão está funcionando corretamente:

```bash
python validate_ingestion.py
```

**Este script exibe:**
- ✅ Total de documentos/chunks armazenados
- ✅ Distribuição entre regras de CÓDIGO vs DOCUMENTAÇÃO
- ✅ Tamanho dos chunks (min/max/médio)
- ✅ Exemplos de regras armazenadas
- ✅ Teste de busca semântica com 5 queries
- ✅ Validação de embeddings (dimensões, valores)
- ✅ Teste de retrieval RAG com cenários específicos

### Opção 4: Visualizador Interativo do Banco

Explore o ChromaDB de forma interativa:

```bash
python view_database.py
```

**Menu do visualizador:**
1. Ver RESUMO de todos os documentos
2. Ver apenas regras de CÓDIGO
3. Ver apenas regras de DOCUMENTAÇÃO
4. Ver documento COMPLETO por ID
5. Buscar por palavra-chave
6. Estatísticas do banco
7. Exportar para CSV

## � CI/CD - Aprendizado Contínuo

O sistema possui **integração completa com GitHub Actions** para aprendizado automático a cada commit!

### ⚡ Como Funciona

```
Desenvolvedor modifica código/docs
           ↓
    git push origin main
           ↓
GitHub Actions detecta alterações (git diff)
           ↓
Processa APENAS arquivos modificados (Delta)
           ↓
Atualiza ChromaDB automaticamente
           ↓
✅ Cérebro de QA mais inteligente!
```

### 🔧 Configuração Rápida

1. **Adicione o secret no GitHub:**
   - Vá em **Settings** → **Secrets and variables** → **Actions**
   - Adicione: `OPENAI_API_KEY` com sua chave OpenAI

2. **Pronto!** O pipeline já está configurado em `.github/workflows/rag-ingestion.yml`

3. **Teste localmente antes de fazer push:**
   ```bash
   # Simulação completa do pipeline CI/CD
   python test_cicd_local.py

   # Teste rápido sem git diff
   python test_cicd_local.py --quick
   ```

### 📚 Pipeline Completo

O workflow executa automaticamente:

1. ✅ **Detecção de Mudanças** - `git diff HEAD^ HEAD` para arquivos `.py` e `.md`
2. ✅ **Configuração** - Python 3.10, instalação de dependências
3. ✅ **Ingestão Delta** - Processa apenas arquivos alterados
4. ✅ **Validação** - Executa `validate_ingestion.py`
5. ✅ **Artefatos** - Salva ChromaDB atualizado (30 dias)
6. ✅ **Relatório** - Gera markdown com estatísticas (90 dias)
7. ✅ **Comentário PR** - Informa arquivos processados (em Pull Requests)

### 📖 Documentação Completa

Para guia detalhado de configuração, troubleshooting e customização:

👉 **[Guia Completo de CI/CD](docs/GITHUB_ACTIONS_SETUP.md)**

## �🔍 Exemplos de Queries

```
"Gere cenários de teste BDD para o cálculo de frete considerando diferentes regiões"

"Gere testes para validação de cupons BLACKFRIDAY, NEWUSER e VIP10"

"Gere cenários de teste para o parcelamento, incluindo juros e parcela mínima"

"Gere testes para validação de cadastro de clientes (CPF, idade, email, telefone)"

"Gere cenários de teste para o programa de fidelidade com diferentes tiers"

"Gere testes para validação de devolução e estorno de pedidos"
```

## 🧪 Validação da Ingestão

### Estatísticas Esperadas

Após executar a ingestão, você deve ver:

- **Total de chunks:** ~42 documentos
- **Regras de CÓDIGO:** ~33 (extraídas do Python)
- **Regras de DOCUMENTAÇÃO:** ~9 (da .md)
- **Dimensão dos embeddings:** 1536 (text-embedding-ada-002)
- **Tamanho dos chunks:**
  - Mínimo: ~77 caracteres
  - Máximo: ~1023 caracteres
  - Médio: ~291 caracteres

### Testes de Busca Semântica

O script `validate_ingestion.py` testa 5 queries automáticas:

1. "Como funciona o frete?"
2. "Quais são as regras de cupom?"
3. "Como é o parcelamento?"
4. "Validação de CPF"
5. "Programa de fidelidade"

Cada query retorna **3 documentos relevantes**.

### Testes de Retrieval RAG

5 cenários completos de RAG:

1. Frete Regional
2. Parcelamento
3. Validação de Cliente
4. Cupons Promocionais
5. Programa de Fidelidade

Cada cenário recupera os **5 documentos mais relevantes**.

## 🔧 Configurações Técnicas

### Modelos Utilizados

- **LLM (Tradução + Geração):** `gpt-4o-mini`
- **Embeddings:** `text-embedding-ada-002`
- **Temperature:** 0.1 (tradução), 0.2 (geração)

### Parâmetros de Chunking

- **Separador:** `\n\n` (quebra de parágrafo)
- **Chunk size:** 1000 caracteres
- **Chunk overlap:** 200 caracteres

### Parâmetros de Retrieval

- **Top-K:** 5 documentos mais relevantes
- **Método:** Similarity search (cosine similarity)

## 📈 Métricas de Sucesso

### ✅ Ingestão
- [x] Código traduzido em regras de negócio
- [x] Chunks salvos no ChromaDB
- [x] Embeddings gerados corretamente
- [x] Busca semântica retornando resultados relevantes

### ✅ Geração
- [x] Plano de Testes BDD gerado
- [x] Formato Gherkin (Given/When/Then)
- [x] Regras de contexto identificadas
- [x] Cobertura de happy path + edge cases
- [x] Rastreabilidade de fontes (código vs doc)

## 🐛 Troubleshooting

### Erro: "No module named 'langchain'"
```bash
pip install -r requirements.txt
```

### Erro: "OpenAI API Key not found"
Verifique se o arquivo `.env` existe e contém:
```env
OPENAI_API_KEY=sk-proj-...
```

### Erro: "ChromaDB not found"
Execute a ingestão primeiro:
```bash
python src/main.py
```
ou clique em "Iniciar Ingestão" no Streamlit.

### Streamlit não inicia
**Windows PowerShell:**
```powershell
.venv\Scripts\streamlit.exe run app.py
```

**Linux/Mac:**
```bash
streamlit run app.py
```

### Erro: "Arquivo já está sendo usado" (WinError 32)
O ChromaDB está bloqueado. Feche o Streamlit antes de limpar o DB:
```bash
taskkill /F /IM streamlit.exe  # Windows
pkill -f streamlit             # Linux/Mac
```

## 🔒 Segurança

- ✅ `.env` adicionado ao `.gitignore`
- ✅ Chave de API não exposta no código
- ✅ `chroma_db/` não commitado (banco local)
- ✅ `__pycache__/` ignorado
- ⚠️ **SEMPRE** revogue chaves expostas acidentalmente no painel da OpenAI

## 6. CI/CD e Aprendizado Contínuo

### ✅ Pipeline GitHub Actions Implementado

O sistema possui **integração completa com GitHub Actions** que executa automaticamente a cada commit!

**Arquivo:** `.github/workflows/rag-ingestion.yml`

**Funcionalidades:**
- ✅ Detecção automática de arquivos alterados via `git diff`
- ✅ Processamento delta (apenas arquivos modificados)
- ✅ Atualização automática do ChromaDB
- ✅ Validação da integridade do banco
- ✅ Geração de artefatos (ChromaDB + relatórios)
- ✅ Comentários automáticos em Pull Requests

**Para ativar:**
1. Configure o secret `OPENAI_API_KEY` no GitHub (Settings → Secrets)
2. Faça push de qualquer alteração em arquivos `.py` ou `.md`
3. Acompanhe a execução em **Actions**

**Teste localmente antes de fazer push:**
```bash
# Simulação completa do pipeline CI/CD
python test_cicd_local.py

# Teste rápido sem git diff
python test_cicd_local.py --quick
```

👉 **[Guia Completo de Configuração CI/CD](docs/GITHUB_ACTIONS_SETUP.md)**

### Função de Ingestão Delta (Implementada)

**Arquivo:** `src/core/delta_ingestion.py`

```python
# Processar apenas arquivos alterados
from src.core.delta_ingestion import process_changed_files

stats = process_changed_files(
    changed_files=['data/code_example.py', 'data/doc_example.md']
)
```

**Uso via CLI:**
```bash
# Detecta alterações via git diff
python src/main.py --delta

# Arquivos específicos
python src/main.py --delta --files data/code_example.py
```

## 📚 Próximos Passos (Roadmap)

### Fase 1: Melhorias Imediatas
- [ ] Suporte a múltiplas linguagens de programação (Java, JavaScript, C#)
- [ ] Interface para upload de arquivos via Streamlit
- [ ] Histórico de queries e resultados salvos
- [ ] Exportação de planos de teste para arquivos `.feature` (Gherkin)
- [ ] Métricas de cobertura de regras

### Fase 2: Escalabilidade
- [ ] Migrar ChromaDB local para **Pinecone** ou **PGVector**
- [x] Implementar ingestão delta (processar apenas alterações) ✅
- [x] Integração CI/CD real (GitHub Actions) ✅
- [ ] Cache de embeddings para reduzir custos de API
- [ ] Suporte a múltiplos projetos/workspaces

### Fase 3: Fontes de Dados Adicionais
- [ ] Loader para **Confluence** (Wiki)
- [ ] Loader para **Jira** (Épicos/User Stories)
- [ ] Loader para **Schemas de Banco de Dados** (SQL)
- [ ] Loader para **APIs** (OpenAPI/Swagger)
- [ ] Loader para **Postman Collections**

### Fase 4: Inteligência Avançada
- [ ] Avaliar modelos alternativos (Gemini 1.5 Pro, GPT-4o)
- [ ] Detecção automática de regras conflitantes
- [ ] Sugestão de casos de teste faltantes
- [ ] Geração de dados de teste sintéticos
- [ ] Análise de impacto de mudanças de código

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este é um projeto MVP para demonstração de conceito.

## 👥 Autores

- **Eduardo Alves de Paulo Filho** - [edu-data-dev](https://github.com/edu-data-dev)

## 🙏 Agradecimentos

- OpenAI pela API GPT e Embeddings
- LangChain pela framework RAG
- Streamlit pela interface web
- ChromaDB pelo banco vetorial

---

**Desenvolvido com ❤️ usando LangChain, OpenAI e Streamlit**

**Repositório:** [AI-Agent-Qualidade](https://github.com/edu-data-dev/AI-Agent-Qualidade)
