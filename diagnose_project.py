#!/usr/bin/env python3
"""
Script de diagnóstico para projetos Flask
Ajuda a identificar a estrutura do projeto e configurar testes
"""

import os
import sys
import importlib
from pathlib import Path

def print_header(title):
    """Imprimir cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Imprimir seção formatada"""
    print(f"\n📋 {title}")
    print("-" * 40)

def check_project_structure():
    """Verificar estrutura do projeto"""
    print_section("Estrutura do Projeto")
    
    current_dir = Path('.')
    
    # Arquivos Python
    python_files = list(current_dir.glob('*.py'))
    print(f"📄 Arquivos Python encontrados ({len(python_files)}):")
    for file in sorted(python_files):
        size = file.stat().st_size
        print(f"  • {file.name} ({size} bytes)")
    
    # Diretórios importantes
    important_dirs = ['tests', 'test', 'static', 'templates', 'migrations', 'instance']
    print(f"\n📁 Diretórios importantes:")
    for dir_name in important_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            files_count = len(list(dir_path.glob('*')))
            print(f"  ✅ {dir_name}/ ({files_count} arquivos)")
        else:
            print(f"  ❌ {dir_name}/ (não encontrado)")
    
    # Arquivos de configuração
    config_files = ['requirements.txt', 'requirements-dev.txt', 'pytest.ini', 'conftest.py', '.env', 'config.py']
    print(f"\n⚙️ Arquivos de configuração:")
    for file_name in config_files:
        file_path = current_dir / file_name
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name}")

def check_python_modules():
    """Verificar módulos Python disponíveis"""
    print_section("Módulos Python Disponíveis")
    
    # Módulos essenciais
    essential_modules = [
        ('flask', 'Flask framework'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('pytest', 'Framework de testes'),
        ('pytest_cov', 'Cobertura de código'),
    ]
    
    # Módulos opcionais
    optional_modules = [
        ('flask_migrate', 'Flask-Migrate'),
        ('flask_wtf', 'Flask-WTF'),
        ('flask_login', 'Flask-Login'),
        ('requests', 'HTTP requests'),
        ('sqlalchemy', 'SQLAlchemy'),
    ]
    
    print("🔧 Módulos essenciais:")
    for module_name, description in essential_modules:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'versão desconhecida')
            print(f"  ✅ {module_name} ({version}) - {description}")
        except ImportError:
            print(f"  ❌ {module_name} - {description} (NÃO INSTALADO)")
    
    print("\n🔧 Módulos opcionais:")
    for module_name, description in optional_modules:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'versão desconhecida')
            print(f"  ✅ {module_name} ({version}) - {description}")
        except ImportError:
            print(f"  ⚠️ {module_name} - {description} (não instalado)")

def find_flask_app():
    """Encontrar aplicação Flask no projeto"""
    print_section("Procurando Aplicação Flask")
    
    # Arquivos possíveis
    possible_files = ['app.py', 'main.py', 'run.py', 'server.py', 'application.py', '__init__.py']
    
    # Nomes possíveis de variáveis
    possible_app_names = ['app', 'application', 'flask_app', 'create_app']
    
    found_apps = []
    
    for filename in possible_files:
        file_path = Path(filename)
        if not file_path.exists():
            continue
            
        print(f"\n🔍 Analisando {filename}:")
        
        try:
            # Ler conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar imports do Flask
            if 'from flask import' in content or 'import flask' in content:
                print(f"  ✅ Imports do Flask encontrados")
                
                # Tentar importar o módulo
                module_name = file_path.stem
                if module_name == '__init__':
                    module_name = file_path.parent.name
                
                try:
                    # Adicionar diretório atual ao path
                    sys.path.insert(0, str(Path.cwd()))
                    
                    module = importlib.import_module(module_name)
                    
                    # Procurar aplicação Flask
                    for app_name in possible_app_names:
                        if hasattr(module, app_name):
                            attr = getattr(module, app_name)
                            
                            # Verificar se é aplicação Flask
                            if hasattr(attr, 'config') and hasattr(attr, 'route'):
                                print(f"  ✅ Aplicação Flask: {module_name}.{app_name}")
                                found_apps.append((module_name, app_name, 'instance'))
                            
                            # Verificar se é factory
                            elif callable(attr):
                                try:
                                    test_app = attr()
                                    if hasattr(test_app, 'config') and hasattr(test_app, 'route'):
                                        print(f"  ✅ Factory Flask: {module_name}.{app_name}()")
                                        found_apps.append((module_name, app_name, 'factory'))
                                except:
                                    pass
                
                except Exception as e:
                    print(f"  ⚠️ Erro ao importar {module_name}: {e}")
            
            else:
                print(f"  ❌ Não contém imports do Flask")
                
        except Exception as e:
            print(f"  ❌ Erro ao ler arquivo: {e}")
    
    if found_apps:
        print(f"\n🎉 Aplicações Flask encontradas:")
        for module, app_name, app_type in found_apps:
            print(f"  • {module}.{app_name} ({app_type})")
    else:
        print(f"\n❌ Nenhuma aplicação Flask encontrada")
        print(f"💡 Verifique se você tem um arquivo com aplicação Flask configurada")

