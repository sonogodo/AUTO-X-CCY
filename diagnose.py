# diagnose.py
# SCRIPT DE DIAGNÓSTICO PARA IDENTIFICAR PROBLEMAS DO BOT

import os
import sys
import json
import traceback
from datetime import datetime

def check_file_permissions():
    """Verifica permissões de arquivos"""
    print("🔍 Verificando permissões de arquivos...")
    
    files_to_check = [
        'keys.py', 'bot.py', 'bot_improved.py', 
        'keyword_prompts.py', 'last_seen_ids.json'
    ]
    
    issues = []
    for filename in files_to_check:
        if os.path.exists(filename):
            if not os.access(filename, os.R_OK):
                issues.append(f"❌ {filename}: Sem permissão de leitura")
            elif filename.endswith('.py') and not os.access(filename, os.X_OK):
                issues.append(f"⚠️  {filename}: Sem permissão de execução")
            else:
                print(f"✅ {filename}: OK")
        else:
            issues.append(f"❌ {filename}: Arquivo não encontrado")
    
    return issues

def test_imports():
    """Testa importações críticas"""
    print("\n🔍 Testando importações...")
    
    imports_to_test = [
        ('tweepy', 'tweepy'),
        ('openai', 'openai'), 
        ('requests', 'requests'),
        ('json', 'json'),
        ('time', 'time'),
        ('datetime', 'datetime')
    ]
    
    issues = []
    for module_name, import_name in imports_to_test:
        try:
            __import__(import_name)
            print(f"✅ {module_name}: OK")
        except ImportError as e:
            issues.append(f"❌ {module_name}: {e}")
    
    return issues

