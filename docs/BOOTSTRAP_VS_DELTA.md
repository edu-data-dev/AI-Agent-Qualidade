# 🎯 Bootstrap vs Delta - Estratégia de Ingestão

## 📚 Visão Geral

O Cérebro de QA possui **duas estratégias de ingestão** complementares:

### 1. **BOOTSTRAP** (Ingestão Inicial Completa)
- 🎯 **Quando:** Primeira vez que você conecta o sistema a um projeto
- 📦 **O que faz:** Processa **TODO** o código-fonte e documentação
- ⏱️ **Tempo:** Pode levar vários minutos (depende do tamanho do projeto)
- 💰 **Custo:** Maior (processa tudo)
- ✅ **Resultado:** Base de conhecimento completa criada do zero

### 2. **DELTA** (Ingestão Incremental)
- 🎯 **Quando:** Após o bootstrap, em cada commit/push
- 📦 **O que faz:** Processa **APENAS** arquivos modificados
- ⏱️ **Tempo:** Rápido (segundos a poucos minutos)
- 💰 **Custo:** Menor (processa só mudanças)
- ✅ **Resultado:** Base de conhecimento atualizada incrementalmente

---

## 🚀 Como Funciona na Prática

### Cenário 1: Primeiro Uso (Bootstrap)

```
Você cria o repositório no GitHub
         ↓
Configura OPENAI_API_KEY no GitHub Secrets
         ↓
Faz o primeiro push
         ↓
GitHub Actions detecta: ChromaDB NÃO existe
         ↓
🎯 EXECUTA BOOTSTRAP
         ↓
Escaneia TODO o projeto:
  - src/models/*.py (100 arquivos)
  - src/services/*.java (50 arquivos)
  - docs/*.md (20 arquivos)
  - config/*.yaml (10 arquivos)
         ↓
Traduz código em regras via GPT-4o-mini
         ↓
Cria embeddings de TUDO
         ↓
Salva no ChromaDB (ex: 5.000 chunks)
         ↓
✅ BASE DE CONHECIMENTO COMPLETA CRIADA!
```

**Tempo estimado:** 10-30 minutos (projeto médio)  
**Custo estimado:** $2-5 em API OpenAI

---

### Cenário 2: Desenvolvimento Contínuo (Delta)

```
Dev modifica UserService.java
         ↓
git commit -m "feat: adiciona validação de email"
git push origin main
         ↓
GitHub Actions detecta: ChromaDB JÁ existe
         ↓
🔄 EXECUTA DELTA
         ↓
git diff detecta: 1 arquivo alterado
  - src/services/UserService.java
         ↓
Processa APENAS UserService.java
         ↓
Traduz novas regras via GPT-4o-mini
         ↓
Cria embeddings das mudanças
         ↓
ADICIONA ao ChromaDB existente (ex: +8 chunks)
         ↓
✅ BASE ATUALIZADA INCREMENTALMENTE!
```

**Tempo estimado:** 30-60 segundos  
**Custo estimado:** $0.05-0.20 em API OpenAI

---

## 📊 Comparação Detalhada

| Aspecto | Bootstrap | Delta |
|:--------|:----------|:------|
| **Gatilho** | Primeira execução (ChromaDB vazio) | Execuções subsequentes |
| **Arquivos processados** | TODOS do projeto | Apenas alterados (git diff) |
| **Tempo** | Minutos a horas | Segundos a minutos |
| **Custo OpenAI** | Alto (processa tudo) | Baixo (só mudanças) |
| **Quando usar** | Setup inicial | Desenvolvimento diário |
| **Comando manual** | `python bootstrap_project.py --project-path .` | `python src/main.py --delta` |
| **GitHub Actions** | Automático (se ChromaDB vazio) | Automático (se ChromaDB existe) |

---

## 🎓 Casos de Uso

### Caso 1: Novo Projeto

**Situação:** Você quer conectar o Cérebro de QA a um projeto existente.

**Passos:**

1. **Clone o Cérebro de QA** no seu repositório ou workspace
2. **Execute o bootstrap localmente** (recomendado antes de push):
   ```bash
   python bootstrap_project.py --project-path /caminho/do/seu/projeto
   ```
3. **Valide** que funcionou:
   ```bash
   python validate_ingestion.py
   ```
4. **Teste** no Streamlit:
   ```bash
   streamlit run app.py
   ```
