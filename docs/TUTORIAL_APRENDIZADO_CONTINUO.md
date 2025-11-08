# 🎓 Tutorial: Testando o Aprendizado Contínuo

Este tutorial mostra como o Cérebro de QA **aprende automaticamente** quando você adiciona novas regras de negócio ao código.

## 🎯 Objetivo

Demonstrar o ciclo completo de **aprendizado contínuo**:
1. ✅ Adicionar uma nova regra de negócio ao código
2. ✅ Fazer commit e push para o GitHub
3. ✅ GitHub Actions detecta a mudança
4. ✅ Sistema processa apenas o arquivo alterado (delta)
5. ✅ ChromaDB é atualizado automaticamente
6. ✅ Nova regra fica disponível para geração de testes

---

## 📝 Passo a Passo

### 1. Adicionar Nova Regra ao Código

Vamos adicionar uma nova regra de **cashback progressivo** ao `data/code_example.py`:

```python
def calculate_cashback(total_value: float, customer_tier: str, payment_method: str) -> float:
    """
    Calcula o cashback baseado no valor, tier do cliente e forma de pagamento.
    
    Regras de Negócio:
    - Tier Bronze: 1% de cashback
    - Tier Prata: 2% de cashback  
    - Tier Ouro: 3% de cashback
    - Tier Platina: 5% de cashback
    - Pagamento via PIX: +0.5% adicional
    - Compras acima de R$ 500: +0.5% adicional
    - Cashback máximo: R$ 100 por transação
    """
    
    # Cashback base por tier
    tier_percentages = {
        'BRONZE': 0.01,
        'PRATA': 0.02,
        'OURO': 0.03,
        'PLATINA': 0.05
    }
    
    cashback_percentage = tier_percentages.get(customer_tier.upper(), 0.01)
    
    # Bônus PIX
    if payment_method.upper() == 'PIX':
        cashback_percentage += 0.005
    
    # Bônus compra alta
    if total_value > 500:
        cashback_percentage += 0.005
    
    # Calcula valor do cashback
    cashback = total_value * cashback_percentage
    
    # Limite máximo
    return min(cashback, 100.0)
```

**Como adicionar:**

```bash
# Abra o arquivo
code data/code_example.py

# Cole a função acima no final do arquivo

# Salve (Ctrl+S)
```

---

### 2. Testar Localmente (Recomendado)

Antes de fazer push, teste se o sistema consegue processar a mudança:

```bash
# Simula o pipeline CI/CD localmente
python test_cicd_local.py --quick
```

**Saída esperada:**
```
🚀 TESTE RÁPIDO - INGESTÃO DELTA
================================================
📁 Processando 1 arquivo(s) de teste...
   - data/code_example.py

🧠 CÉREBRO DE QA - INGESTÃO DELTA
================================================
📄 Processando: data/code_example.py
    🔄 Traduzindo código em regras de negócio...
    ✅ X chunks criados

💾 Adicionando X chunks ao banco vetorial...
   ✅ Chunks adicionados ao banco existente!

📊 RELATÓRIO DA INGESTÃO DELTA
================================================
✅ Arquivos processados: 1/1
📦 Total de chunks: X
   └─ Código: X chunks
   └─ Docs:   0 chunks
```

---

### 3. Commit e Push

```bash
# Adicionar arquivo modificado
git add data/code_example.py

# Commit com mensagem descritiva
git commit -m "feat: adiciona regra de cashback progressivo"

# Push para o GitHub
git push origin main
```

---

### 4. Acompanhar Execução no GitHub

1. **Acesse seu repositório no GitHub**
2. **Clique na aba "Actions"**
3. **Você verá o workflow "🧠 Cérebro de QA - Aprendizado Contínuo" em execução**

**Etapas do workflow:**
- ✅ Checkout do código
- ✅ Configurar Python 3.10
- ✅ Instalar dependências
- ✅ Detectar arquivos alterados (git diff)
- ✅ Executar ingestão delta
- ✅ Validar banco de dados
- ✅ Upload de artefatos

**Tempo estimado:** 2-3 minutos

---

### 5. Verificar Logs do Workflow

Clique na execução para ver os logs detalhados:

