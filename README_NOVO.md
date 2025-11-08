# 🧠 Cérebro de QA - MVP (Minimum Viable Product)

Sistema RAG (Retrieval-Augmented Generation) para descobrir regras de negócio não documentadas ("Regras Fantasmas") e gerar Planos de Teste BDD automaticamente.

## 🎯 Objetivo

Automatizar a geração de planos de teste BDD (Behavior-Driven Development) através da análise inteligente de:
- **Código-fonte** (traduzido em regras de negócio via LLM)
- **Documentação** (regras documentadas)

## 🏗️ Arquitetura

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

## 📦 Estrutura do Projeto

```
cerebro_qa_mvp/
├── app.py                      # Interface Streamlit
├── validate_ingestion.py       # Script de validação dos chunks
├── requirements.txt            # Dependências Python
├── .env                        # Chave de API OpenAI (NÃO COMMITAR!)
├── .gitignore                  # Proteção de arquivos sensíveis
├── data/
│   ├── code_example.py         # Código simulado (22 regras)
│   └── doc_example.md          # Documentação (30+ regras)
├── src/
│   ├── main.py                 # Script CLI principal
│   └── core/
│       ├── ingestion.py        # Módulo de ingestão e tradução
│       └── rag_pipeline.py     # Módulo de geração RAG
└── chroma_db/                  # Banco de dados vetorial (gerado)
```

## 🚀 Instalação

### 1. Criar ambiente virtual

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 3. Configurar variável de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_aqui
```

**⚠️ IMPORTANTE:** Nunca commite o arquivo `.env` no Git!

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

```powershell
streamlit run app.py
```

Acesse: http://localhost:8501

**Fluxo de uso:**
1. Clique em "1. Iniciar Ingestão" na sidebar
2. Aguarde o processamento (tradução do código → embeddings → ChromaDB)
3. Digite sua query ou use a padrão
4. Clique em "Gerar Plano de Testes"
5. Visualize o resultado BDD + regras utilizadas

### Opção 2: Script CLI

**Execução padrão (ingestão + geração):**
```powershell
python src/main.py
```

**Pular ingestão (usar DB existente):**
```powershell
python src/main.py --skip-ingestion
```

**Query personalizada:**
```powershell
python src/main.py --query "Gere testes para validação de CPF e email no cadastro"
```

**Múltiplos cenários de teste:**
```powershell
python src/main.py --multi-scenario
```

### Opção 3: Validação dos Chunks

Para verificar se a ingestão está funcionando corretamente:

```powershell
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

## 🔍 Exemplos de Queries

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

- **Total de chunks:** ~30-50 (varia com o chunking)
- **Regras de CÓDIGO:** ~22 (extraídas do Python)
- **Regras de DOCUMENTAÇÃO:** ~30+ (da .md)
- **Dimensão dos embeddings:** 1536 (text-embedding-ada-002)

### Testes de Busca Semântica

O script `validate_ingestion.py` testa 5 queries automáticas:

1. "Como funciona o frete?"
2. "Quais são as regras de cupom?"
3. "Como é o parcelamento?"
4. "Validação de CPF"
5. "Programa de fidelidade"

Cada query deve retornar **3 documentos relevantes**.

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
- [ ] Código traduzido em regras de negócio
- [ ] Chunks salvos no ChromaDB
- [ ] Embeddings gerados corretamente
- [ ] Busca semântica retornando resultados relevantes

### ✅ Geração
- [ ] Plano de Testes BDD gerado
- [ ] Formato Gherkin (Given/When/Then)
- [ ] Regras de contexto identificadas
- [ ] Cobertura de happy path + edge cases

## 🐛 Troubleshooting

### Erro: "No module named 'langchain'"
```powershell
pip install -r requirements.txt
```

### Erro: "OpenAI API Key not found"
Verifique se o arquivo `.env` existe e contém:
```env
OPENAI_API_KEY=sk-proj-...
```

### Erro: "ChromaDB not found"
Execute a ingestão primeiro:
```powershell
python src/main.py
```

### Streamlit não inicia
```powershell
# Windows PowerShell
.venv\Scripts\streamlit.exe run app.py
```

### Erro: "Arquivo já está sendo usado" (WinError 32)
O ChromaDB está bloqueado. Feche o Streamlit antes de limpar o DB:
```powershell
taskkill /F /IM streamlit.exe
```

## 🔒 Segurança

- ✅ `.env` adicionado ao `.gitignore`
- ✅ Chave de API não exposta no código
- ✅ `chroma_db/` não commitado (banco local)
- ⚠️ **SEMPRE** revogue chaves expostas acidentalmente

## 📚 Próximos Passos (Roadmap)

- [ ] Suporte a múltiplas linguagens de programação
- [ ] Interface para upload de arquivos
- [ ] Histórico de queries e resultados
- [ ] Exportação de planos de teste (.feature files)
- [ ] Métricas de cobertura de regras
- [ ] Integração com CI/CD

## 📝 Licença

Este é um projeto MVP para demonstração de conceito.

## 🤝 Contribuição

Contribuições são bem-vindas! Abra issues ou pull requests.

---

**Desenvolvido com ❤️ usando LangChain, OpenAI e Streamlit**
