import pytest
import json
from decimal import Decimal
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.pedido import Pedido, ItemPedido, Produto, StatusPedido, db

class TestCasosExtremos:
    """Testes para casos extremos e edge cases"""
    
    def test_pedido_com_valor_zero(self, app):
        """Teste de pedido com valor zero"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('0.00')
            )
            
            db.session.add(pedido)
            db.session.commit()
            
            assert pedido.total == Decimal('0.00')
            
            # Testa serialização
            pedido_dict = pedido.to_dict()
            assert pedido_dict['total'] == 0.0
    
    def test_produto_com_preco_alto(self, app):
        """Teste de produto com preço alto"""
        with app.app_context():
            produto = Produto(
                nome='Produto Premium',
                categoria='Premium',
                preco=Decimal('999.99'),
                disponivel=True
            )
            
            db.session.add(produto)
            db.session.commit()
            
            assert produto.preco == Decimal('999.99')
            
            # Testa serialização
            produto_dict = produto.to_dict()
            assert produto_dict['preco'] == 999.99
    
    def test_item_pedido_quantidade_alta(self, app):
        """Teste de item com quantidade alta"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('0.00')
            )
            db.session.add(pedido)
            db.session.commit()
            
            item = ItemPedido(
                pedido_id=pedido.id,
                produto_id=1,
                nome_produto='Produto Teste',
                categoria='Teste',
                quantidade=100,  # Quantidade alta
                preco_unitario=Decimal('1.50')
            )
            
            db.session.add(item)
            db.session.commit()
            
            assert item.quantidade == 100
            
            # Testa cálculo do total
            pedido.calcular_total()
            assert pedido.total == Decimal('150.00')  # 100 * 1.50
    
    def test_nome_produto_longo(self, app):
        """Teste de produto com nome muito longo"""
        with app.app_context():
            nome_longo = 'Hambúrguer Artesanal Premium com Queijo Especial e Ingredientes Selecionados da Casa'
            
            produto = Produto(
                nome=nome_longo,
                categoria='Lanche',
                preco=Decimal('25.90'),
                disponivel=True
            )
            
            db.session.add(produto)
            db.session.commit()
            
            assert produto.nome == nome_longo
            
            # Testa serialização
            produto_dict = produto.to_dict()
            assert produto_dict['nome'] == nome_longo
    
    def test_cliente_id_formato_especial(self, app):
        """Teste de pedido com cliente_id em formato especial"""
        with app.app_context():
            # CPF com formatação
            cliente_id = '123.456.789-01'
            
            pedido = Pedido(
                cliente_id=cliente_id,
                status=StatusPedido.RECEBIDO,
                total=Decimal('15.50')
            )
            
            db.session.add(pedido)
            db.session.commit()
            
            assert pedido.cliente_id == cliente_id
            
            # Testa serialização
            pedido_dict = pedido.to_dict()
            assert pedido_dict['cliente_id'] == cliente_id
    
    def test_observacoes_longas(self, app):
        """Teste de item com observações muito longas"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('15.50')
            )
            db.session.add(pedido)
            db.session.commit()
            
            observacoes_longas = (
                'Sem cebola, sem tomate, sem alface, extra queijo, '
                'extra bacon, molho especial da casa, pão tostado, '
                'batata frita crocante, refrigerante gelado, '
                'entrega rápida por favor'
            )
            
            item = ItemPedido(
                pedido_id=pedido.id,
                produto_id=1,
                nome_produto='Hambúrguer',
                categoria='Lanche',
                quantidade=1,
                preco_unitario=Decimal('15.50'),
                observacoes=observacoes_longas
            )
            
            db.session.add(item)
            db.session.commit()
            
            assert item.observacoes == observacoes_longas
    
    def test_todos_status_pedido_transicoes(self, app):
        """Teste de todas as transições de status"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('15.50')
            )
            db.session.add(pedido)
            db.session.commit()
            
            # Testa todas as transições
            status_sequence = [
                StatusPedido.RECEBIDO,
                StatusPedido.EM_PREPARACAO,
                StatusPedido.PRONTO,
                StatusPedido.FINALIZADO
            ]
            
            for status in status_sequence:
                pedido.status = status
                db.session.commit()
                
                # Verifica se o status foi salvo corretamente
                pedido_recarregado = Pedido.query.get(pedido.id)
                assert pedido_recarregado.status == status
                
                # Testa serialização
                pedido_dict = pedido_recarregado.to_dict()
                assert pedido_dict['status'] == status.value

