# Arquivo de código simulado: payment_service.py

def calculate_shipping(order_value: float, is_prime_customer: bool, customer_region: str = "sudeste") -> float:
    """
    Calcula o valor do frete com base no valor do pedido, status do cliente e região.
    """
    SHIPPING_FEE = 25.00
    FREE_SHIPPING_THRESHOLD = 1000.00
    PRIME_DISCOUNT = 0.5  # 50% de desconto
    NORTH_REGION_SURCHARGE = 15.00  # Acréscimo para região Norte
    NORTHEAST_REGION_SURCHARGE = 10.00  # Acréscimo para região Nordeste

    if order_value >= FREE_SHIPPING_THRESHOLD:
        # Regra 1: Frete grátis para pedidos acima de R$ 1000
        return 0.0
    
    base_fee = SHIPPING_FEE
    
    # Regra 2: Acréscimo regional no frete
    if customer_region.lower() == "norte":
        base_fee += NORTH_REGION_SURCHARGE
    elif customer_region.lower() == "nordeste":
        base_fee += NORTHEAST_REGION_SURCHARGE
    
    if is_prime_customer:
        # Regra 3: Clientes Prime têm 50% de desconto no frete (aplicado após acréscimos regionais)
        return base_fee * PRIME_DISCOUNT
    
    # Regra 4: Frete padrão com acréscimos regionais
    return base_fee


def validate_coupon(coupon_code: str, order_value: float, customer_email: str = "", is_first_purchase: bool = False) -> dict:
    """
    Valida se um cupom pode ser aplicado ao pedido e retorna detalhes da validação.
    """
    result = {
        "valid": False,
        "discount_percentage": 0,
        "max_discount": 0,
        "reason": ""
    }
    
    if coupon_code == "BLACKFRIDAY" and order_value >= 500:
        # Regra 5: Cupom BLACKFRIDAY só é válido para pedidos acima de R$ 500
        # Desconto de 20% com limite de R$ 200
        result["valid"] = True
        result["discount_percentage"] = 20
        result["max_discount"] = 200.00
        result["reason"] = "Cupom Black Friday aplicado"
        return result
    
    if coupon_code == "NEWUSER" and is_first_purchase and order_value < 100:
        # Regra 6: Cupom NEWUSER só é válido para primeira compra e pedidos abaixo de R$ 100
        # Desconto de 15% sem limite
        result["valid"] = True
        result["discount_percentage"] = 15
        result["max_discount"] = None
        result["reason"] = "Cupom novo usuário aplicado"
        return result
    
    if coupon_code == "VIP10" and "@vip.com" in customer_email:
        # Regra 7: Cupom VIP10 exclusivo para emails com domínio @vip.com
        # Desconto de 10% sem limite de valor
        result["valid"] = True
        result["discount_percentage"] = 10
        result["max_discount"] = None
        result["reason"] = "Cupom VIP aplicado"
        return result
        
    result["reason"] = "Cupom inválido ou não atende aos critérios"
    return result


def calculate_installments(order_value: float, requested_installments: int, has_credit_card: bool = True) -> dict:
    """
    Calcula as parcelas disponíveis para um pedido.
    """
    MIN_INSTALLMENT_VALUE = 50.00
    MAX_INSTALLMENTS_NO_INTEREST = 3
    MAX_INSTALLMENTS_WITH_INTEREST = 12
    INTEREST_RATE = 0.0299  # 2.99% ao mês
    
    result = {
        "approved": False,
        "installments": 0,
        "installment_value": 0,
        "total_value": 0,
        "has_interest": False,
        "reason": ""
    }
    
    if not has_credit_card:
        # Regra 8: Parcelamento só disponível para pagamento com cartão de crédito
        result["reason"] = "Parcelamento disponível apenas para cartão de crédito"
        return result
    
    if order_value < MIN_INSTALLMENT_VALUE:
        # Regra 9: Valor mínimo de R$ 50 para parcelar
        result["reason"] = f"Valor mínimo para parcelamento é R$ {MIN_INSTALLMENT_VALUE}"
        return result
    
    # Regra 10: Cada parcela deve ser no mínimo R$ 50
    max_possible_installments = int(order_value / MIN_INSTALLMENT_VALUE)
    
    if requested_installments > MAX_INSTALLMENTS_WITH_INTEREST:
        # Regra 11: Máximo de 12 parcelas
        result["reason"] = f"Máximo de {MAX_INSTALLMENTS_WITH_INTEREST} parcelas permitido"
        return result
    
    if requested_installments > max_possible_installments:
        # Regra 12: Parcela mínima de R$ 50
        result["reason"] = f"Parcela mínima deve ser R$ {MIN_INSTALLMENT_VALUE}. Máximo de {max_possible_installments} parcelas para este valor"
        return result
    
    if requested_installments <= MAX_INSTALLMENTS_NO_INTEREST:
        # Regra 13: Até 3x sem juros
        result["approved"] = True
        result["installments"] = requested_installments
        result["installment_value"] = order_value / requested_installments
        result["total_value"] = order_value
        result["has_interest"] = False
        result["reason"] = f"Parcelamento sem juros aprovado"
    else:
        # Regra 14: De 4x a 12x com juros de 2.99% ao mês
        total_with_interest = order_value * ((1 + INTEREST_RATE) ** requested_installments)
        result["approved"] = True
        result["installments"] = requested_installments
        result["installment_value"] = total_with_interest / requested_installments
        result["total_value"] = total_with_interest
        result["has_interest"] = True
        result["reason"] = f"Parcelamento com juros aprovado"
    
    return result


