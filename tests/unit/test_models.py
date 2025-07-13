import pytest
from decimal import Decimal
from src.models.pedido import Pedido, ItemPedido, Produto, StatusPedido, db
from tests.fixtures.factories import PedidoFactory, ItemPedidoFactory, ProdutoFactory

class TestProduto:
    """Testes para o modelo Produto"""
    
    def test_criar_produto(self, app_context):
        """Teste de criação de produto"""
        produto = Produto(
            nome="Hambúrguer Clássico",
            categoria="Lanche",
            preco=Decimal('15.50'),
            descricao="Hambúrguer com carne, alface e tomate",
            disponivel=True
        )
        
        db.session.add(produto)
        db.session.commit()
        
        assert produto.id is not None
        assert produto.nome == "Hambúrguer Clássico"
        assert produto.categoria == "Lanche"
        assert produto.preco == Decimal('15.50')
        assert produto.disponivel is True
    
    def test_produto_to_dict(self, app_context):
        """Teste de serialização do produto"""
        produto = ProdutoFactory()
        produto_dict = produto.to_dict()
        
        assert 'id' in produto_dict
        assert 'nome' in produto_dict
        assert 'categoria' in produto_dict
        assert 'preco' in produto_dict
        assert 'disponivel' in produto_dict
        assert isinstance(produto_dict['preco'], float)

class TestPedido:
    """Testes para o modelo Pedido"""
    
    def test_criar_pedido(self, app_context):
        """Teste de criação de pedido"""
        pedido = Pedido(
            cliente_id="12345678901",
            total=Decimal('25.50')
        )
        
        db.session.add(pedido)
        db.session.commit()
        
        assert pedido.id is not None
        assert pedido.cliente_id == "12345678901"
        assert pedido.status == StatusPedido.RECEBIDO
        assert pedido.total == Decimal('25.50')
        assert pedido.data_criacao is not None
    
    def test_pedido_sem_cliente(self, app_context):
        """Teste de criação de pedido sem cliente (anônimo)"""
        pedido = Pedido(total=Decimal('10.00'))
        
        db.session.add(pedido)
        db.session.commit()
        
        assert pedido.cliente_id is None
        assert pedido.status == StatusPedido.RECEBIDO
    
    def test_calcular_total_pedido(self, app_context):
        """Teste de cálculo do total do pedido"""
        pedido = PedidoFactory()
        
        # Adicionar itens ao pedido
        item1 = ItemPedidoFactory(
            pedido=pedido,
            quantidade=2,
            preco_unitario=Decimal('10.00')
        )
        item2 = ItemPedidoFactory(
            pedido=pedido,
            quantidade=1,
            preco_unitario=Decimal('5.50')
        )
        
        total_calculado = pedido.calcular_total()
        
        assert total_calculado == Decimal('25.50')  # (2 * 10.00) + (1 * 5.50)
        assert pedido.total == Decimal('25.50')
    
    def test_pedido_to_dict(self, app_context):
        """Teste de serialização do pedido"""
        pedido = PedidoFactory()
        pedido_dict = pedido.to_dict()
        
        assert 'id' in pedido_dict
        assert 'cliente_id' in pedido_dict
        assert 'status' in pedido_dict
        assert 'total' in pedido_dict
        assert 'data_criacao' in pedido_dict
        assert 'itens' in pedido_dict
        assert isinstance(pedido_dict['total'], float)
        assert isinstance(pedido_dict['itens'], list)

class TestItemPedido:
    """Testes para o modelo ItemPedido"""
    
    def test_criar_item_pedido(self, app_context):
        """Teste de criação de item de pedido"""
        pedido = PedidoFactory()
        
        item = ItemPedido(
            pedido_id=pedido.id,
            produto_id=1,
            nome_produto="Hambúrguer",
            categoria="Lanche",
            quantidade=2,
            preco_unitario=Decimal('15.50'),
            observacoes="Sem cebola"
        )
        
        db.session.add(item)
        db.session.commit()
        
        assert item.id is not None
        assert item.pedido_id == pedido.id
        assert item.produto_id == 1
        assert item.nome_produto == "Hambúrguer"
        assert item.quantidade == 2
        assert item.preco_unitario == Decimal('15.50')
        assert item.observacoes == "Sem cebola"
    
    def test_item_pedido_to_dict(self, app_context):
        """Teste de serialização do item de pedido"""
        item = ItemPedidoFactory()
        item_dict = item.to_dict()
        
        assert 'id' in item_dict
        assert 'produto_id' in item_dict
        assert 'nome_produto' in item_dict
        assert 'categoria' in item_dict
        assert 'quantidade' in item_dict
        assert 'preco_unitario' in item_dict
        assert 'subtotal' in item_dict
        assert isinstance(item_dict['preco_unitario'], float)
        assert isinstance(item_dict['subtotal'], float)
        
        # Verificar cálculo do subtotal
        expected_subtotal = float(item.preco_unitario * item.quantidade)
        assert item_dict['subtotal'] == expected_subtotal

class TestStatusPedido:
    """Testes para o enum StatusPedido"""
    
    def test_status_values(self):
        """Teste dos valores do enum StatusPedido"""
        assert StatusPedido.RECEBIDO.value == "Recebido"
        assert StatusPedido.EM_PREPARACAO.value == "Em preparação"
        assert StatusPedido.PRONTO.value == "Pronto"
        assert StatusPedido.FINALIZADO.value == "Finalizado"
    
    def test_status_enum_creation(self):
        """Teste de criação do enum a partir de string"""
        status = StatusPedido("Recebido")
        assert status == StatusPedido.RECEBIDO
        
        with pytest.raises(ValueError):
            StatusPedido("Status Inválido")