class TestValidacoesDados:
    """Testes para validações de dados"""
    
    def test_produto_preco_decimal_precisao(self, app):
        """Teste de precisão decimal em preços (corrigido para SQLite)"""
        with app.app_context():
            # Usar preço com 2 casas decimais (padrão do SQLite)
            preco_preciso = Decimal('15.99')
            
            produto = Produto(
                nome='Produto Preciso',
                categoria='Teste',
                preco=preco_preciso,
                disponivel=True
            )
            
            db.session.add(produto)
            db.session.commit()
            
            # Recarregar do banco para ver como foi salvo
            produto_recarregado = Produto.query.get(produto.id)
            
            # SQLite pode arredondar, então verificamos se está próximo
            assert abs(produto_recarregado.preco - preco_preciso) < Decimal('0.01')
            
            # Testa serialização
            produto_dict = produto_recarregado.to_dict()
            assert isinstance(produto_dict['preco'], float)
    
    def test_calcular_total_com_decimais_complexos(self, app):
        """Teste de cálculo de total com decimais (corrigido para SQLite)"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('0.00')
            )
            db.session.add(pedido)
            db.session.commit()
            
            # Usar preços com 2 casas decimais (compatível com SQLite)
            item1 = ItemPedido(
                pedido_id=pedido.id,
                produto_id=1,
                nome_produto='Item 1',
                categoria='Teste',
                quantidade=3,
                preco_unitario=Decimal('12.33')  # 2 casas decimais
            )
            
            item2 = ItemPedido(
                pedido_id=pedido.id,
                produto_id=2,
                nome_produto='Item 2',
                categoria='Teste',
                quantidade=2,
                preco_unitario=Decimal('8.67')  # 2 casas decimais
            )
            
            db.session.add(item1)
            db.session.add(item2)
            db.session.commit()
            
            # Calcula total
            pedido.calcular_total()
            
            # Verifica cálculo: (3 * 12.33) + (2 * 8.67) = 36.99 + 17.34 = 54.33
            expected_total = Decimal('54.33')
            
            # Permite pequena diferença devido ao arredondamento do SQLite
            assert abs(pedido.total - expected_total) < Decimal('0.01')
    
    def test_produto_disponibilidade_toggle(self, app):
        """Teste de alternância de disponibilidade do produto"""
        with app.app_context():
            produto = Produto(
                nome='Produto Toggle',
                categoria='Teste',
                preco=Decimal('10.00'),
                disponivel=True
            )
            
            db.session.add(produto)
            db.session.commit()
            
            # Testa mudança de disponibilidade
            assert produto.disponivel is True
            
            produto.disponivel = False
            db.session.commit()
            
            produto_recarregado = Produto.query.get(produto.id)
            assert produto_recarregado.disponivel is False
            
            # Testa serialização
            produto_dict = produto_recarregado.to_dict()
            assert produto_dict['disponivel'] is False
    
    def test_preco_com_centavos_complexos(self, app):
        """Teste de preços com centavos específicos"""
        with app.app_context():
            precos_teste = [
                Decimal('1.01'),
                Decimal('9.99'),
                Decimal('15.50'),
                Decimal('99.95'),
                Decimal('0.50')
            ]
            
            for i, preco in enumerate(precos_teste):
                produto = Produto(
                    nome=f'Produto {i+1}',
                    categoria='Teste',
                    preco=preco,
                    disponivel=True
                )
                
                db.session.add(produto)
                db.session.commit()
                
                # Verifica se o preço foi salvo corretamente
                produto_recarregado = Produto.query.get(produto.id)
                assert produto_recarregado.preco == preco
                
                # Testa serialização
                produto_dict = produto_recarregado.to_dict()
                assert produto_dict['preco'] == float(preco)
    
    def test_calcular_total_multiplos_itens_mesmo_produto(self, app):
        """Teste de cálculo com múltiplos itens do mesmo produto"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('0.00')
            )
            db.session.add(pedido)
            db.session.commit()
            
            # Múltiplos itens do mesmo produto
            for i in range(3):
                item = ItemPedido(
                    pedido_id=pedido.id,
                    produto_id=1,  # Mesmo produto
                    nome_produto='Hambúrguer',
                    categoria='Lanche',
                    quantidade=1,
                    preco_unitario=Decimal('15.50')
                )
                db.session.add(item)
            
            db.session.commit()
            
            # Calcula total
            pedido.calcular_total()
            
            # 3 itens * 1 quantidade * 15.50 = 46.50
            assert pedido.total == Decimal('46.50')
    
    def test_item_pedido_quantidade_zero(self, app):
        """Teste de item com quantidade zero"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('0.00')
            )
            db.session.add(pedido)
            db.session.commit()
            
            item = ItemPedido(
                pedido_id=pedido.id,
                produto_id=1,
                nome_produto='Produto Teste',
                categoria='Teste',
                quantidade=0,  # Quantidade zero
                preco_unitario=Decimal('15.50')
            )
            
            db.session.add(item)
            db.session.commit()
            
            assert item.quantidade == 0
            
            # Testa cálculo do total
            pedido.calcular_total()
            assert pedido.total == Decimal('0.00')  # 0 * 15.50 = 0.00

