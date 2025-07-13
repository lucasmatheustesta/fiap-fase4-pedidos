import pytest
import json
from decimal import Decimal
from src.models.pedido import Pedido, ItemPedido, Produto, StatusPedido, db
from tests.fixtures.factories import PedidoFactory, ItemPedidoFactory, ProdutoFactory

class TestHealthEndpoint:
    """Testes para o endpoint de health check"""
    
    def test_health_check(self, client):
        """Teste do endpoint de health check"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'pedidos-service'
        assert 'timestamp' in data

class TestServiceInfo:
    """Testes para o endpoint de informações do serviço"""
    
    def test_service_info(self, client):
        """Teste do endpoint de informações do serviço"""
        response = client.get('/api/info')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['service'] == 'pedidos-service'
        assert data['version'] == '1.0.0'
        assert 'endpoints' in data

class TestPedidosEndpoints:
    """Testes para os endpoints de pedidos"""
    
    def test_listar_pedidos_vazio(self, client):
        """Teste de listagem de pedidos quando não há pedidos"""
        response = client.get('/api/pedidos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pedidos'] == []
        assert data['total'] == 0
    
    def test_criar_pedido_valido(self, client):
        """Teste de criação de pedido válido"""
        pedido_data = {
            'cliente_id': '12345678901',
            'itens': [
                {
                    'produto_id': 1,
                    'nome_produto': 'Hambúrguer',
                    'categoria': 'Lanche',
                    'quantidade': 2,
                    'preco_unitario': 15.50,
                    'observacoes': 'Sem cebola'
                },
                {
                    'produto_id': 2,
                    'nome_produto': 'Batata Frita',
                    'categoria': 'Acompanhamento',
                    'quantidade': 1,
                    'preco_unitario': 8.00
                }
            ]
        }
        
        response = client.post('/api/pedidos', 
                             data=json.dumps(pedido_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['cliente_id'] == '12345678901'
        assert data['status'] == 'Recebido'
        assert data['total'] == 39.0  # (2 * 15.50) + (1 * 8.00)
        assert len(data['itens']) == 2
    
    def test_criar_pedido_sem_itens(self, client):
        """Teste de criação de pedido sem itens (deve falhar)"""
        pedido_data = {
            'cliente_id': '12345678901',
            'itens': []
        }
        
        response = client.post('/api/pedidos',
                             data=json.dumps(pedido_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_criar_pedido_anonimo(self, client):
        """Teste de criação de pedido anônimo (sem cliente_id)"""
        pedido_data = {
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
        
        response = client.post('/api/pedidos',
                             data=json.dumps(pedido_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['cliente_id'] is None
        assert data['total'] == 15.5
    
    def test_obter_pedido_existente(self, client):
        """Teste de obtenção de pedido existente"""
        # Criar um pedido primeiro
        with client.application.app_context():
            pedido = PedidoFactory()
            ItemPedidoFactory(pedido=pedido)
            db.session.commit()
            pedido_id = pedido.id
        
        response = client.get(f'/api/pedidos/{pedido_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == pedido_id
    
    def test_obter_pedido_inexistente(self, client):
        """Teste de obtenção de pedido inexistente"""
        response = client.get('/api/pedidos/999')
        
        assert response.status_code == 404
    
    def test_atualizar_status_pedido(self, client):
        """Teste de atualização de status do pedido"""
        # Criar um pedido primeiro
        with client.application.app_context():
            pedido = PedidoFactory()
            db.session.commit()
            pedido_id = pedido.id
        
        status_data = {'status': 'Em preparação'}
        
        response = client.put(f'/api/pedidos/{pedido_id}/status',
                            data=json.dumps(status_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Em preparação'
    
    def test_atualizar_status_invalido(self, client):
        """Teste de atualização com status inválido"""
        with client.application.app_context():
            pedido = PedidoFactory()
            db.session.commit()
            pedido_id = pedido.id
        
        status_data = {'status': 'Status Inválido'}
        
        response = client.put(f'/api/pedidos/{pedido_id}/status',
                            data=json.dumps(status_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data

class TestProdutosEndpoints:
    """Testes para os endpoints de produtos"""
    
    def test_listar_produtos_vazio(self, client):
        """Teste de listagem de produtos quando não há produtos"""
        response = client.get('/api/produtos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['produtos'] == []
        assert data['total'] == 0
    
    def test_listar_produtos_com_dados(self, client):
        """Teste de listagem de produtos com dados"""
        with client.application.app_context():
            produto1 = ProdutoFactory(categoria='Lanche')
            produto2 = ProdutoFactory(categoria='Bebida')
            db.session.commit()
        
        response = client.get('/api/produtos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['produtos']) == 2
        assert data['total'] == 2
    
    def test_listar_produtos_por_categoria(self, client):
        """Teste de listagem de produtos filtrados por categoria"""
        with client.application.app_context():
            produto1 = ProdutoFactory(categoria='Lanche')
            produto2 = ProdutoFactory(categoria='Bebida')
            db.session.commit()
        
        response = client.get('/api/produtos?categoria=Lanche')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['produtos']) == 1
        assert data['produtos'][0]['categoria'] == 'Lanche'
    
    def test_listar_categorias(self, client):
        """Teste de listagem de categorias"""
        response = client.get('/api/produtos/categorias')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        expected_categories = ['Lanche', 'Acompanhamento', 'Bebida', 'Sobremesa']
        assert data['categorias'] == expected_categories

class TestFilaPedidos:
    """Testes para o endpoint de fila de pedidos"""
    
    def test_fila_pedidos_vazia(self, client):
        """Teste de fila de pedidos vazia"""
        response = client.get('/api/pedidos/fila')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['fila'] == []
        assert data['total'] == 0
    
    def test_fila_pedidos_com_dados(self, client):
        """Teste de fila de pedidos com dados"""
        with client.application.app_context():
            # Criar pedidos em diferentes status
            pedido1 = PedidoFactory(status=StatusPedido.RECEBIDO)
            pedido2 = PedidoFactory(status=StatusPedido.EM_PREPARACAO)
            pedido3 = PedidoFactory(status=StatusPedido.FINALIZADO)  # Não deve aparecer na fila
            db.session.commit()
        
        response = client.get('/api/pedidos/fila')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['fila']) == 2  # Apenas pedidos não finalizados
        assert data['total'] == 2



class TestPedidosClienteEndpoints:
    """Testes para endpoints de pedidos por cliente"""
    
    def test_listar_pedidos_cliente_vazio(self, client):
        """Teste de listagem de pedidos de cliente sem pedidos"""
        response = client.get('/api/pedidos/cliente/12345678901')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pedidos'] == []
        assert data['cliente_id'] == '12345678901'
        assert data['total'] == 0
    
    def test_listar_pedidos_cliente_com_dados(self, client):
        """Teste de listagem de pedidos de cliente com dados"""
        with client.application.app_context():
            pedido1 = PedidoFactory(cliente_id='12345678901')
            pedido2 = PedidoFactory(cliente_id='98765432100')  # Outro cliente
            db.session.commit()
        
        response = client.get('/api/pedidos/cliente/12345678901')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['pedidos']) == 1
        assert data['cliente_id'] == '12345678901'
        assert data['total'] == 1

class TestSincronizacaoProdutos:
    """Testes para sincronização de produtos"""
    
    def test_sincronizar_produtos_sucesso(self, client):
        """Teste de sincronização de produtos com sucesso"""
        produtos_data = {
            'produtos': [
                {
                    'id': 1,
                    'nome': 'Hambúrguer',
                    'categoria': 'Lanche',
                    'preco': 15.50,
                    'descricao': 'Hambúrguer clássico',
                    'disponivel': True
                },
                {
                    'id': 2,
                    'nome': 'Batata Frita',
                    'categoria': 'Acompanhamento',
                    'preco': 8.00,
                    'disponivel': True
                }
            ]
        }
        
        response = client.post('/api/produtos/sync',
                             data=json.dumps(produtos_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'mensagem' in data
    
    def test_sincronizar_produtos_sem_dados(self, client):
        """Teste de sincronização sem dados de produtos"""
        response = client.post('/api/produtos/sync',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data

class TestFiltrosPedidos:
    """Testes para filtros de pedidos"""
    
    def test_listar_pedidos_filtro_status(self, client):
        """Teste de listagem de pedidos com filtro de status"""
        with client.application.app_context():
            pedido1 = PedidoFactory(status=StatusPedido.RECEBIDO)
            pedido2 = PedidoFactory(status=StatusPedido.EM_PREPARACAO)
            db.session.commit()
        
        response = client.get('/api/pedidos?status=Recebido')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['pedidos']) == 1
        assert data['pedidos'][0]['status'] == 'Recebido'
    
    def test_listar_pedidos_filtro_status_invalido(self, client):
        """Teste de listagem com status inválido"""
        response = client.get('/api/pedidos?status=StatusInvalido')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_listar_pedidos_filtro_cliente(self, client):
        """Teste de listagem de pedidos com filtro de cliente"""
        with client.application.app_context():
            pedido1 = PedidoFactory(cliente_id='12345678901')
            pedido2 = PedidoFactory(cliente_id='98765432100')
            db.session.commit()
        
        response = client.get('/api/pedidos?cliente_id=12345678901')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['pedidos']) == 1
        assert data['pedidos'][0]['cliente_id'] == '12345678901'

class TestValidacoesPedidos:
    """Testes para validações de pedidos"""
    
    def test_criar_pedido_dados_incompletos(self, client):
        """Teste de criação de pedido com dados incompletos"""
        pedido_data = {
            'itens': [
                {
                    'produto_id': 1,
                    'nome_produto': 'Hambúrguer',
                    # Faltando categoria, quantidade e preco_unitario
                }
            ]
        }
        
        response = client.post('/api/pedidos',
                             data=json.dumps(pedido_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_atualizar_status_sem_dados(self, client):
        """Teste de atualização de status sem dados"""
        with client.application.app_context():
            pedido = PedidoFactory()
            db.session.commit()
            pedido_id = pedido.id
        
        response = client.put(f'/api/pedidos/{pedido_id}/status',
                            data=json.dumps({}),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data

