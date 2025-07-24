"""
Funções utilitárias para o microsserviço de pedidos
"""
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

def calcular_total_pedido(itens: List[Dict[str, Any]]) -> Decimal:
    """
    Calcula o total de um pedido baseado nos itens
    
    Args:
        itens: Lista de itens do pedido
        
    Returns:
        Decimal: Total do pedido
    """
    if not itens:
        return Decimal('0.00')
    
    total = Decimal('0.00')
    for item in itens:
        quantidade = item.get('quantidade', 0)
        preco_unitario = Decimal(str(item.get('preco_unitario', 0)))
        total += quantidade * preco_unitario
    
    return total

def validar_cpf(cpf: str) -> bool:
    """
    Valida se um CPF está no formato correto
    
    Args:
        cpf: String do CPF
        
    Returns:
        bool: True se válido, False caso contrário
    """
    if not cpf:
        return False
    
    # Remove caracteres não numéricos
    cpf_numeros = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf_numeros) != 11:
        return False
    
    # Verifica se não são todos iguais
    if cpf_numeros == cpf_numeros[0] * 11:
        return False
    
    return True

def formatar_moeda(valor: Decimal) -> str:
    """
    Formata um valor decimal como moeda brasileira
    
    Args:
        valor: Valor em Decimal
        
    Returns:
        str: Valor formatado como moeda
    """
    if valor is None:
        return "R$ 0,00"
    
    return f"R$ {valor:.2f}".replace('.', ',')

def gerar_numero_pedido() -> str:
    """
    Gera um número único para o pedido
    
    Returns:
        str: Número do pedido
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PED{timestamp}"

def validar_item_pedido(item: Dict[str, Any]) -> List[str]:
    """
    Valida um item de pedido e retorna lista de erros
    
    Args:
        item: Dicionário com dados do item
        
    Returns:
        List[str]: Lista de erros encontrados
    """
    erros = []
    
    if not item.get('produto_id'):
        erros.append("ID do produto é obrigatório")
    
    if not item.get('nome_produto'):
        erros.append("Nome do produto é obrigatório")
    
    if not item.get('categoria'):
        erros.append("Categoria é obrigatória")
    
    quantidade = item.get('quantidade', 0)
    if not isinstance(quantidade, int) or quantidade <= 0:
        erros.append("Quantidade deve ser um número inteiro positivo")
    
    try:
        preco = Decimal(str(item.get('preco_unitario', 0)))
        if preco <= 0:
            erros.append("Preço unitário deve ser maior que zero")
    except:
        erros.append("Preço unitário deve ser um número válido")
    
    return erros

def converter_status_para_display(status: str) -> str:
    """
    Converte status interno para exibição amigável
    
    Args:
        status: Status interno
        
    Returns:
        str: Status para exibição
    """
    status_map = {
        'RECEBIDO': 'Pedido Recebido',
        'EM_PREPARACAO': 'Em Preparação',
        'PRONTO': 'Pronto para Retirada',
        'FINALIZADO': 'Finalizado'
    }
    
    return status_map.get(status, status)

def calcular_tempo_preparo(categoria: str, quantidade: int) -> int:
    """
    Calcula tempo estimado de preparo em minutos
    
    Args:
        categoria: Categoria do produto
        quantidade: Quantidade de itens
        
    Returns:
        int: Tempo em minutos
    """
    tempo_base = {
        'Lanche': 15,
        'Acompanhamento': 8,
        'Bebida': 3,
        'Sobremesa': 10
    }
    
    base = tempo_base.get(categoria, 10)
    return base + (quantidade - 1) * 2  # 2 min adicional por item extra

def sanitizar_entrada(texto: str) -> str:
    """
    Remove caracteres especiais de uma entrada de texto
    
    Args:
        texto: Texto a ser sanitizado
        
    Returns:
        str: Texto sanitizado
    """
    if not texto:
        return ""
    
    # Remove caracteres especiais, mantém apenas letras, números e espaços
    import re
    return re.sub(r'[^a-zA-Z0-9\sÀ-ÿ]', '', texto).strip()

def agrupar_itens_por_categoria(itens: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Agrupa itens de pedido por categoria
    
    Args:
        itens: Lista de itens
        
    Returns:
        Dict: Itens agrupados por categoria
    """
    if not itens:
        return {}
    
    grupos = {}
    for item in itens:
        categoria = item.get('categoria', 'Outros')
        if categoria not in grupos:
            grupos[categoria] = []
        grupos[categoria].append(item)
    
    return grupos

def calcular_desconto(total: Decimal, tipo_desconto: str, valor_desconto: Decimal) -> Decimal:
    """
    Calcula desconto aplicado ao pedido
    
    Args:
        total: Total do pedido
        tipo_desconto: 'percentual' ou 'fixo'
        valor_desconto: Valor do desconto
        
    Returns:
        Decimal: Valor do desconto
    """
    if total <= 0 or valor_desconto <= 0:
        return Decimal('0.00')
    
    if tipo_desconto == 'percentual':
        desconto = total * (valor_desconto / 100)
        return min(desconto, total)  # Desconto não pode ser maior que o total
    elif tipo_desconto == 'fixo':
        return min(valor_desconto, total)
    
    return Decimal('0.00')

def gerar_resumo_pedido(pedido_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera resumo completo do pedido
    
    Args:
        pedido_data: Dados do pedido
        
    Returns:
        Dict: Resumo do pedido
    """
    itens = pedido_data.get('itens', [])
    total = calcular_total_pedido(itens)
    grupos = agrupar_itens_por_categoria(itens)
    
    # Calcular tempo total de preparo
    tempo_total = 0
    for item in itens:
        categoria = item.get('categoria', 'Outros')
        quantidade = item.get('quantidade', 1)
        tempo_total += calcular_tempo_preparo(categoria, quantidade)
    
    return {
        'numero_pedido': gerar_numero_pedido(),
        'total_itens': len(itens),
        'valor_total': total,
        'valor_formatado': formatar_moeda(total),
        'grupos_categoria': grupos,
        'tempo_preparo_estimado': tempo_total,
        'status_display': converter_status_para_display(pedido_data.get('status', 'RECEBIDO'))
    }

def validar_dados_pedido_completo(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validação completa dos dados de um pedido
    
    Args:
        dados: Dados do pedido
        
    Returns:
        Dict: Resultado da validação
    """
    erros = []
    warnings = []
    
    # Validar cliente
    cliente_id = dados.get('cliente_id')
    if cliente_id and not validar_cpf(cliente_id):
        warnings.append("CPF do cliente pode estar inválido")
    
    # Validar itens
    itens = dados.get('itens', [])
    if not itens:
        erros.append("Pedido deve ter pelo menos um item")
    
    for i, item in enumerate(itens):
        erros_item = validar_item_pedido(item)
        for erro in erros_item:
            erros.append(f"Item {i+1}: {erro}")
    
    # Calcular totais
    total = calcular_total_pedido(itens)
    if total <= 0:
        erros.append("Total do pedido deve ser maior que zero")
    
    return {
        'valido': len(erros) == 0,
        'erros': erros,
        'warnings': warnings,
        'total_calculado': total,
        'resumo': gerar_resumo_pedido(dados) if len(erros) == 0 else None
    }