5. **Configure GitHub Actions** (se quiser automação)
6. **Push** - a partir daí, usa delta automaticamente

---

### Caso 2: Projeto Já em Produção

**Situação:** Projeto já está no GitHub, quer adicionar o Cérebro de QA.

**Passos:**

1. **Adicione os arquivos do Cérebro de QA** ao repositório:
   ```
   .github/workflows/rag-ingestion.yml
   bootstrap_project.py
   src/core/delta_ingestion.py
   (outros arquivos do sistema)
   ```

2. **Configure secret** `OPENAI_API_KEY` no GitHub

3. **Faça push**:
   ```bash
   git add .
   git commit -m "feat: adiciona Cérebro de QA"
   git push origin main
   ```

4. **GitHub Actions detecta:** ChromaDB não existe → **Executa BOOTSTRAP automaticamente**

5. **Aguarde** (10-30 min dependendo do tamanho)

6. **Valide** baixando o artefato `chroma-db-<SHA>`

7. **A partir do próximo commit:** usa DELTA automaticamente ✅

---

### Caso 3: Reset Completo

**Situação:** Quer reprocessar tudo do zero (mudou prompt, modelo, etc.).

**Opção 1: Local**
```bash
# Deleta banco antigo
rm -rf chroma_db/

# Executa bootstrap novamente
python bootstrap_project.py --project-path .
```

**Opção 2: GitHub Actions**
```bash
# Deleta banco do artefato anterior
# (ou simplesmente espera 30 dias para expirar)

# Força bootstrap no próximo push
# (GitHub Actions detectará ChromaDB vazio)
git commit --allow-empty -m "chore: força rebuild do ChromaDB"
git push origin main
```

---

## 🔧 Configuração do Bootstrap

### Arquivo: `bootstrap_project.py`

**Argumentos disponíveis:**

```bash
# Bootstrap padrão (código + docs)
python bootstrap_project.py --project-path .

# Incluir arquivos de configuração
python bootstrap_project.py --project-path . --include-config

# Apenas código (sem docs)
python bootstrap_project.py --project-path . --no-docs

# Apenas documentação (sem código)
python bootstrap_project.py --project-path . --no-code

# Banco customizado
python bootstrap_project.py --project-path . --db-path ./meu_banco
```

---

### Extensões Suportadas

