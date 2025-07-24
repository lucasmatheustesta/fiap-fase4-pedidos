import factory
from decimal import Decimal
from datetime import datetime
from factory.alchemy import SQLAlchemyModelFactory
from factory import Faker, LazyAttribute, SubFactory

# Importar modelos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.pedido import db, Pedido, ItemPedido, Produto, StatusPedido

class ProdutoFactory(SQLAlchemyModelFactory):
    """Factory para criar produtos de teste"""
    
    class Meta:
        model = Produto
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    id = factory.Sequence(lambda n: n)
    nome = factory.Faker('word')
    categoria = factory.Iterator(['Lanche', 'Acompanhamento', 'Bebida', 'Sobremesa'])
    preco = factory.LazyAttribute(lambda obj: Decimal('15.50'))
    descricao = factory.Faker('sentence')
    disponivel = True

class PedidoFactory(SQLAlchemyModelFactory):
    """Factory para criar pedidos de teste"""
    
    class Meta:
        model = Pedido
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    id = factory.Sequence(lambda n: n)
    cliente_id = factory.Faker('numerify', text='###########')
    status = StatusPedido.RECEBIDO
    total = factory.LazyAttribute(lambda obj: Decimal('23.50'))
    data_criacao = factory.LazyFunction(datetime.utcnow)
    data_atualizacao = factory.LazyFunction(datetime.utcnow)

class ItemPedidoFactory(SQLAlchemyModelFactory):
    """Factory para criar itens de pedido de teste"""
    
    class Meta:
        model = ItemPedido
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    id = factory.Sequence(lambda n: n)
    pedido = factory.SubFactory(PedidoFactory)
    produto_id = 1
    nome_produto = 'Hambúrguer Teste'
    categoria = 'Lanche'
    quantidade = 1
    preco_unitario = factory.LazyAttribute(lambda obj: Decimal('15.50'))
    observacoes = factory.Faker('sentence')