def check_database_config():
    """Verificar configuração de banco de dados"""
    print_section("Configuração de Banco de Dados")
    
    # Procurar por configurações de banco
    config_patterns = [
        'SQLALCHEMY_DATABASE_URI',
        'DATABASE_URL',
        'sqlite',
        'postgresql',
        'mysql',
        'flask_sqlalchemy',
        'SQLAlchemy'
    ]
    
    found_configs = []
    
    # Verificar arquivos Python
    for py_file in Path('.').glob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in config_patterns:
                if pattern in content:
                    found_configs.append((py_file.name, pattern))
        except:
            continue
    
    if found_configs:
        print("🗄️ Configurações de banco encontradas:")
        for filename, pattern in found_configs:
            print(f"  • {filename}: {pattern}")
    else:
        print("❌ Nenhuma configuração de banco encontrada")

def generate_recommendations():
    """Gerar recomendações baseadas no diagnóstico"""
    print_section("Recomendações")
    
    current_dir = Path('.')
    
    # Verificar se conftest.py existe
    if not (current_dir / 'conftest.py').exists():
        print("📝 1. Criar conftest.py:")
        print("   • Use o conftest_fixed.py fornecido")
        print("   • Renomeie para conftest.py")
    
    # Verificar se pytest.ini existe
    if not (current_dir / 'pytest.ini').exists():
        print("📝 2. Criar pytest.ini:")
        print("   • Configure parâmetros do pytest")
        print("   • Defina cobertura mínima")
    
    # Verificar se há testes
    test_files = list(current_dir.glob('test_*.py')) + list(current_dir.glob('*_test.py'))
    if len(test_files) == 0:
        print("📝 3. Criar testes:")
        print("   • Use test_basic_flask.py como exemplo")
        print("   • Crie pasta tests/ para organizar")
    
    # Verificar requirements
    if not (current_dir / 'requirements.txt').exists():
        print("📝 4. Criar requirements.txt:")
        print("   • Liste dependências do projeto")
        print("   • Inclua Flask e outras bibliotecas")
    
    print("\n💡 Para corrigir o erro de importação:")
    print("   1. Use conftest_fixed.py (detecta automaticamente a aplicação)")
    print("   2. Execute: python diagnose_project.py")
    print("   3. Verifique se sua aplicação Flask foi encontrada")
    print("   4. Execute: pytest test_basic_flask.py -v")

def main():
    """Função principal"""
    print_header("DIAGNÓSTICO DO PROJETO FLASK")
    
    print(f"📁 Diretório atual: {Path.cwd()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📦 Pytest disponível: {'✅' if 'pytest' in sys.modules or importlib.util.find_spec('pytest') else '❌'}")
    
    check_project_structure()
    check_python_modules()
    find_flask_app()
    check_database_config()
    generate_recommendations()
    
    print_header("DIAGNÓSTICO CONCLUÍDO")
    print("💡 Use as recomendações acima para configurar seu projeto")
    print("🚀 Após as correções, execute: pytest --cov=. --cov-report=term")

if __name__ == '__main__':
    main()

