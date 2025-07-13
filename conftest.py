# conftest.py - Configuração de testes para Flask
# Coloque este arquivo na raiz do seu projeto Flask

import pytest
import os
import tempfile
from app import app, db

# Configurar variáveis de ambiente para testes
os.environ['TESTING'] = 'true'
os.environ['FLASK_ENV'] = 'testing'
os.environ['WTF_CSRF_ENABLED'] = 'false'

@pytest.fixture(scope='session')
def test_app():
    """
    Fixture para criar aplicação Flask de teste
    """
    # Configuração de teste
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    
    # Criar contexto da aplicação
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        yield app
        # Cleanup após todos os testes
        db.drop_all()

@pytest.fixture(scope='function')
def client(test_app):
    """
    Fixture para cliente de teste Flask
    """
    return test_app.test_client()

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
        # Iniciar transação
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configurar sessão para usar a transação
        db.session.configure(bind=connection)
        
        yield db.session
        
        # Rollback da transação após o teste
        transaction.rollback()
        connection.close()
        db.session.remove()

@pytest.fixture(scope='function')
def auth_headers():
    """
    Fixture para headers de autenticação (se aplicável)
    """
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

@pytest.fixture(scope='function')
def sample_user(db_session):
    """
    Fixture para criar usuário de exemplo (ajuste conforme seus modelos)
    """
    try:
        # Assumindo que você tem um modelo User
        from app import User  # Ajuste conforme sua estrutura
        
        user = User(
            username='testuser',
            email='test@example.com',
            # Adicione outros campos conforme necessário
        )
        db_session.add(user)
        db_session.commit()
        return user
    except ImportError:
        # Se não tiver modelo User, retornar None
        return None

@pytest.fixture(scope='function')
def logged_in_user(client, sample_user):
    """
    Fixture para usuário logado (ajuste conforme seu sistema de auth)
    """
    if sample_user:
        # Simular login (ajuste conforme sua implementação)
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
    return sample_user

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

def pytest_unconfigure(config):
    """
    Limpeza executada após todos os testes
    """
    pass

# Marcadores personalizados
pytest_plugins = []

# Configuração para testes assíncronos (se usar)
@pytest.fixture
def event_loop():
    """
    Fixture para loop de eventos assíncronos
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

