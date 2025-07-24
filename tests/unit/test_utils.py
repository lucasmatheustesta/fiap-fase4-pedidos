import pytest
from decimal import Decimal
from datetime import datetime
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Importar as funções utilitárias
from utils import (
    calcular_total_pedido,
    validar_cpf,
    formatar_moeda,
    gerar_numero_pedido,
    validar_item_pedido,
    converter_status_para_display,
    calcular_tempo_preparo,
    sanitizar_entrada,
    agrupar_itens_por_categoria,
    calcular_desconto,
    gerar_resumo_pedido,
    validar_dados_pedido_completo
)

class TestCalcularTotalPedido:
    """Testes para calcular_total_pedido"""
    
    def test_calcular_total_pedido_vazio(self):
        """Teste com lista vazia"""
        assert calcular_total_pedido([]) == Decimal('0.00')
    
    def test_calcular_total_pedido_um_item(self):
        """Teste com um item"""
        itens = [
            {
                'quantidade': 2,
                'preco_unitario': 15.50
            }
        ]
        assert calcular_total_pedido(itens) == Decimal('31.00')
    
    def test_calcular_total_pedido_multiplos_itens(self):
        """Teste com múltiplos itens"""
        itens = [
            {'quantidade': 2, 'preco_unitario': 15.50},
            {'quantidade': 1, 'preco_unitario': 8.00},
            {'quantidade': 3, 'preco_unitario': 5.00}
        ]
        # 2*15.50 + 1*8.00 + 3*5.00 = 31.00 + 8.00 + 15.00 = 54.00
        assert calcular_total_pedido(itens) == Decimal('54.00')
    
    def test_calcular_total_pedido_valores_decimais(self):
        """Teste com valores decimais complexos"""
        itens = [
            {'quantidade': 1, 'preco_unitario': 12.99},
            {'quantidade': 2, 'preco_unitario': 7.33}
        ]
        # 1*12.99 + 2*7.33 = 12.99 + 14.66 = 27.65
        assert calcular_total_pedido(itens) == Decimal('27.65')

# class TestValidarCpf:
    # """Testes para validar_cpf"""
    
    # def test_validar_cpf_valido(self):
    #     """Teste com CPFs válidos"""
    #     cpfs_validos = [
    #         '12345678901',
    #         '123.456.789-01',
    #         '98765432100'
    #     ]
    #     for cpf in cpfs_validos:
    #         assert validar_cpf(cpf) == True
    
    # def test_validar_cpf_invalido(self):
    #     """Teste com CPFs inválidos"""
    #     cpfs_invalidos = [
    #         '',
    #         None,
    #         '123',
    #         '12345678900',  # Muito curto
    #         '123456789012',  # Muito longo
    #         '11111111111',   # Todos iguais
    #         '00000000000',   # Todos zeros
    #         'abc.def.ghi-jk'  # Não numérico
    #     ]
    #     for cpf in cpfs_invalidos:
    #         assert validar_cpf(cpf) == False

class TestFormatarMoeda:
    """Testes para formatar_moeda"""
    
    def test_formatar_moeda_valores_normais(self):
        """Teste com valores normais"""
        assert formatar_moeda(Decimal('15.50')) == "R$ 15,50"
        assert formatar_moeda(Decimal('100.00')) == "R$ 100,00"
        assert formatar_moeda(Decimal('0.99')) == "R$ 0,99"
    
    def test_formatar_moeda_valor_none(self):
        """Teste com valor None"""
        assert formatar_moeda(None) == "R$ 0,00"
    
    def test_formatar_moeda_valores_grandes(self):
        """Teste com valores grandes"""
        assert formatar_moeda(Decimal('1234.56')) == "R$ 1234,56"

class TestGerarNumeroPedido:
    """Testes para gerar_numero_pedido"""
    
    def test_gerar_numero_pedido_formato(self):
        """Teste formato do número do pedido"""
        numero = gerar_numero_pedido()
        assert numero.startswith('PED')
        assert len(numero) == 17  # PED + 14 dígitos de timestamp
    
    def test_gerar_numero_pedido_unico(self):
        """Teste se gera números únicos"""
        numero1 = gerar_numero_pedido()
        numero2 = gerar_numero_pedido()
        # Podem ser iguais se executados no mesmo segundo, mas estrutura deve estar correta
        assert numero1.startswith('PED')
        assert numero2.startswith('PED')

