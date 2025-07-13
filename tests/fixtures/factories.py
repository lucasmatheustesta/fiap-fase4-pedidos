import factory
from decimal import Decimal
from src.models.pedido import Pedido, ItemPedido, Produto, StatusPedido, db

class ProdutoFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory para criar produtos de teste"""
    class Meta:
        model = Produto
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    id = factory.Sequence(lambda n: n)
    nome = factory.Faker('word')
    categoria = factory.Iterator(['Lanche', 'Acompanhamento', 'Bebida', 'Sobremesa'])
    preco = factory.LazyFunction(lambda: Decimal('10.50'))
    descricao = factory.Faker('text', max_nb_chars=100)
    disponivel = True

class PedidoFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory para criar pedidos de teste"""
    class Meta:
        model = Pedido
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    cliente_id = factory.Faker('numerify', text='###########')  # CPF fictício
    status = StatusPedido.RECEBIDO
    total = factory.LazyFunction(lambda: Decimal('25.50'))

class ItemPedidoFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory para criar itens de pedido de teste"""
    class Meta:
        model = ItemPedido
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    pedido = factory.SubFactory(PedidoFactory)
    produto_id = 1
    nome_produto = factory.Faker('word')
    categoria = factory.Iterator(['Lanche', 'Acompanhamento', 'Bebida', 'Sobremesa'])
    quantidade = 1
    preco_unitario = factory.LazyFunction(lambda: Decimal('15.50'))
    observacoes = factory.Faker('text', max_nb_chars=50)