def test_api_connections():
    """Testa conexões com APIs"""
    print("\n🔍 Testando conexões com APIs...")
    
    issues = []
    
    # Testa importação das chaves
    try:
        from keys import (X_BEARER_TOKEN, OPENAI_API_KEY, XAI_API_KEY,
                         X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
        print("✅ Chaves importadas com sucesso")
    except ImportError as e:
        issues.append(f"❌ Erro ao importar chaves: {e}")
        return issues
    
    # Testa Twitter/X
    try:
        import tweepy
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN)
        me = client.get_me()
        print(f"✅ Twitter/X: Conectado como @{me.data.username}")
    except Exception as e:
        issues.append(f"❌ Twitter/X: {e}")
    
    # Testa OpenAI
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        models = client.models.list()
        print("✅ OpenAI: Conexão OK")
    except Exception as e:
        issues.append(f"❌ OpenAI: {e}")
    
    # Testa xAI (Grok)
    try:
        import requests
        headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
        response = requests.get("https://api.x.ai/v1/models", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ xAI (Grok): Conexão OK")
        else:
            issues.append(f"⚠️  xAI: Status {response.status_code}")
    except Exception as e:
        issues.append(f"❌ xAI: {e}")
    
    return issues

def check_json_files():
    """Verifica integridade dos arquivos JSON"""
    print("\n🔍 Verificando arquivos JSON...")
    
    json_files = [
        'last_seen_ids.json',
        'bot_stats.json', 
        'processed_tweets.json'
    ]
    
    issues = []
    for filename in json_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    json.load(f)
                print(f"✅ {filename}: JSON válido")
            except json.JSONDecodeError as e:
                issues.append(f"❌ {filename}: JSON inválido - {e}")
            except Exception as e:
                issues.append(f"❌ {filename}: Erro ao ler - {e}")
        else:
            print(f"⚠️  {filename}: Não existe (será criado automaticamente)")
    
    return issues

def check_configuration():
    """Verifica configurações do bot"""
    print("\n🔍 Verificando configurações...")
    
    issues = []
    
    try:
        from keyword_prompts import TARGET_USER_IDS, prompts_com_aliases
        
        if not TARGET_USER_IDS:
            issues.append("❌ TARGET_USER_IDS está vazio")
        else:
            print(f"✅ {len(TARGET_USER_IDS)} usuários configurados")
        
        if not prompts_com_aliases:
            issues.append("❌ prompts_com_aliases está vazio")
        else:
            total_keywords = sum(len(keywords) for keywords in prompts_com_aliases.keys())
            print(f"✅ {len(prompts_com_aliases)} grupos de prompts, {total_keywords} palavras-chave")
            
    except ImportError as e:
        issues.append(f"❌ Erro ao importar configurações: {e}")
    
    return issues

def test_bot_functionality():
    """Testa funcionalidade básica do bot"""
    print("\n🔍 Testando funcionalidade do bot...")
    
    issues = []
    
    try:
        # Testa geração de comentário
        from bot_improved import SmartXBot
        
        print("✅ Bot melhorado pode ser importado")
        
        # Testa inicialização (sem executar)
        try:
            bot = SmartXBot()
            print("✅ Bot pode ser inicializado")
        except Exception as e:
            issues.append(f"❌ Erro na inicialização do bot: {e}")
            
    except ImportError as e:
        issues.append(f"❌ Erro ao importar bot melhorado: {e}")
        
        # Tenta bot original
        try:
            import bot
            print("✅ Bot original pode ser importado")
        except ImportError as e2:
            issues.append(f"❌ Erro ao importar bot original: {e2}")
    
    return issues

def generate_diagnostic_report():
    """Gera relatório completo de diagnóstico"""
    print("🔧 DIAGNÓSTICO COMPLETO DO BOT X.COM")
    print("=" * 50)
    
    all_issues = []
    
    # Executa todos os testes
    all_issues.extend(check_file_permissions())
    all_issues.extend(test_imports())
    all_issues.extend(test_api_connections())
    all_issues.extend(check_json_files())
    all_issues.extend(check_configuration())
    all_issues.extend(test_bot_functionality())
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📋 RESUMO DO DIAGNÓSTICO")
    print("=" * 50)
    
    if not all_issues:
        print("🎉 TUDO OK! O bot está pronto para funcionar.")
        print("\n💡 Para iniciar o bot, execute:")
        print("   python start_bot.py")
    else:
        print(f"⚠️  {len(all_issues)} problema(s) encontrado(s):")
        print()
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        
        print("\n🔧 SOLUÇÕES SUGERIDAS:")
        
        # Sugestões baseadas nos problemas
        if any("permissão" in issue.lower() for issue in all_issues):
            print("• Verifique permissões dos arquivos com: chmod +x *.py")
        
        if any("importar" in issue.lower() for issue in all_issues):
            print("• Instale dependências: pip install -r requirements.txt")
        
        if any("api" in issue.lower() or "conexão" in issue.lower() for issue in all_issues):
            print("• Verifique suas chaves de API no arquivo keys.py")
            print("• Teste conexão de internet")
        
        if any("json" in issue.lower() for issue in all_issues):
            print("• Delete arquivos JSON corrompidos (serão recriados)")
        
        print("\n📞 Se os problemas persistirem:")
        print("• Execute: python start_bot.py → opção 4 (Testar configurações)")
        print("• Verifique o arquivo bot.log para mais detalhes")
    
    # Salva relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"diagnostic_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Relatório de Diagnóstico - {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        
        if all_issues:
            f.write("PROBLEMAS ENCONTRADOS:\n")
            for i, issue in enumerate(all_issues, 1):
                f.write(f"{i}. {issue}\n")
        else:
            f.write("Nenhum problema encontrado. Bot OK!\n")
    
    print(f"\n📄 Relatório salvo em: {report_file}")

if __name__ == "__main__":
    try:
        generate_diagnostic_report()
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO no diagnóstico: {e}")
        print("\nStack trace completo:")
        traceback.print_exc()
        
        print(f"\n🆘 DIAGNÓSTICO DE EMERGÊNCIA:")
        print(f"• Python: {sys.version}")
        print(f"• Diretório atual: {os.getcwd()}")
        print(f"• Arquivos no diretório: {os.listdir('.')}")