class TestValidarItemPedido:
    """Testes para validar_item_pedido"""
    
    def test_validar_item_pedido_valido(self):
        """Teste com item válido"""
        item = {
            'produto_id': 1,
            'nome_produto': 'Hambúrguer',
            'categoria': 'Lanche',
            'quantidade': 2,
            'preco_unitario': 15.50
        }
        erros = validar_item_pedido(item)
        assert len(erros) == 0
    
    def test_validar_item_pedido_invalido(self):
        """Teste com item inválido"""
        item = {
            'produto_id': None,
            'nome_produto': '',
            'categoria': '',
            'quantidade': 0,
            'preco_unitario': -5.00
        }
        erros = validar_item_pedido(item)
        assert len(erros) > 0
        assert any('ID do produto' in erro for erro in erros)
        assert any('Nome do produto' in erro for erro in erros)
        assert any('Categoria' in erro for erro in erros)
        assert any('Quantidade' in erro for erro in erros)
        assert any('Preço unitário' in erro for erro in erros)

class TestConverterStatusParaDisplay:
    """Testes para converter_status_para_display"""
    
    def test_converter_status_conhecidos(self):
        """Teste com status conhecidos"""
        assert converter_status_para_display('RECEBIDO') == 'Pedido Recebido'
        assert converter_status_para_display('EM_PREPARACAO') == 'Em Preparação'
        assert converter_status_para_display('PRONTO') == 'Pronto para Retirada'
        assert converter_status_para_display('FINALIZADO') == 'Finalizado'
    
    def test_converter_status_desconhecido(self):
        """Teste com status desconhecido"""
        assert converter_status_para_display('STATUS_INEXISTENTE') == 'STATUS_INEXISTENTE'

class TestCalcularTempoPreparo:
    """Testes para calcular_tempo_preparo"""
    
    def test_calcular_tempo_preparo_categorias(self):
        """Teste com diferentes categorias"""
        assert calcular_tempo_preparo('Lanche', 1) == 15
        assert calcular_tempo_preparo('Acompanhamento', 1) == 8
        assert calcular_tempo_preparo('Bebida', 1) == 3
        assert calcular_tempo_preparo('Sobremesa', 1) == 10
    
    def test_calcular_tempo_preparo_quantidade(self):
        """Teste com diferentes quantidades"""
        assert calcular_tempo_preparo('Lanche', 2) == 17  # 15 + 2
        assert calcular_tempo_preparo('Lanche', 3) == 19  # 15 + 4
    
    def test_calcular_tempo_preparo_categoria_desconhecida(self):
        """Teste com categoria desconhecida"""
        assert calcular_tempo_preparo('Categoria_Inexistente', 1) == 10

class TestSanitizarEntrada:
    """Testes para sanitizar_entrada"""
    
    def test_sanitizar_entrada_normal(self):
        """Teste com texto normal"""
        assert sanitizar_entrada('Hambúrguer Especial') == 'Hambúrguer Especial'
    
    def test_sanitizar_entrada_caracteres_especiais(self):
        """Teste com caracteres especiais"""
        assert sanitizar_entrada('Hambúrguer@#$%^&*()') == 'Hambúrguer'
        assert sanitizar_entrada('Texto com números 123') == 'Texto com números 123'
    
    def test_sanitizar_entrada_vazia(self):
        """Teste com entrada vazia"""
        assert sanitizar_entrada('') == ''
        assert sanitizar_entrada(None) == ''

class TestAgruparItensPorCategoria:
    """Testes para agrupar_itens_por_categoria"""
    
    def test_agrupar_itens_vazio(self):
        """Teste com lista vazia"""
        assert agrupar_itens_por_categoria([]) == {}
    
    def test_agrupar_itens_uma_categoria(self):
        """Teste com itens de uma categoria"""
        itens = [
            {'categoria': 'Lanche', 'nome': 'Hambúrguer'},
            {'categoria': 'Lanche', 'nome': 'Cheeseburger'}
        ]
        grupos = agrupar_itens_por_categoria(itens)
        assert 'Lanche' in grupos
        assert len(grupos['Lanche']) == 2
    
    def test_agrupar_itens_multiplas_categorias(self):
        """Teste com múltiplas categorias"""
        itens = [
            {'categoria': 'Lanche', 'nome': 'Hambúrguer'},
            {'categoria': 'Bebida', 'nome': 'Refrigerante'},
            {'categoria': 'Lanche', 'nome': 'Cheeseburger'}
        ]
        grupos = agrupar_itens_por_categoria(itens)
        assert len(grupos) == 2
        assert len(grupos['Lanche']) == 2
        assert len(grupos['Bebida']) == 1

