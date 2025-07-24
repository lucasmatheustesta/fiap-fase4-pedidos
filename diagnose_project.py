#!/usr/bin/env python3
"""
Script de diagnóstico completo para identificar e corrigir problemas nos testes Flask
"""

import os
import sys
import subprocess
import json

def verificar_estrutura_projeto():
    """
    Verifica a estrutura do projeto
    """
    print("🔍 VERIFICANDO ESTRUTURA DO PROJETO")
    print("=" * 50)
    
    arquivos_importantes = [
        'src/main.py',
        'src/models/pedido.py', 
        'src/routes/pedidos.py',
        'conftest.py',
        'requirements.txt',
        'pytest.ini'
    ]
    
    for arquivo in arquivos_importantes:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - FALTANDO")
    
    print()

def verificar_imports():
    """
    Verifica problemas de import nos arquivos de teste
    """
    print("🔍 VERIFICANDO IMPORTS NOS TESTES")
    print("=" * 50)
    
    import glob
    
    arquivos_teste = glob.glob('tests/**/*.py', recursive=True) + glob.glob('test_*.py')
    
    problemas = []
    
    for arquivo in arquivos_teste:
        if os.path.isfile(arquivo):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                if 'from app import' in conteudo:
                    problemas.append(f"{arquivo}: Usa 'from app import' em vez de 'from src.main import'")
                
                if 'import app' in conteudo and 'src.main' not in conteudo:
                    problemas.append(f"{arquivo}: Usa 'import app' em vez de 'import src.main'")
                    
            except Exception as e:
                problemas.append(f"{arquivo}: Erro ao ler arquivo - {e}")
    
    if problemas:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"  - {problema}")
    else:
        print("✅ Todos os imports estão corretos")
    
    print()
    return len(problemas) == 0

def verificar_configuracao_flask():
    """
    Verifica se a configuração Flask está correta
    """
    print("🔍 VERIFICANDO CONFIGURAÇÃO FLASK")
    print("=" * 50)
    
    try:
        # Configurar ambiente de teste
        os.environ['TESTING'] = 'true'
        os.environ['FLASK_ENV'] = 'testing'
        
        # Adicionar src ao path
        sys.path.insert(0, 'src')
        
        from src.main import app, db
        
        print("✅ Importação da aplicação Flask: OK")
        
        # Testar configuração
        with app.app_context():
            print("✅ Contexto da aplicação: OK")
            
            # Verificar se db está inicializado
            try:
                db.create_all()
                print("✅ Criação de tabelas: OK")
            except Exception as e:
                print(f"❌ Criação de tabelas: {e}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração Flask: {e}")
        return False

def verificar_rotas():
    """
    Verifica se as rotas estão registradas
    """
    print("🔍 VERIFICANDO ROTAS REGISTRADAS")
    print("=" * 50)
    
    try:
        os.environ['TESTING'] = 'true'
        sys.path.insert(0, 'src')
        
        from src.main import app
        
        with app.app_context():
            client = app.test_client()
            
            rotas_teste = [
                ('/api/health', 'Health check'),
                ('/api/info', 'Service info'),
                ('/api/pedidos', 'Pedidos endpoint'),
                ('/api/produtos', 'Produtos endpoint')
            ]
            
            rotas_ok = 0
            
            for rota, descricao in rotas_teste:
                try:
                    response = client.get(rota)
                    if response.status_code != 404:
                        print(f"✅ {rota} ({descricao}): {response.status_code}")
                        rotas_ok += 1
                    else:
                        print(f"❌ {rota} ({descricao}): 404 - Rota não encontrada")
                except Exception as e:
                    print(f"❌ {rota} ({descricao}): Erro - {e}")
            
            print(f"\n📊 Rotas funcionando: {rotas_ok}/{len(rotas_teste)}")
            return rotas_ok == len(rotas_teste)
            
    except Exception as e:
        print(f"❌ Erro ao verificar rotas: {e}")
        return False

def executar_teste_simples():
    """
    Executa um teste simples para verificar se está funcionando
    """
    print("🔍 EXECUTANDO TESTE SIMPLES")
    print("=" * 50)
    
    try:
        # Executar apenas um teste básico
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/unit/test_routes.py::TestHealthEndpoint::test_health_check',
            '-v', '--tb=short'
        ], capture_output=True, text=True, env={**os.environ, 'TESTING': 'true'})
        
        if result.returncode == 0:
            print("✅ Teste simples passou!")
            return True
        else:
            print("❌ Teste simples falhou:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False

def gerar_relatorio():
    """
    Gera relatório completo de diagnóstico
    """
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO DE DIAGNÓSTICO")
    print("=" * 60)
    
    verificacoes = [
        ("Estrutura do projeto", verificar_estrutura_projeto),
        ("Imports nos testes", verificar_imports),
        ("Configuração Flask", verificar_configuracao_flask),
        ("Rotas registradas", verificar_rotas),
        ("Teste simples", executar_teste_simples)
    ]
    
    resultados = {}
    
    for nome, funcao in verificacoes:
        print(f"\n🔍 {nome}...")
        try:
            resultado = funcao()
            resultados[nome] = resultado
            status = "✅ OK" if resultado else "❌ FALHOU"
            print(f"   {status}")
        except Exception as e:
            resultados[nome] = False
            print(f"   ❌ ERRO: {e}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    
    total = len(resultados)
    passou = sum(1 for r in resultados.values() if r)
    
    for nome, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        print(f"{status} {nome}")
    
    print(f"\n🎯 RESULTADO: {passou}/{total} verificações passaram")
    
    if passou == total:
        print("🎉 TUDO OK! Seu projeto está configurado corretamente.")
        print("\n💡 Execute os testes:")
        print("export TESTING=true")
        print("python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=70")
    else:
        print("⚠️  PROBLEMAS ENCONTRADOS! Siga as correções sugeridas:")
        print("\n🔧 SOLUÇÕES:")
        
        if not resultados.get("Imports nos testes", True):
            print("1. Execute o script corrigir_imports.py")
        
        if not resultados.get("Configuração Flask", True):
            print("2. Substitua conftest.py pelo conftest_final.py")
        
        if not resultados.get("Rotas registradas", True):
            print("3. Verifique se as rotas estão sendo registradas no main.py")

def main():
    """
    Função principal
    """
    print("🚀 DIAGNÓSTICO COMPLETO DO PROJETO FLASK")
    print("=" * 60)
    print("Este script vai identificar e sugerir correções para problemas nos testes.")
    print()
    
    gerar_relatorio()

if __name__ == '__main__':
    main()