def validate_customer_registration(cpf: str, age: int, email: str, phone: str) -> dict:
    """
    Valida o cadastro de um novo cliente.
    """
    import re
    
    result = {
        "valid": False,
        "errors": []
    }
    
    # Regra 15: CPF deve ter exatamente 11 dígitos numéricos
    if not cpf.isdigit() or len(cpf) != 11:
        result["errors"].append("CPF inválido: deve conter 11 dígitos numéricos")
    
    # Regra 16: Cliente deve ser maior de 18 anos
    if age < 18:
        result["errors"].append("Cliente deve ter pelo menos 18 anos")
    
    # Regra 17: Email deve ter formato válido (contém @ e .)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        result["errors"].append("Email em formato inválido")
    
    # Regra 18: Telefone deve ter 10 ou 11 dígitos (DDD + número)
    phone_digits = re.sub(r'\D', '', phone)
    if len(phone_digits) not in [10, 11]:
        result["errors"].append("Telefone deve ter 10 ou 11 dígitos (incluindo DDD)")
    
    # Regra 19: Domínios de email temporários não são permitidos
    temp_domains = ["tempmail.com", "throwaway.email", "guerrillamail.com"]
    email_domain = email.split("@")[-1].lower() if "@" in email else ""
    if email_domain in temp_domains:
        result["errors"].append("Emails temporários não são permitidos")
    
    if not result["errors"]:
        result["valid"] = True
    
    return result


def apply_loyalty_points(customer_id: str, order_value: float, customer_tier: str = "bronze") -> dict:
    """
    Calcula e aplica pontos de fidelidade baseado no valor da compra e tier do cliente.
    """
    BRONZE_MULTIPLIER = 1.0  # 1 ponto por real
    SILVER_MULTIPLIER = 1.5  # 1.5 pontos por real
    GOLD_MULTIPLIER = 2.0    # 2 pontos por real
    PLATINUM_MULTIPLIER = 3.0  # 3 pontos por real
    BONUS_THRESHOLD = 500.00  # Bônus acima de R$ 500
    BONUS_POINTS = 100
    
    result = {
        "points_earned": 0,
        "bonus_points": 0,
        "total_points": 0,
        "tier": customer_tier,
        "next_tier_points": 0
    }
    
    # Regra 20: Multiplicador de pontos baseado no tier do cliente
    multiplier = BRONZE_MULTIPLIER
    if customer_tier.lower() == "silver":
        multiplier = SILVER_MULTIPLIER
    elif customer_tier.lower() == "gold":
        multiplier = GOLD_MULTIPLIER
    elif customer_tier.lower() == "platinum":
        multiplier = PLATINUM_MULTIPLIER
    
    base_points = int(order_value * multiplier)
    result["points_earned"] = base_points
    
    # Regra 21: Bônus de 100 pontos para compras acima de R$ 500
    if order_value >= BONUS_THRESHOLD:
        result["bonus_points"] = BONUS_POINTS
    
    result["total_points"] = result["points_earned"] + result["bonus_points"]
    
    # Regra 22: Informação sobre próximo tier
    if customer_tier.lower() == "bronze":
        result["next_tier_points"] = 1000 - result["total_points"]
    elif customer_tier.lower() == "silver":
        result["next_tier_points"] = 3000 - result["total_points"]
    elif customer_tier.lower() == "gold":
        result["next_tier_points"] = 10000 - result["total_points"]
    
    return result