**Código:**
- `.py` (Python)
- `.java` (Java)
- `.js`, `.ts`, `.jsx`, `.tsx` (JavaScript/TypeScript)
- `.cs` (C#)
- `.cpp`, `.c` (C/C++)
- `.go` (Go)
- `.rb` (Ruby)
- `.php` (PHP)

**Documentação:**
- `.md` (Markdown)
- `.txt` (Texto)
- `.rst` (reStructuredText)
- `.adoc` (AsciiDoc)

**Configuração** (opcional):
- `.json` (JSON)
- `.yaml`, `.yml` (YAML)
- `.toml` (TOML)
- `.ini` (INI)
- `.xml` (XML)

---

### Diretórios Ignorados

O bootstrap automaticamente ignora:

- `__pycache__`
- `node_modules`
- `.git`
- `.venv`, `venv`, `env`
- `build`, `dist`, `target`
- `.pytest_cache`, `.mypy_cache`
- `coverage`
- `.idea`, `.vscode`
- `chroma_db` (para não processar o próprio banco!)

---

## ⚡ Performance e Otimização

### Estimativas de Tempo

| Tamanho do Projeto | Arquivos | Bootstrap | Delta (1 arquivo) |
|:-------------------|:---------|:----------|:------------------|
| **Pequeno** | < 100 | 2-5 min | 10-30 seg |
| **Médio** | 100-500 | 5-15 min | 20-60 seg |
| **Grande** | 500-2000 | 15-45 min | 30-90 seg |
| **Muito Grande** | > 2000 | 45+ min | 1-3 min |

### Estimativas de Custo (OpenAI)

**Premissas:**
- GPT-4o-mini: $0.15/1M tokens input, $0.60/1M tokens output
- text-embedding-ada-002: $0.10/1M tokens

| Tamanho do Projeto | Bootstrap | Delta (1 arquivo) |
|:-------------------|:----------|:------------------|
| **Pequeno** | $1-2 | $0.02-0.05 |
| **Médio** | $3-8 | $0.05-0.15 |
| **Grande** | $10-25 | $0.10-0.30 |
| **Muito Grande** | $25+ | $0.20-0.50 |

### Dicas de Otimização

1. **Execute bootstrap localmente primeiro**
   - Evita surpresas de custo/tempo no CI/CD
   - Permite ajustar configurações

2. **Use .gitignore efetivo**
   - Evita processar arquivos desnecessários
   - Reduz tempo e custo

3. **Ajuste chunk size**
   - Chunks maiores = menos tokens de embedding
   - Chunks menores = mais precisão na busca

4. **Cache de resultados** (futuro)
   - Guardar traduções de código já processado
   - Evitar reprocessar arquivos idênticos

---

## 🔄 Fluxo Completo (Primeira Vez)

```
┌─────────────────────────────────────────────────────────┐
│  1. SETUP INICIAL                                       │
│                                                         │
│  - Clone Cérebro de QA                                 │
│  - Configure .env com OPENAI_API_KEY                   │
│  - Instale dependências: pip install -r requirements.txt│
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  2. BOOTSTRAP LOCAL (Recomendado)                      │
│                                                         │
│  $ python bootstrap_project.py --project-path .        │
│                                                         │
│  Output:                                               │
│    🔍 Escaneando diretório...                         │
│    📊 150 arquivos descobertos                        │
│    🔄 Traduzindo UserService.java...                  │
│    ✅ UserService.java: 12 chunks                     │
│    ... (continua para todos os arquivos)              │
│    💾 Criando ChromaDB com 2.500 chunks...           │
│    ✅ Banco criado com sucesso!                       │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  3. VALIDAÇÃO                                          │
│                                                         │
│  $ python validate_ingestion.py                        │
│                                                         │
│  Output:                                               │
│    ✅ 2.500 documentos no banco                       │
│    ✅ 2.100 chunks de CÓDIGO                          │
│    ✅ 400 chunks de DOCUMENTAÇÃO                      │
│    ✅ Embeddings: 1536 dimensões                      │
│    ✅ Busca semântica funcionando                     │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  4. TESTE NO STREAMLIT                                 │
│                                                         │
│  $ streamlit run app.py                                │
│                                                         │
│  Query: "Gere testes para validação de email"         │
│  Result: Plano BDD com cenários baseados no código!   │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  5. CONFIGURAR GITHUB ACTIONS                          │
│                                                         │
│  - Adicione secret OPENAI_API_KEY                      │
│  - Commit & push do Cérebro de QA                      │
│  - Workflow detecta ChromaDB local                     │
│  - Faz upload como artefato                            │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  6. USO CONTÍNUO (Delta Automático)                    │
│                                                         │
│  Dev modifica código → git push                        │
│       ↓                                                 │
│  GitHub Actions detecta mudança                        │
│       ↓                                                 │
│  Processa APENAS arquivo modificado                    │
│       ↓                                                 │
│  Atualiza ChromaDB incrementalmente                    │
│       ↓                                                 │
│  ✅ Sistema aprende automaticamente!                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Resumo Executivo

### ✅ O Que Você Precisa Saber

1. **Bootstrap = Primeira Vez**
   - Processa TODO o projeto
   - Cria banco do zero
   - Leva tempo, mas é só uma vez

2. **Delta = Uso Diário**
   - Processa SÓ mudanças
   - Rápido e barato
   - Mantém sistema atualizado

3. **Automação Inteligente**
   - GitHub Actions decide automaticamente
   - Se ChromaDB vazio → Bootstrap
   - Se ChromaDB existe → Delta

4. **Teste Local Primeiro**
   - Execute bootstrap localmente
   - Valide antes de push
   - Evite surpresas no CI/CD

---

## 📚 Próximos Passos

1. **Agora:** Execute bootstrap local no seu projeto
   ```bash
   python bootstrap_project.py --project-path /seu/projeto
   ```

2. **Valide:** Certifique-se que funcionou
   ```bash
   python validate_ingestion.py
   ```

3. **Configure:** Adicione ao GitHub com CI/CD

4. **Use:** A partir daí, é automático! 🎉

---

**Dúvidas?** Consulte:
- `PROXIMOS_PASSOS.md` - Instruções gerais
- `docs/GITHUB_ACTIONS_SETUP.md` - Configuração CI/CD
- `docs/TUTORIAL_APRENDIZADO_CONTINUO.md` - Tutorial prático

---

**Desenvolvido com ❤️ para aprendizado contínuo eficiente**
