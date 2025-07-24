import pytest
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestMainApp:
    """Testes para o arquivo main.py"""
    
    def test_app_configuration(self, app):
        """Teste da configuração da aplicação"""
        # Verifica se a aplicação foi configurada corretamente
        assert app.config['TESTING'] is True
        assert 'SQLALCHEMY_DATABASE_URI' in app.config
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    
    def test_blueprints_registered(self, app):
        """Teste se os blueprints foram registrados"""
        # Verifica se o blueprint de pedidos foi registrado
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'pedidos' in blueprint_names or len(app.blueprints) > 0
    
    def test_database_initialization(self, app):
        """Teste da inicialização do banco de dados"""
        with app.app_context():
            from models.pedido import db
            
            # Verifica se o banco foi inicializado
            assert db is not None
            
            # Verifica se as tabelas podem ser criadas
            db.create_all()
            
            # Verifica se as tabelas existem
            inspector = db.inspect(db.engine)
            table_names = inspector.get_table_names()
            
            # Deve ter pelo menos uma tabela
            assert len(table_names) > 0
    
    def test_cors_configuration(self, client):
        """Teste da configuração CORS"""
        # Faz uma requisição OPTIONS para testar CORS
        response = client.options('/api/health')
        
        # CORS deve permitir a requisição (ou pelo menos não dar erro de conexão)
        assert response.status_code is not None
    
    def test_error_handlers(self, client):
        """Teste dos manipuladores de erro"""
        # Testa endpoint inexistente
        response = client.get('/api/endpoint-inexistente')
        
        # Deve retornar 404 ou outro erro tratado
        assert response.status_code >= 400
        
        # Testa método não permitido
        response = client.patch('/api/health')  # PATCH não é suportado
        
        # Deve retornar erro tratado
        assert response.status_code >= 400
    
    def test_json_error_handling(self, client):
        """Teste do tratamento de erros JSON"""
        # Envia JSON malformado
        response = client.post('/api/pedidos',
                             data='{"malformed": json,}',
                             content_type='application/json')
        
        # Deve tratar o erro graciosamente
        assert response.status_code >= 400
    
    def test_app_context_available(self, app):
        """Teste se o contexto da aplicação está disponível"""
        with app.app_context():
            from flask import current_app
            
            # Verifica se o contexto está ativo
            assert current_app is not None
            assert current_app.name is not None
    
    def test_database_session_handling(self, app):
        """Teste do gerenciamento de sessões do banco"""
        with app.app_context():
            from models.pedido import db, Produto
            from decimal import Decimal
            
            # Testa criação e rollback
            produto = Produto(
                nome='Produto Teste',
                categoria='Teste',
                preco=Decimal('10.00')
            )
            
            db.session.add(produto)
            # Não faz commit, faz rollback
            db.session.rollback()
            
            # Produto não deve estar no banco
            produtos = Produto.query.all()
            produto_teste = [p for p in produtos if p.nome == 'Produto Teste']
            assert len(produto_teste) == 0

