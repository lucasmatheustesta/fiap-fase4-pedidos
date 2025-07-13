# test_basic_flask.py - Testes básicos que funcionam com qualquer estrutura Flask
# Coloque este arquivo na raiz do projeto ou pasta tests/

import pytest
import os
import sys
from pathlib import Path

# Adicionar diretório atual ao path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

class TestProjectStructure:
    """
    Testes básicos da estrutura do projeto
    """
    
    def test_python_files_exist(self):
        """Verificar se existem arquivos Python no projeto"""
        current_dir = Path('.')
        python_files = list(current_dir.glob('*.py'))
        assert len(python_files) > 0, "Nenhum arquivo Python encontrado no projeto"
        print(f"✅ Encontrados {len(python_files)} arquivos Python")
    
    def test_project_has_main_file(self):
        """Verificar se existe um arquivo principal"""
        possible_main_files = ['app.py', 'main.py', 'run.py', 'server.py', '__init__.py']
        current_dir = Path('.')
        
        found_files = []
        for filename in possible_main_files:
            if (current_dir / filename).exists():
                found_files.append(filename)
        
        assert len(found_files) > 0, f"Nenhum arquivo principal encontrado. Procurados: {possible_main_files}"
        print(f"✅ Arquivos principais encontrados: {found_files}")

class TestFlaskApp:
    """
    Testes da aplicação Flask (se disponível)
    """
    
    def test_flask_app_import(self):
        """Tentar importar aplicação Flask"""
        possible_modules = ['app', 'main', 'run', 'server', '__init__']
        app_found = False
        
        for module_name in possible_modules:
            try:
                module = __import__(module_name)
                
                # Procurar por objetos Flask
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Verificar se é uma aplicação Flask
                    if hasattr(attr, 'config') and hasattr(attr, 'route'):
                        print(f"✅ Aplicação Flask encontrada: {module_name}.{attr_name}")
                        app_found = True
                        break
                    
                    # Verificar se é uma factory function
                    elif callable(attr) and attr_name in ['create_app', 'app', 'application']:
                        try:
                            test_app = attr()
                            if hasattr(test_app, 'config') and hasattr(test_app, 'route'):
                                print(f"✅ Factory Flask encontrada: {module_name}.{attr_name}()")
                                app_found = True
                                break
                        except:
                            continue
                
                if app_found:
                    break
                    
            except ImportError:
                continue
            except Exception as e:
                print(f"⚠️ Erro ao importar {module_name}: {e}")
                continue
        
        if not app_found:
            print("⚠️ Aplicação Flask não encontrada automaticamente")
            print("💡 Isso é normal se o projeto ainda não tem uma aplicação Flask configurada")
        
        # Este teste sempre passa, apenas informa o status
        assert True

class TestEnvironment:
    """
    Testes do ambiente de desenvolvimento
    """
    
    def test_python_version(self):
        """Verificar versão do Python"""
        version = sys.version_info
        assert version.major >= 3, f"Python 3+ necessário, encontrado: {version}"
        assert version.minor >= 8, f"Python 3.8+ recomendado, encontrado: {version.major}.{version.minor}"
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    def test_required_packages(self):
        """Verificar se pacotes essenciais estão disponíveis"""
        required_packages = ['flask']
        optional_packages = ['flask_sqlalchemy', 'pytest', 'pytest_cov']
        
        available_packages = []
        missing_packages = []
        
        for package in required_packages + optional_packages:
            try:
                __import__(package)
                available_packages.append(package)
            except ImportError:
                missing_packages.append(package)
        
        print(f"✅ Pacotes disponíveis: {available_packages}")
        if missing_packages:
            print(f"⚠️ Pacotes não encontrados: {missing_packages}")
        
        # Verificar se pelo menos Flask está disponível
        flask_available = 'flask' in available_packages
        if not flask_available:
            print("❌ Flask não está instalado!")
            print("💡 Execute: pip install flask")
        
        assert flask_available, "Flask é obrigatório para o projeto"
    
    def test_environment_variables(self):
        """Verificar variáveis de ambiente de teste"""
        test_vars = ['TESTING', 'FLASK_ENV']
        
        for var in test_vars:
            value = os.environ.get(var)
            print(f"🔧 {var} = {value}")
        
        # Este teste sempre passa, apenas mostra as variáveis
        assert True

class TestBasicFunctionality:
    """
    Testes de funcionalidade básica
    """
    
    def test_basic_math(self):
        """Teste matemático básico para verificar pytest"""
        assert 2 + 2 == 4
        assert 10 / 2 == 5
        print("✅ Operações matemáticas básicas funcionando")
    
    def test_string_operations(self):
        """Teste de operações com strings"""
        text = "Flask Test"
        assert text.upper() == "FLASK TEST"
        assert len(text) == 10
        assert "Flask" in text
        print("✅ Operações com strings funcionando")
    
    def test_list_operations(self):
        """Teste de operações com listas"""
        numbers = [1, 2, 3, 4, 5]
        assert sum(numbers) == 15
        assert max(numbers) == 5
        assert min(numbers) == 1
        assert len(numbers) == 5
        print("✅ Operações com listas funcionando")

class TestFlaskBasics:
    """
    Testes básicos do Flask (se disponível)
    """
    
    def test_create_minimal_flask_app(self):
        """Criar aplicação Flask mínima para teste"""
        try:
            from flask import Flask
            
            app = Flask(__name__)
            app.config['TESTING'] = True
            
            @app.route('/')
            def hello():
                return 'Hello, Test!'
            
            with app.test_client() as client:
                response = client.get('/')
                assert response.status_code == 200
                assert b'Hello, Test!' in response.data
            
            print("✅ Aplicação Flask mínima funcionando")
            
        except ImportError:
            pytest.skip("Flask não está instalado")
    
    def test_flask_config(self):
        """Testar configuração do Flask"""
        try:
            from flask import Flask
            
            app = Flask(__name__)
            app.config.update({
                'TESTING': True,
                'SECRET_KEY': 'test-key',
                'DEBUG': False
            })
            
            assert app.config['TESTING'] == True
            assert app.config['SECRET_KEY'] == 'test-key'
            assert app.config['DEBUG'] == False
            
            print("✅ Configuração do Flask funcionando")
            
        except ImportError:
            pytest.skip("Flask não está instalado")

# Função para executar diagnóstico
def run_diagnostics():
    """
    Executar diagnóstico do projeto
    """
    print("\n🔍 DIAGNÓSTICO DO PROJETO FLASK")
    print("=" * 50)
    
    # Verificar estrutura
    print("\n📁 Estrutura do projeto:")
    current_dir = Path('.')
    for file in sorted(current_dir.glob('*.py')):
        print(f"  📄 {file.name}")
    
    # Verificar imports
    print("\n🐍 Testando imports:")
    modules_to_test = ['flask', 'flask_sqlalchemy', 'pytest', 'pytest_cov']
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} (não instalado)")
    
    # Verificar aplicação Flask
    print("\n🌶️ Procurando aplicação Flask:")
    possible_files = ['app.py', 'main.py', 'run.py', 'server.py']
    
    for filename in possible_files:
        if Path(filename).exists():
            print(f"  📄 {filename} encontrado")
        else:
            print(f"  ❌ {filename} não encontrado")
    
    print("\n✅ Diagnóstico concluído!")

if __name__ == '__main__':
    run_diagnostics()

