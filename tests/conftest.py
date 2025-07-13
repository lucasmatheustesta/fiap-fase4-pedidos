# conftest.py - Configuração de testes Flask (VERSÃO CORRIGIDA)
# Coloque este arquivo na raiz do seu projeto Flask

import pytest
import os
import sys
import tempfile
from pathlib import Path

# Adicionar diretório atual ao PYTHONPATH
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Configurar variáveis de ambiente para testes ANTES de importar a aplicação
os.environ['TESTING'] = 'true'
os.environ['FLASK_ENV'] = 'testing'
os.environ['WTF_CSRF_ENABLED'] = 'false'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

# Função para detectar e importar a aplicação Flask
def get_flask_app():
    """
    Detecta automaticamente a aplicação Flask no projeto
    """
    app = None
    db = None
    
    # Lista de possíveis nomes de módulos/arquivos principais
    possible_modules = [
        'app',           # app.py
        'main',          # main.py
        'run',           # run.py
        'server',        # server.py
        'application',   # application.py
        'wsgi',          # wsgi.py
        '__init__',      # __init__.py (se for um pacote)
    ]
    
    # Lista de possíveis nomes de variáveis da aplicação
    possible_app_names = ['app', 'application', 'flask_app', 'create_app']
    
    # Lista de possíveis nomes de variáveis do banco
    possible_db_names = ['db', 'database', 'sqlalchemy']
    
    for module_name in possible_modules:
        try:
            print(f"Tentando importar módulo: {module_name}")
            module = __import__(module_name)
            
            # Procurar pela aplicação Flask
            for app_name in possible_app_names:
                if hasattr(module, app_name):
                    potential_app = getattr(module, app_name)
                    
                    # Se for uma função (factory pattern)
                    if callable(potential_app):
                        try:
                            app = potential_app()
                            print(f"✅ Aplicação Flask encontrada: {module_name}.{app_name}() (factory)")
                            break
                        except Exception as e:
                            print(f"⚠️ Erro ao chamar factory {app_name}: {e}")
                            continue
                    
                    # Se for uma instância direta
                    elif hasattr(potential_app, 'config'):
                        app = potential_app
                        print(f"✅ Aplicação Flask encontrada: {module_name}.{app_name}")
                        break
            
            # Se encontrou a aplicação, procurar pelo banco
            if app:
                for db_name in possible_db_names:
                    if hasattr(module, db_name):
                        db = getattr(module, db_name)
                        print(f"✅ Banco de dados encontrado: {module_name}.{db_name}")
                        break
                break
                
        except ImportError as e:
            print(f"⚠️ Não foi possível importar {module_name}: {e}")
            continue
        except Exception as e:
            print(f"⚠️ Erro inesperado ao importar {module_name}: {e}")
            continue
    
    return app, db

# Tentar importar a aplicação
try:
    flask_app, flask_db = get_flask_app()
    
    if flask_app is None:
        print("❌ Não foi possível encontrar aplicação Flask automaticamente")
        print("📝 Criando aplicação Flask mínima para testes...")
        
        # Criar aplicação Flask mínima se não encontrar
        from flask import Flask
        try:
            from flask_sqlalchemy import SQLAlchemy
            flask_app = Flask(__name__)
            flask_app.config.update({
                'TESTING': True,
                'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
                'WTF_CSRF_ENABLED': False,
                'SECRET_KEY': 'test-secret-key',
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            })
            flask_db = SQLAlchemy(flask_app)
            print("✅ Aplicação Flask mínima criada para testes")
        except ImportError:
            flask_app = Flask(__name__)
            flask_app.config.update({
                'TESTING': True,
                'SECRET_KEY': 'test-secret-key',
            })
            flask_db = None
            print("✅ Aplicação Flask básica criada (sem SQLAlchemy)")
    
except Exception as e:
    print(f"❌ Erro crítico ao configurar aplicação Flask: {e}")
    # Criar aplicação Flask de emergência
    from flask import Flask
    flask_app = Flask(__name__)
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'emergency-test-key'
    flask_db = None

@pytest.fixture(scope='session')
def app():
    """
    Fixture para aplicação Flask de teste
    """
    if flask_app is None:
        pytest.skip("Aplicação Flask não encontrada")
    
    # Configurar para testes
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
    })
    
    # Configurar banco se disponível
    if flask_db is not None:
        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        })
    
    # Criar contexto da aplicação
    with flask_app.app_context():
        # Criar tabelas se banco disponível
        if flask_db is not None:
            try:
                flask_db.create_all()
                print("✅ Tabelas do banco criadas para testes")
            except Exception as e:
                print(f"⚠️ Erro ao criar tabelas: {e}")
        
        yield flask_app
        
        # Cleanup
        if flask_db is not None:
            try:
                flask_db.drop_all()
            except Exception as e:
                print(f"⚠️ Erro ao limpar banco: {e}")

@pytest.fixture(scope='function')
def client(app):
    """
    Fixture para cliente de teste Flask
    """
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """
    Fixture para CLI runner do Flask
    """
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def db_session(app):
    """
    Fixture para sessão de banco de dados (se disponível)
    """
    if flask_db is None:
        pytest.skip("SQLAlchemy não disponível")
    
    with app.app_context():
        # Iniciar transação
        connection = flask_db.engine.connect()
        transaction = connection.begin()
        
        # Configurar sessão para usar a transação
        flask_db.session.configure(bind=connection)
        
        yield flask_db.session
        
        # Rollback da transação após o teste
        transaction.rollback()
        connection.close()
        flask_db.session.remove()

@pytest.fixture(scope='function')
def db(app):
    """
    Fixture para objeto SQLAlchemy (se disponível)
    """
    if flask_db is None:
        pytest.skip("SQLAlchemy não disponível")
    
    return flask_db

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
def auth_headers():
    """
    Fixture para headers de autenticação
    """
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

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
    
    print("\n🧪 Configuração de testes Flask iniciada")
    print(f"📁 Diretório de trabalho: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")

def pytest_unconfigure(config):
    """
    Limpeza executada após todos os testes
    """
    print("\n✅ Testes Flask finalizados")

# Função utilitária para debug
def debug_project_structure():
    """
    Função para debugar a estrutura do projeto
    """
    print("\n🔍 Estrutura do projeto:")
    current_dir = Path('.')
    for file in current_dir.glob('*.py'):
        print(f"  📄 {file.name}")
    
    print("\n📦 Módulos Python encontrados:")
    for file in current_dir.glob('*.py'):
        if file.name != 'conftest.py':
            print(f"  🐍 {file.stem}")

# Executar debug se executado diretamente
if __name__ == '__main__':
    debug_project_structure()
    print(f"\n🔧 Aplicação Flask: {flask_app}")
    print(f"🗄️ SQLAlchemy: {flask_db}")

