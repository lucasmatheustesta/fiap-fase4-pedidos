import pytest
import os
import sys
import tempfile

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.pedido import db

@pytest.fixture
def client():
    """Fixture para cliente de teste Flask"""
    # Criar banco de dados temporário para testes
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def app_context():
    """Fixture para contexto da aplicação"""
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

