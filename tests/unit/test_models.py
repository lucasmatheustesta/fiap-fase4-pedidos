import pytest
from decimal import Decimal
from datetime import datetime
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.pedido import Pedido, ItemPedido, Produto, StatusPedido, db

class TestProduto:
    """Testes para o modelo Produto"""
    
    def test_criar_produto(self, app):
        """Teste de criação de produto"""
        with app.app_context():
            produto = Produto(
                nome='Hambúrguer Teste',
                categoria='Lanche',
                preco=Decimal('15.50'),
                descricao='Hambúrguer delicioso',
                disponivel=True
            )
            
            db.session.add(produto)
            db.session.commit()
            
            assert produto.id is not None
            assert produto.nome == 'Hambúrguer Teste'
            assert produto.categoria == 'Lanche'
            assert produto.preco == Decimal('15.50')
            assert produto.disponivel is True
    
    def test_produto_to_dict(self, app):
        """Teste de serialização do produto"""
        with app.app_context():
            produto = Produto(
                nome='Batata Frita',
                categoria='Acompanhamento',
                preco=Decimal('8.00'),
                disponivel=True
            )
            
            produto_dict = produto.to_dict()
            
            assert 'nome' in produto_dict
            assert 'categoria' in produto_dict
            assert 'preco' in produto_dict
            assert produto_dict['nome'] == 'Batata Frita'
            assert produto_dict['preco'] == 8.00

class TestPedido:
    """Testes para o modelo Pedido"""
    
    def test_criar_pedido(self, app):
        """Teste de criação de pedido"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('23.50')
            )
            
            db.session.add(pedido)
            db.session.commit()
            
            assert pedido.id is not None
            assert pedido.cliente_id == '12345678901'
            assert pedido.status == StatusPedido.RECEBIDO
            assert pedido.total == Decimal('23.50')
    
    def test_pedido_sem_cliente(self, app):
        """Teste de pedido anônimo"""
        with app.app_context():
            pedido = Pedido(
                cliente_id=None,
                status=StatusPedido.RECEBIDO,
                total=Decimal('15.50')
            )
            
            db.session.add(pedido)
            db.session.commit()
            
            assert pedido.cliente_id is None
            assert pedido.status == StatusPedido.RECEBIDO
    
    def test_calcular_total_pedido(self, app):
        """Teste de cálculo do total do pedido"""
        with app.app_context():
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('0.00')
            )
            
            db.session.add(pedido)
            db.session.commit()
            
            # Adicionar itens
            item1 = ItemPedido(
                pedido_id=pedido.id,
                produto_id=1,
                nome_produto='Hambúrguer',
                categoria='Lanche',
                quantidade=2,
                preco_unitario=Decimal('15.50')
            )
            
            item2 = ItemPedido(
                pedido_id=pedido.id,
                produto_id=2,
                nome_produto='Batata',
                categoria='Acompanhamento',
                quantidade=1,
                preco_unitario=Decimal('8.00')
            )
            
            db.session.add(item1)
            db.session.add(item2)
            db.session.commit()
            
            # Calcular total
            pedido.calcular_total()
            
            assert pedido.total == Decimal('39.00')  # (15.50 * 2) + (8.00 * 1)
    
    def test_pedido_to_dict(self, app):
        """Teste de serialização do pedido"""
        with app.app_context():
            # Criar pedido com data_criacao explícita
            now = datetime.utcnow()
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('23.50'),
                data_criacao=now,
                data_atualizacao=now
            )
            
            db.session.add(pedido)
            db.session.commit()
            
            pedido_dict = pedido.to_dict()
            
            assert 'id' in pedido_dict
            assert 'cliente_id' in pedido_dict
            assert 'status' in pedido_dict
            assert 'total' in pedido_dict
            assert 'data_criacao' in pedido_dict
            assert 'data_atualizacao' in pedido_dict
            assert pedido_dict['cliente_id'] == '12345678901'
            assert pedido_dict['status'] == 'Recebido'
            assert pedido_dict['total'] == 23.50

class TestItemPedido:
    """Testes para o modelo ItemPedido"""
    
    def test_criar_item_pedido(self, app):
        """Teste de criação de item de pedido"""
        with app.app_context():
            # Criar pedido primeiro
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('15.50')
            )
            db.session.add(pedido)
            db.session.commit()
            
            # Criar item
            item = ItemPedido(
                pedido_id=pedido.id,
                produto_id=1,
                nome_produto='Hambúrguer',
                categoria='Lanche',
                quantidade=1,
                preco_unitario=Decimal('15.50')
            )
            
            db.session.add(item)
            db.session.commit()
            
            assert item.id is not None
            assert item.pedido_id == pedido.id
            assert item.produto_id == 1
            assert item.quantidade == 1
            assert item.preco_unitario == Decimal('15.50')
    
    def test_item_pedido_to_dict(self, app):
        """Teste de serialização do item de pedido"""
        with app.app_context():
            # Criar pedido primeiro
            pedido = Pedido(
                cliente_id='12345678901',
                status=StatusPedido.RECEBIDO,
                total=Decimal('15.50')
            )
            db.session.add(pedido)
            db.session.commit()
            
            # Criar item
            item = ItemPedido(
                pedido_id=pedido.id,
                produto_id=1,
                nome_produto='Hambúrguer',
                categoria='Lanche',
                quantidade=1,
                preco_unitario=Decimal('15.50')
            )
            
            item_dict = item.to_dict()
            
            assert 'produto_id' in item_dict
            assert 'nome_produto' in item_dict
            assert 'quantidade' in item_dict
            assert 'preco_unitario' in item_dict
            assert item_dict['nome_produto'] == 'Hambúrguer'
            assert item_dict['quantidade'] == 1

class TestStatusPedido:
    """Testes para o enum StatusPedido"""
    
    def test_status_values(self):
        """Teste dos valores do enum"""
        assert StatusPedido.RECEBIDO.value == 'Recebido'
        assert StatusPedido.EM_PREPARACAO.value == 'Em preparação'
        assert StatusPedido.PRONTO.value == 'Pronto'
        assert StatusPedido.FINALIZADO.value == 'Finalizado'
    
    def test_status_enum_creation(self):
        """Teste de criação do enum"""
        status = StatusPedido('Recebido')
        assert status == StatusPedido.RECEBIDO
        
        status2 = StatusPedido('Em preparação')
        assert status2 == StatusPedido.EM_PREPARACAO