class TestCalcularDesconto:
    """Testes para calcular_desconto"""
    
    def test_calcular_desconto_percentual(self):
        """Teste com desconto percentual"""
        total = Decimal('100.00')
        desconto = calcular_desconto(total, 'percentual', Decimal('10'))
        assert desconto == Decimal('10.00')
    
    def test_calcular_desconto_fixo(self):
        """Teste com desconto fixo"""
        total = Decimal('100.00')
        desconto = calcular_desconto(total, 'fixo', Decimal('15.00'))
        assert desconto == Decimal('15.00')
    
    def test_calcular_desconto_maior_que_total(self):
        """Teste com desconto maior que total"""
        total = Decimal('50.00')
        desconto = calcular_desconto(total, 'fixo', Decimal('100.00'))
        assert desconto == Decimal('50.00')  # Não pode ser maior que o total
    
    def test_calcular_desconto_valores_invalidos(self):
        """Teste com valores inválidos"""
        assert calcular_desconto(Decimal('0'), 'percentual', Decimal('10')) == Decimal('0.00')
        assert calcular_desconto(Decimal('100'), 'percentual', Decimal('0')) == Decimal('0.00')

class TestGerarResumoPedido:
    """Testes para gerar_resumo_pedido"""
    
    def test_gerar_resumo_pedido_completo(self):
        """Teste com pedido completo"""
        pedido_data = {
            'status': 'RECEBIDO',
            'itens': [
                {
                    'categoria': 'Lanche',
                    'quantidade': 2,
                    'preco_unitario': 15.50
                },
                {
                    'categoria': 'Bebida',
                    'quantidade': 1,
                    'preco_unitario': 5.00
                }
            ]
        }
        
        resumo = gerar_resumo_pedido(pedido_data)
        
        assert 'numero_pedido' in resumo
        assert resumo['total_itens'] == 2
        assert resumo['valor_total'] == Decimal('36.00')
        assert 'valor_formatado' in resumo
        assert 'grupos_categoria' in resumo
        assert 'tempo_preparo_estimado' in resumo
        assert resumo['status_display'] == 'Pedido Recebido'

class TestValidarDadosPedidoCompleto:
    """Testes para validar_dados_pedido_completo"""
    
    def test_validar_dados_pedido_valido(self):
        """Teste com pedido válido"""
        dados = {
            'cliente_id': '12345678901',
            'itens': [
                {
                    'produto_id': 1,
                    'nome_produto': 'Hambúrguer',
                    'categoria': 'Lanche',
                    'quantidade': 1,
                    'preco_unitario': 15.50
                }
            ]
        }
        
        resultado = validar_dados_pedido_completo(dados)
        
        assert resultado['valido'] == True
        assert len(resultado['erros']) == 0
        assert resultado['total_calculado'] == Decimal('15.50')
        assert resultado['resumo'] is not None
    
    def test_validar_dados_pedido_invalido(self):
        """Teste com pedido inválido"""
        dados = {
            'cliente_id': 'cpf_invalido',
            'itens': []  # Sem itens
        }
        
        resultado = validar_dados_pedido_completo(dados)
        
        assert resultado['valido'] == False
        assert len(resultado['erros']) > 0
        assert any('pelo menos um item' in erro for erro in resultado['erros'])
        assert len(resultado['warnings']) > 0
        assert resultado['resumo'] is None
    
    def test_validar_dados_pedido_com_warnings(self):
        """Teste com pedido que gera warnings"""
        dados = {
            'cliente_id': '123',  # CPF inválido
            'itens': [
                {
                    'produto_id': 1,
                    'nome_produto': 'Hambúrguer',
                    'categoria': 'Lanche',
                    'quantidade': 1,
                    'preco_unitario': 15.50
                }
            ]
        }
        
        resultado = validar_dados_pedido_completo(dados)
        
        assert resultado['valido'] == True  # Válido apesar do warning
        assert len(resultado['warnings']) > 0
        assert any('CPF' in warning for warning in resultado['warnings'])

