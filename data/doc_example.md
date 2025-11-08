# Documentação de Regras de Negócio - Módulo de Pagamento e E-commerce

## 1. Processamento de Pedidos

### 1.1. Validação de Usuário

**Regra Documentada:** Todo novo usuário deve ter um CPF válido (11 dígitos) e ser maior de 18 anos para completar o cadastro. Esta é uma regra de negócio crítica para compliance com a LGPD e requisitos legais.

**Regra Documentada:** Emails de domínios temporários (exemplo: tempmail.com, throwaway.email) não são permitidos no cadastro. Esta regra visa garantir a qualidade da base de clientes e evitar fraudes.

**Regra Documentada:** O telefone informado no cadastro deve incluir o DDD e ter no mínimo 10 dígitos (fixo) ou 11 dígitos (celular). Esta informação é essencial para contato em caso de problemas com pedidos.

### 1.2. Regras de Desconto e Cupons

**Regra Documentada:** O desconto máximo aplicável a um pedido é de 20% do valor total. Qualquer combinação de cupons ou promoções que exceda este limite deve ser rejeitada pelo sistema.

**Regra Documentada:** Cupons promocionais não são cumulativos. Apenas um cupom pode ser aplicado por pedido. O cliente deve escolher o cupom mais vantajoso para sua compra.

**Regra Documentada:** Cupons de "primeira compra" (como NEWUSER) só podem ser utilizados uma única vez por CPF. O sistema deve validar se é realmente a primeira compra do cliente antes de aceitar o cupom.

**Regra Documentada:** Cupons com limite de desconto em reais (exemplo: máximo R$ 200 de desconto) devem ter este limite respeitado, mesmo que o percentual aplicado resulte em valor maior.

## 2. Regras de Frete e Logística

### 2.1. Cálculo de Frete

**Regra Documentada:** O valor base do frete é R$ 25,00 para a região Sudeste. Clientes Prime têm 50% de desconto no valor final do frete, aplicado após os acréscimos regionais.

**Regra Documentada:** Regiões Norte e Nordeste têm acréscimos no frete devido à maior distância e complexidade logística:
- Região Norte: acréscimo de R$ 15,00
- Região Nordeste: acréscimo de R$ 10,00
- Outras regiões: sem acréscimo adicional

**Regra Documentada:** Pedidos com valor total igual ou superior a R$ 1.000,00 têm frete grátis, independentemente da região ou status Prime do cliente. Esta é uma regra promocional permanente.

### 2.2. Prazos de Entrega

**Regra Documentada:** Os prazos de entrega variam por região:
- Sudeste: 3 a 5 dias úteis
- Sul: 5 a 7 dias úteis
- Centro-Oeste: 7 a 10 dias úteis
- Nordeste: 10 a 15 dias úteis
- Norte: 15 a 20 dias úteis

**Regra Documentada:** Clientes Prime têm prioridade no processamento e seus prazos são reduzidos em 50% (arredondando para cima).

## 3. Regras de Parcelamento

### 3.1. Condições Gerais

**Regra Documentada:** Parcelamento está disponível apenas para pagamentos com cartão de crédito. Pagamentos via PIX, boleto ou débito devem ser à vista.

**Regra Documentada:** O valor mínimo para habilitar parcelamento é R$ 50,00. Pedidos abaixo deste valor devem ser pagos à vista.

**Regra Documentada:** Cada parcela individual deve ter valor mínimo de R$ 50,00. O sistema deve calcular automaticamente o número máximo de parcelas baseado nesta regra.

### 3.2. Taxas e Juros

**Regra Documentada:** Compras parceladas em até 3 vezes são isentas de juros. Esta é uma política comercial padrão da empresa.

**Regra Documentada:** Parcelamentos de 4 a 12 vezes têm taxa de juros de 2,99% ao mês, calculada de forma composta sobre o valor total da compra.

