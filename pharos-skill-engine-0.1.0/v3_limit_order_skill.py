import math
import json
from web3 import Web3

# ---------------------------------------------------------
# PHAROS AGENT CENTER SKILL: DeFi V3 Limit Order
# Version: 1.0 (Hackathon Ready)
# ---------------------------------------------------------

class V3LimitOrderSkill:
    def __init__(self, rpc_url="https://rpc.pharos.xyz"):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Dicionário de Traduções (i18n)
        self.locales = {
            "en": {
                "error_amount": "Amount must be greater than zero.",
                "processing": "Agent processing Limit Order via Uniswap V3...",
                "success": "Transaction payload generated successfully! Ready for wallet signature.",
                "action_desc": "Creating a unilateral liquidity position for Target Price: $"
            },
            "pt": {
                "error_amount": "A quantidade deve ser maior que zero.",
                "processing": "Agente a processar Ordem Limite via Uniswap V3...",
                "success": "Dados da transação gerados com sucesso! Pronto para assinatura na carteira.",
                "action_desc": "A criar posição de liquidez unilateral para o Preço Alvo: $"
            },
            "kr": {
                "error_amount": "수량은 0보다 커야 합니다.",
                "processing": "에이전트가 Uniswap V3를 통해 지정가 주문을 처리 중입니다...",
                "success": "트랜잭션 페이로드가 성공적으로 생성되었습니다! 지갑 서명 준비 완료.",
                "action_desc": "목표 가격에 대한 일방적 유동성 포지션 생성 중: $"
            }
        }

    def _price_to_tick(self, price, token0_decimals=18, token1_decimals=18):
        """Calcula o Tick exato da Uniswap V3 com base no Preço Alvo"""
        if price <= 0: return 0
        adjusted_price = price * (10 ** (token1_decimals - token0_decimals))
        tick = math.log(adjusted_price) / math.log(1.0001)
        return int(tick)

    def generate_limit_order_payload(self, wallet_address, token_in, token_out, amount, target_price, lang="en"):
        """
        Função principal consumida pelo Agente de IA.
        Retorna um dicionário (JSON) padronizado.
        """
        # Fallback de idioma
        if lang not in self.locales:
            lang = "en"
            
        lang_dict = self.locales[lang]

        # Validação básica
        if amount <= 0:
            return {"status": "error", "message": lang_dict["error_amount"], "payload": None}

        # Cálculo de Ticks
        target_tick = self._price_to_tick(target_price)
        tick_lower = target_tick - 1
        tick_upper = target_tick + 1

        # Montagem da Transação Real para a Blockchain
        payload = {
            "contractAddress": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88", # Position Manager
            "method": "mint",
            "params": {
                "token0": token_in,
                "token1": token_out,
                "tickLower": tick_lower,
                "tickUpper": tick_upper,
                "amount0Desired": amount,
                "amount1Desired": 0
            },
            "estimatedGas": "350000"
        }

        # Resposta Estruturada para a IA
        response = {
            "status": "success",
            "agent_message": f"{lang_dict['processing']}\n{lang_dict['action_desc']}{target_price}",
            "system_message": lang_dict["success"],
            "wallet": wallet_address,
            "transaction_payload": payload
        }
        
        return response

# --- SIMULAÇÃO DA SKILL NO TERMINAL ---
if __name__ == "__main__":
    skill = V3LimitOrderSkill()
    
    # Simulação 1: Um utilizador a falar em Coreano
    resultado_kr = skill.generate_limit_order_payload(
        wallet_address="0x123...abc",
        token_in="PHR",
        token_out="USDC",
        amount=1000,
        target_price=5.00,
        lang="kr" # Mudando o idioma aqui!
    )
    
    # Imprime o resultado formatado como JSON para vermos como a IA recebe
    print("--- TESTE EM COREANO (KR) ---")
    print(json.dumps(resultado_kr, indent=4, ensure_ascii=False))
    print("\n")
    
    # Simulação 2: Um utilizador a falar em Inglês
    resultado_en = skill.generate_limit_order_payload(
        wallet_address="0x123...abc",
        token_in="PHR",
        token_out="USDC",
        amount=1000,
        target_price=5.00,
        lang="en"
    )
    
    print("--- TESTE EM INGLÊS (EN) ---")
    print(json.dumps(resultado_en, indent=4))