import json
from decimal import Decimal
from pytest_bdd import scenarios, given, when, then, parsers
from src.models.pedido import Pedido, Produto, StatusPedido, db
from tests.fixtures.factories import PedidoFactory, ProdutoFactory

# Carregar cenários do arquivo .feature
scenarios('pedidos.feature')

# Contexto compartilhado entre steps
class Context:
    def __init__(self):
        self.cliente_id = None
        self.pedido_data = None
        self.response = None
        self.pedido_id = None
        self.produtos = []

# Instância global do contexto
test_context = Context()

@given('que o sistema está funcionando')
def sistema_funcionando(client):
    """Verifica se o sistema está funcionando"""
    response = client.get('/api/health')
    assert response.status_code == 200

@given('existem produtos disponíveis')
def produtos_disponiveis(client):
    """Cria produtos disponíveis para teste"""
    with client.application.app_context():
        produto1 = Produto(
            id=1,
            nome='Hambúrguer',
            categoria='Lanche',
            preco=Decimal('15.50'),
            disponivel=True
        )
        produto2 = Produto(
            id=2,
            nome='Batata Frita',
            categoria='Acompanhamento',
            preco=Decimal('8.00'),
            disponivel=True
        )
        db.session.add(produto1)
        db.session.add(produto2)
        db.session.commit()

@given(parsers.parse('que sou um cliente identificado com CPF "{cpf}"'))
def cliente_identificado(cpf):
    """Define um cliente identificado"""
    test_context.cliente_id = cpf

@given('que sou um cliente anônimo')
def cliente_anonimo():
    """Define um cliente anônimo"""
    test_context.cliente_id = None

@given(parsers.parse('que existe um pedido com status "{status}"'))
def pedido_existente(client, status):
    """Cria um pedido existente com status específico"""
    with client.application.app_context():
        pedido = PedidoFactory(status=StatusPedido(status))
        db.session.commit()
        test_context.pedido_id = pedido.id

@when('eu faço um pedido com os seguintes itens:')
def fazer_pedido_com_itens(client, datatable):
    """Faz um pedido com itens especificados"""
    itens = []
    # Pular o cabeçalho (primeira linha)
    for row in datatable[1:]:
        item = {
            'produto_id': int(row[0]),  # produto_id
            'nome_produto': row[1],     # nome_produto
            'categoria': row[2],        # categoria
            'quantidade': int(row[3]),  # quantidade
            'preco_unitario': float(row[4])  # preco_unitario
        }
        itens.append(item)
    
    pedido_data = {'itens': itens}
    if test_context.cliente_id:
        pedido_data['cliente_id'] = test_context.cliente_id
    
    test_context.response = client.post('/api/pedidos',
                                     data=json.dumps(pedido_data),
                                     content_type='application/json')

@when('eu tento fazer um pedido sem itens')
def fazer_pedido_sem_itens(client):
    """Tenta fazer um pedido sem itens"""
    pedido_data = {'itens': []}
    if test_context.cliente_id:
        pedido_data['cliente_id'] = test_context.cliente_id
    
    test_context.response = client.post('/api/pedidos',
                                     data=json.dumps(pedido_data),
                                     content_type='application/json')

@when(parsers.parse('o status do pedido é atualizado para "{novo_status}"'))
def atualizar_status_pedido(client, novo_status):
    """Atualiza o status do pedido"""
    status_data = {'status': novo_status}
    test_context.response = client.put(f'/api/pedidos/{test_context.pedido_id}/status',
                                    data=json.dumps(status_data),
                                    content_type='application/json')

@then('o pedido deve ser criado com sucesso')
def pedido_criado_sucesso():
    """Verifica se o pedido foi criado com sucesso"""
    assert test_context.response.status_code == 201

@then('o pedido não deve ser criado')
def pedido_nao_criado():
    """Verifica se o pedido não foi criado"""
    assert test_context.response.status_code == 400

@then(parsers.parse('o status do pedido deve ser "{status_esperado}"'))
def verificar_status_pedido(status_esperado):
    """Verifica o status do pedido"""
    data = json.loads(test_context.response.data)
    assert data['status'] == status_esperado

@then(parsers.parse('o total do pedido deve ser {total:g}'))
def verificar_total_pedido(total):
    """Verifica o total do pedido"""
    data = json.loads(test_context.response.data)
    assert data['total'] == total

@then('o cliente_id deve ser nulo')
def verificar_cliente_nulo():
    """Verifica se o cliente_id é nulo"""
    data = json.loads(test_context.response.data)
    assert data['cliente_id'] is None

@then('a data de atualização deve ser modificada')
def verificar_data_atualizacao():
    """Verifica se a data de atualização foi modificada"""
    data = json.loads(test_context.response.data)
    assert 'data_atualizacao' in data

@then(parsers.parse('deve retornar erro "{mensagem_erro}"'))
def verificar_mensagem_erro(mensagem_erro):
    """Verifica a mensagem de erro"""
    data = json.loads(test_context.response.data)
    assert mensagem_erro in data['erro']