**Regra Documentada:** O número máximo de parcelas permitido é 12x, independentemente do valor da compra.

## 4. Programa de Fidelidade

### 4.1. Tiers de Clientes

**Regra Documentada:** O programa de fidelidade possui 4 tiers (níveis):
- Bronze: cliente novo ou com menos de 1.000 pontos acumulados
- Silver: entre 1.000 e 2.999 pontos acumulados
- Gold: entre 3.000 e 9.999 pontos acumulados
- Platinum: 10.000 pontos ou mais acumulados

**Regra Documentada:** A mudança de tier é automática e acontece imediatamente quando o cliente atinge a pontuação necessária.

### 4.2. Acúmulo de Pontos

**Regra Documentada:** Pontos são acumulados com base no valor da compra e no tier do cliente:
- Bronze: 1 ponto por real gasto
- Silver: 1,5 pontos por real gasto
- Gold: 2 pontos por real gasto
- Platinum: 3 pontos por real gasto

**Regra Documentada:** Compras acima de R$ 500,00 recebem um bônus adicional de 100 pontos, independentemente do tier do cliente.

**Regra Documentada:** Pontos são creditados na conta do cliente em até 7 dias úteis após a confirmação da entrega do pedido.

### 4.3. Resgate e Validade

**Regra Documentada:** Cada 100 pontos equivalem a R$ 1,00 de desconto em compras futuras. O resgate mínimo é de 500 pontos (R$ 5,00).

**Regra Documentada:** Pontos têm validade de 12 meses a partir da data de acúmulo. Pontos expirados são removidos automaticamente da conta do cliente.

**Regra Documentada:** Pontos não podem ser transferidos entre contas de clientes diferentes.

## 5. Política de Cancelamento e Devolução

### 5.1. Cancelamento de Pedidos

**Regra Documentada:** Pedidos podem ser cancelados sem custo em até 24 horas após a confirmação, desde que ainda não tenham sido despachados.

**Regra Documentada:** Após o despacho, o cancelamento não é mais possível. O cliente deve aguardar a entrega e solicitar devolução se necessário.

### 5.2. Devolução de Produtos

**Regra Documentada:** O cliente tem direito a devolver o produto em até 7 dias após o recebimento (Código de Defesa do Consumidor), sem necessidade de justificativa.

**Regra Documentada:** Produtos devolvidos devem estar na embalagem original, sem sinais de uso, com todos os acessórios e manuais incluídos.

**Regra Documentada:** O estorno do valor pago é realizado na mesma forma de pagamento utilizada na compra:
- Cartão de crédito: estorno em até 2 faturas
- PIX/Débito: devolução em até 5 dias úteis
- Boleto: depósito bancário em até 10 dias úteis

**Regra Documentada:** O custo do frete de devolução é por conta do cliente, exceto em casos de:
- Produto com defeito de fabricação
- Produto errado enviado
- Produto danificado no transporte

## 6. Segurança e Prevenção de Fraudes

### 6.1. Validações de Segurança

**Regra Documentada:** Pedidos acima de R$ 3.000,00 são automaticamente encaminhados para análise manual de fraude antes da aprovação.

**Regra Documentada:** Endereços de entrega que sejam diferentes do endereço de cobrança cadastrado devem ser previamente validados pelo cliente via email ou SMS.

**Regra Documentada:** Múltiplas tentativas de compra com cartões diferentes pelo mesmo CPF em intervalo inferior a 1 hora geram bloqueio temporário da conta para análise.

### 6.2. Proteção de Dados

**Regra Documentada:** Dados de cartão de crédito não são armazenados nos servidores da empresa. Apenas o token criptografado fornecido pelo gateway de pagamento é mantido.

**Regra Documentada:** Senhas de clientes devem ter no mínimo 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.

**Regra Documentada:** Após 5 tentativas consecutivas de login com senha incorreta, a conta é bloqueada temporariamente por 30 minutos.
