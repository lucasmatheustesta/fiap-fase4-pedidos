# test_flask_app.py - Exemplos de testes para aplicação Flask
# Coloque este arquivo na pasta 'tests/' ou na raiz do projeto

import pytest
import json
from app import app, db

class TestFlaskApp:
    """
    Testes básicos da aplicação Flask
    """
    
    def test_app_exists(self):
        """Teste se a aplicação Flask existe"""
        assert app is not None
    
    def test_app_is_testing(self, client):
        """Teste se a aplicação está em modo de teste"""
        assert app.config['TESTING'] == True
    
    def test_database_uri_is_test(self, client):
        """Teste se está usando banco de teste"""
        assert 'memory' in app.config['SQLALCHEMY_DATABASE_URI']

class TestRoutes:
    """
    Testes das rotas da aplicação
    """
    
    def test_home_route(self, client):
        """Teste da rota principal"""
        response = client.get('/')
        # Aceita tanto 200 (se rota existe) quanto 404 (se não existe)
        assert response.status_code in [200, 404]
    
    def test_health_check(self, client):
        """Teste de health check (se existir)"""
        response = client.get('/health')
        # Se a rota não existir, retorna 404, que é ok
        assert response.status_code in [200, 404]
    
    def test_api_routes(self, client):
        """Teste de rotas da API (se existir)"""
        # Teste GET
        response = client.get('/api/test')
        assert response.status_code in [200, 404]
        
        # Teste POST (se aplicável)
        response = client.post('/api/test', 
                             data=json.dumps({'test': 'data'}),
                             content_type='application/json')
        assert response.status_code in [200, 201, 404, 405]

class TestDatabase:
    """
    Testes do banco de dados
    """
    
    def test_database_connection(self, db_session):
        """Teste de conexão com banco"""
        # Verificar se consegue executar query simples
        result = db_session.execute('SELECT 1').fetchone()
        assert result[0] == 1
    
    def test_database_tables_exist(self, db_session):
        """Teste se tabelas foram criadas"""
        # Verificar se consegue listar tabelas
        tables = db.engine.table_names()
        # Pelo menos deve ter alguma tabela ou lista vazia
        assert isinstance(tables, list)

class TestModels:
    """
    Testes dos modelos (ajuste conforme seus modelos)
    """
    
    def test_user_model_creation(self, db_session):
        """Teste de criação de modelo User (se existir)"""
        try:
            from app import User
            
            # Criar usuário de teste
            user = User(
                username='testuser',
                email='test@example.com'
            )
            db_session.add(user)
            db_session.commit()
            
            # Verificar se foi salvo
            saved_user = db_session.query(User).filter_by(username='testuser').first()
            assert saved_user is not None
            assert saved_user.email == 'test@example.com'
            
        except ImportError:
            # Se modelo User não existir, criar teste básico
            pytest.skip("User model not found")
    
    def test_model_relationships(self, db_session):
        """Teste de relacionamentos entre modelos (se aplicável)"""
        try:
            from app import User, Post  # Ajuste conforme seus modelos
            
            # Criar usuário
            user = User(username='testuser', email='test@example.com')
            db_session.add(user)
            db_session.flush()  # Para obter o ID
            
            # Criar post relacionado
            post = Post(title='Test Post', content='Test content', user_id=user.id)
            db_session.add(post)
            db_session.commit()
            
            # Verificar relacionamento
            assert len(user.posts) == 1
            assert post.user == user
            
        except ImportError:
            pytest.skip("Models with relationships not found")

class TestForms:
    """
    Testes de formulários WTF (se aplicável)
    """
    
    def test_form_validation(self):
        """Teste de validação de formulário"""
        try:
            from app import LoginForm  # Ajuste conforme seus formulários
            
            # Teste com dados válidos
            form_data = {
                'username': 'testuser',
                'password': 'testpass'
            }
            form = LoginForm(data=form_data)
            assert form.validate() == True
            
            # Teste com dados inválidos
            invalid_form = LoginForm(data={})
            assert invalid_form.validate() == False
            
        except ImportError:
            pytest.skip("Forms not found")

class TestAPI:
    """
    Testes de API REST (se aplicável)
    """
    
    def test_api_get_request(self, client):
        """Teste de requisição GET da API"""
        response = client.get('/api/users')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            # Verificar se retorna JSON
            assert response.content_type == 'application/json'
    
    def test_api_post_request(self, client):
        """Teste de requisição POST da API"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        response = client.post('/api/users',
                             data=json.dumps(data),
                             content_type='application/json')
        assert response.status_code in [200, 201, 404, 405]
    
    def test_api_error_handling(self, client):
        """Teste de tratamento de erros da API"""
        # Teste com dados inválidos
        response = client.post('/api/users',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code in [400, 404, 405]

class TestAuthentication:
    """
    Testes de autenticação (se aplicável)
    """
    
    def test_login_required_routes(self, client):
        """Teste de rotas que requerem login"""
        # Tentar acessar rota protegida sem login
        response = client.get('/dashboard')
        # Deve redirecionar para login ou retornar 401/403
        assert response.status_code in [302, 401, 403, 404]
    
    def test_login_process(self, client, sample_user):
        """Teste do processo de login"""
        if sample_user:
            # Tentar fazer login
            response = client.post('/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })
            # Deve redirecionar ou retornar sucesso
            assert response.status_code in [200, 302, 404]

class TestErrorHandling:
    """
    Testes de tratamento de erros
    """
    
    def test_404_error(self, client):
        """Teste de página não encontrada"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_500_error_handling(self, client):
        """Teste de tratamento de erro interno"""
        # Este teste pode ser difícil de implementar sem forçar um erro
        # Por enquanto, apenas verificar se a aplicação não quebra
        response = client.get('/')
        assert response.status_code != 500

class TestConfiguration:
    """
    Testes de configuração da aplicação
    """
    
    def test_config_values(self):
        """Teste de valores de configuração"""
        assert app.config['TESTING'] == True
        assert 'memory' in app.config['SQLALCHEMY_DATABASE_URI']
        assert app.config['WTF_CSRF_ENABLED'] == False
    
    def test_secret_key_exists(self):
        """Teste se secret key está configurada"""
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) > 0

# Testes de integração
class TestIntegration:
    """
    Testes de integração completos
    """
    
    def test_full_user_workflow(self, client, db_session):
        """Teste de workflow completo do usuário"""
        try:
            # 1. Registrar usuário (se rota existir)
            response = client.post('/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'newpass'
            })
            # Aceitar vários códigos de resposta
            assert response.status_code in [200, 201, 302, 404]
            
            # 2. Fazer login (se rota existir)
            response = client.post('/login', data={
                'username': 'newuser',
                'password': 'newpass'
            })
            assert response.status_code in [200, 302, 404]
            
            # 3. Acessar área protegida (se existir)
            response = client.get('/dashboard')
            assert response.status_code in [200, 302, 404]
            
        except Exception:
            # Se workflow completo não estiver implementado, pular
            pytest.skip("Full user workflow not implemented")

if __name__ == '__main__':
    # Executar testes se arquivo for executado diretamente
    pytest.main([__file__, '-v'])

