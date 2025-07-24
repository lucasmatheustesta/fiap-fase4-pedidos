# conftest.py - Configuração LIMPA de testes para Flask
# Remove o mock problemático de factories

import pytest
import os
import sys
import tempfile

# Configurar variáveis de ambiente ANTES de qualquer importação
os.environ['TESTING'] = 'true'
os.environ['FLASK_ENV'] = 'testing'
os.environ['WTF_CSRF_ENABLED'] = 'false'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar após configurar ambiente
from src.main import app, db

@pytest.fixture(scope='session')
def test_app():
    """
    Fixture para criar aplicação Flask de teste
    """
    # Forçar configuração de teste
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-12345',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
    })
    
    # Criar contexto da aplicação e configurar banco
    with app.app_context():
        # Garantir que o db está inicializado com a app
        db.init_app(app)
        
        # Criar todas as tabelas
        db.create_all()
        print("✅ Tabelas do banco criadas para testes")
        
        yield app
        
        # Cleanup após todos os testes
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def app_context(test_app):
    """
    Fixture para contexto da aplicação
    """
    with test_app.app_context():
        yield test_app

@pytest.fixture(scope='function')
def client(test_app):
    """
    Fixture para cliente de teste Flask
    """
    with test_app.test_client() as client:
        with test_app.app_context():
            yield client

@pytest.fixture(scope='function')
def runner(test_app):
    """
    Fixture para CLI runner do Flask
    """
    return test_app.test_cli_runner()

@pytest.fixture(scope='function')
def db_session(test_app):
    """
    Fixture para sessão de banco de dados
    Cria uma transação que é revertida após cada teste
    """
    with test_app.app_context():
        # Garantir que as tabelas existem
        db.create_all()
        
        # Iniciar transação
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configurar sessão para usar a transação
        db.session.configure(bind=connection, binds={})
        
        yield db.session
        
        # Rollback da transação após o teste
        db.session.remove()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope='function')
def auth_headers():
    """
    Fixture para headers de autenticação
    """
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Fixture que executa automaticamente antes de cada teste
    """
    # Configurar variáveis de ambiente para cada teste
    original_env = {}
    test_env = {
        'TESTING': 'true',
        'FLASK_ENV': 'testing',
        'WTF_CSRF_ENABLED': 'false',
        'DATABASE_URL': 'sqlite:///:memory:',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    }
    
    # Salvar valores originais e definir valores de teste
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restaurar valores originais
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

@pytest.fixture
def temp_file():
    """
    Fixture para arquivo temporário
    """
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass

@pytest.fixture
def temp_dir():
    """
    Fixture para diretório temporário
    """
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

# Hooks do pytest
def pytest_configure(config):
    """
    Configuração executada antes dos testes
    """
    # Configurar logging para testes
    import logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Garantir que o diretório database existe
    database_dir = os.path.join(os.path.dirname(__file__), 'src', 'database')
    if not os.path.exists(database_dir):
        os.makedirs(database_dir, exist_ok=True)

def pytest_unconfigure(config):
    """
    Limpeza executada após todos os testes
    """
    pass

# Fixtures específicas para o projeto
@pytest.fixture
def sample_pedido_data():
    """
    Fixture com dados de exemplo para pedidos
    """
    return {
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

@pytest.fixture
def sample_produto_data():
    """
    Fixture com dados de exemplo para produtos
    """
    return {
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

print("🧪 Configuração de testes Flask iniciada")
print(f"📁 Diretório de trabalho: {os.getcwd()}")
print(f"🐍 Python path: {sys.path[:3]}...")
print("✅ Testes Flask finalizados")

