# 🚀 Guia de Configuração CI/CD - GitHub Actions

Este guia explica como configurar o pipeline de **Aprendizado Contínuo** do Cérebro de QA no GitHub Actions.

## 📋 Pré-requisitos

1. ✅ Repositório Git criado e conectado ao GitHub
2. ✅ Chave de API da OpenAI válida
3. ✅ Acesso de administrador ao repositório

## 🔧 Passo a Passo

### 1. Adicionar Secret da OpenAI ao GitHub

A chave de API da OpenAI precisa estar disponível como **GitHub Secret** para ser usada no pipeline CI/CD.

**Passos:**

1. Acesse seu repositório no GitHub
2. Clique em **Settings** (Configurações)
3. No menu lateral, clique em **Secrets and variables** → **Actions**
4. Clique em **New repository secret**
5. Preencha:
   - **Name:** `OPENAI_API_KEY`
   - **Secret:** Cole sua chave de API da OpenAI (começa com `sk-...`)
6. Clique em **Add secret**

✅ **Pronto!** A chave estará disponível para o workflow como `${{ secrets.OPENAI_API_KEY }}`

---

### 2. Verificar o Workflow

O arquivo de workflow já está criado em:
```
.github/workflows/rag-ingestion.yml
```

**O que ele faz:**

1. 🔍 **Detecta alterações** - Usa `git diff` para identificar arquivos `.py` e `.md` modificados
2. 📦 **Instala dependências** - Configura Python e instala pacotes do `requirements.txt`
3. 🧠 **Executa ingestão delta** - Processa apenas os arquivos alterados
4. ✅ **Valida o banco** - Executa `validate_ingestion.py` para garantir integridade
5. 💾 **Salva artefatos** - Faz upload do ChromaDB atualizado
6. 💬 **Comenta no PR** - Informa quais arquivos foram processados (em Pull Requests)

---

### 3. Testar Localmente (Opcional mas Recomendado)

Antes de fazer push para o GitHub, você pode simular o pipeline localmente:

```bash
# Teste rápido (sem git diff)
python test_cicd_local.py --quick

# Simulação completa (com git diff)
python test_cicd_local.py
```

Isso permite validar que tudo está funcionando antes de acionar o GitHub Actions.

---

### 4. Ativar o Pipeline

**Para ativar o pipeline CI/CD:**

1. Modifique um arquivo de código ou documentação:
   ```bash
   # Exemplo: adicione uma nova regra ao código
   code data/code_example.py
   ```

2. Faça commit e push:
   ```bash
   git add data/code_example.py
   git commit -m "feat: adiciona nova regra de negócio X"
   git push origin main
   ```

3. Acompanhe a execução:
   - Acesse seu repositório no GitHub
   - Clique na aba **Actions**
   - Você verá o workflow **🧠 Cérebro de QA - Aprendizado Contínuo** em execução

---

## 🎯 Fluxo de Trabalho

### Push Direto (main)
```
Desenvolvedor modifica código
         ↓
    git push origin main
         ↓
GitHub Actions detecta mudanças
         ↓
Executa ingestão delta (apenas arquivos alterados)
         ↓
Atualiza ChromaDB
         ↓
Salva artefato (chroma-db-<SHA>)
         ↓
✅ Cérebro de QA atualizado!
```

### Pull Request
```
Desenvolvedor cria PR
         ↓
GitHub Actions executa pipeline
         ↓
Valida ingestão
         ↓
Posta comentário no PR com detalhes
         ↓
Time de QA pode revisar impacto
         ↓
Após merge: banco atualizado automaticamente
```

---

## 📊 Artefatos Gerados

Cada execução gera 2 artefatos:

### 1. `chroma-db-<SHA>`
- **Conteúdo:** Banco de dados vetorial completo atualizado
- **Retenção:** 30 dias
- **Uso:** Pode ser baixado para testes locais ou restauração

### 2. `ingestion-report-<SHA>`
- **Conteúdo:** Relatório markdown com estatísticas da ingestão
- **Retenção:** 90 dias
- **Uso:** Auditoria e análise de mudanças

**Para baixar:**
1. Acesse **Actions** → Clique na execução desejada
2. Role até **Artifacts** no final da página
3. Clique para baixar

---

## 🔧 Personalização

### Modificar quais arquivos disparam o pipeline

Edite `.github/workflows/rag-ingestion.yml`:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'data/**.py'           # Apenas arquivos Python em data/
      - 'data/**.md'           # Apenas arquivos Markdown em data/
      - 'src/**.py'            # Código-fonte do projeto
      - 'docs/**.md'           # Adicione documentação
      - '**.java'              # Adicione outros tipos de arquivo
```

### Modificar frequência de execução

Você pode adicionar execução agendada:

```yaml
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Todo dia às 2h da manhã
```

### Mudar modelo LLM ou embeddings

Edite `src/core/delta_ingestion.py`:

```python
TRANSLATION_MODEL = "gpt-4o"  # Modelo mais poderoso
EMBEDDING_MODEL = "text-embedding-3-large"  # Embeddings maiores
```

---

## 🐛 Troubleshooting

### Erro: "OPENAI_API_KEY not found"
**Solução:** Verifique se o secret foi adicionado corretamente (Passo 1)

### Erro: "No changed files detected"
**Solução:** Certifique-se de modificar arquivos `.py` ou `.md` que estejam nos paths configurados

### Workflow não executa
**Solução:** Verifique se o arquivo `.github/workflows/rag-ingestion.yml` está na branch `main`

### Erro de permissão no ChromaDB
**Solução:** O ChromaDB usa SQLite. Em ambientes compartilhados, considere usar PGVector ou Pinecone

---

## 📈 Próximos Passos

1. **Monitoramento:** Configure notificações no Slack/Discord para execuções
2. **Testes A/B:** Compare diferentes modelos LLM via diferentes branches
3. **Deploy Automático:** Após ingestão, faça deploy do Streamlit automaticamente
4. **Multi-repo:** Configure para monitorar múltiplos repositórios

---

## 🎓 Referências

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

**Dúvidas?** Abra uma issue no repositório! 🚀
