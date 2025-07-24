import pytest
import os
import sys
from flask import Flask

# Adicionar o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope='session')
def app():
    """Cria uma instância da aplicação Flask para testes"""
    # Importar após adicionar ao path
    from models.pedido import db
    from routes.pedidos import pedidos_bp
    
    app = Flask(__name__)
    
    # Configurações de teste
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Inicializar o banco de dados com a aplicação de teste
    db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(pedidos_bp, url_prefix='/api')
    
    # Criar contexto da aplicação
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        yield app

@pytest.fixture(scope='function')
def client(app):
    """Cliente de teste Flask"""
    return app.test_client()

@pytest.fixture(scope='function', autouse=True)
def setup_db(app):
    """Configura o banco de dados para cada teste"""
    from models.pedido import db
    
    with app.app_context():
        # Limpar todas as tabelas antes de cada teste
        db.drop_all()
        db.create_all()
        yield
        # Limpar após cada teste
        db.session.rollback()
        db.session.close()