```
🔍 Detectando alterações: HEAD^..HEAD
   ✅ 1 arquivo(s) Python/Markdown alterado(s)
      - data/code_example.py

🧠 CÉREBRO DE QA - INGESTÃO DELTA
================================================
📄 Processando: data/code_example.py
    🔄 Traduzindo código em regras de negócio...
    ✅ 8 chunks criados

📊 RELATÓRIO DA INGESTÃO DELTA
================================================
✅ Arquivos processados: 1/1
📦 Total de chunks: 8
   └─ Código: 8 chunks
   └─ Docs:   0 chunks
❌ Erros: 0

🎉 CÉREBRO DE QA ATUALIZADO COM SUCESSO!
```

---

### 6. Baixar Artefatos (Opcional)

O workflow salva 2 artefatos:

**1. ChromaDB Atualizado** (`chroma-db-<SHA>`)
- Banco de dados completo com a nova regra
- Válido por 30 dias

**2. Relatório de Ingestão** (`ingestion-report-<SHA>`)
- Estatísticas da execução
- Válido por 90 dias

**Para baixar:**
1. Role até o final da página da execução
2. Seção **Artifacts**
3. Clique para fazer download

---

### 7. Testar a Nova Regra

Agora a regra de **cashback** está disponível no sistema!

**Via Streamlit:**
```bash
streamlit run app.py
```

**Query de teste:**
```
Gere cenários de teste BDD para o cálculo de cashback progressivo, 
incluindo diferentes tiers de clientes e métodos de pagamento.
```

**Resultado esperado:**
O plano de testes BDD incluirá cenários baseados nas regras de cashback que você acabou de adicionar! 🎉

---

## 🔄 Ciclo Contínuo

A partir de agora, **toda vez que você modificar código ou documentação**:

```
Código alterado → git push → GitHub Actions → Ingestão Delta → ChromaDB atualizado
```

**Sem intervenção manual!** O sistema aprende continuamente. 🧠

---

## 🎯 Testes Adicionais

### Teste 1: Adicionar Regra na Documentação

Edite `data/doc_example.md` e adicione:

```markdown
## Sistema de Cashback

### Regras de Cashback Progressivo

**Regra Documentada:** O sistema oferece cashback progressivo baseado no tier do cliente.

Tiers e percentuais:
- Bronze: 1% de cashback
- Prata: 2% de cashback
- Ouro: 3% de cashback
- Platina: 5% de cashback

**Regra Documentada:** Pagamentos via PIX recebem 0.5% adicional de cashback.

**Regra Documentada:** Compras acima de R$ 500 ganham 0.5% extra de cashback.

**Regra Documentada:** O cashback máximo por transação é de R$ 100.
```

Faça commit e push:
```bash
git add data/doc_example.md
git commit -m "docs: adiciona documentação de cashback"
git push origin main
```

### Teste 2: Modificar Regra Existente

Altere uma regra existente (ex: mudar o valor mínimo de frete grátis) e observe o sistema reaprender.

### Teste 3: Pull Request

Crie uma branch, adicione uma regra e abra um PR:
```bash
git checkout -b feature/nova-regra
# ... modifique arquivos ...
git push origin feature/nova-regra
```

O GitHub Actions comentará no PR mostrando quais arquivos serão processados! 💬

---

## 📊 Monitoramento

**Onde acompanhar:**
- ✅ GitHub Actions → Histórico de execuções
- ✅ Artefatos salvos → ChromaDB de cada versão
- ✅ Streamlit → Testar queries com conhecimento atualizado
- ✅ `validate_ingestion.py` → Verificar chunks armazenados

---

## 🎓 Conceitos Aprendidos

✅ **Ingestão Delta** - Processar apenas mudanças (eficiente)  
✅ **Git Diff** - Detectar arquivos alterados automaticamente  
✅ **GitHub Actions** - Pipeline CI/CD automatizado  
✅ **Aprendizado Contínuo** - Sistema que melhora a cada commit  
✅ **RAG Dinâmico** - Base de conhecimento sempre atualizada  

---

## 🚀 Próximo Nível

Experimente:
1. ✅ Adicionar suporte a outros tipos de arquivo (`.java`, `.js`)
2. ✅ Integrar com Jira/Confluence para capturar documentação externa
3. ✅ Criar notificações no Slack quando o sistema aprender algo novo
4. ✅ Implementar métricas de cobertura de regras

---

**Parabéns!** 🎉 Você agora tem um **Analista de QA Inteligente** que aprende automaticamente com seu código!
