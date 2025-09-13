# start_bot.py
# SCRIPT DE INICIALIZAÇÃO INTELIGENTE DO BOT

import os
import sys
import json
from datetime import datetime
import subprocess

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        'tweepy', 'openai', 'requests', 'pandas', 'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Pacotes faltando:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n💡 Instale com: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def check_api_keys():
    """Verifica se as chaves da API estão configuradas"""
    try:
        from keys import (
            X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, 
            X_ACCESS_TOKEN_SECRET, X_BEARER_TOKEN, 
            OPENAI_API_KEY, XAI_API_KEY
        )
        
        keys_to_check = {
            'X_API_KEY': X_API_KEY,
            'X_API_SECRET': X_API_SECRET, 
            'X_ACCESS_TOKEN': X_ACCESS_TOKEN,
            'X_ACCESS_TOKEN_SECRET': X_ACCESS_TOKEN_SECRET,
            'X_BEARER_TOKEN': X_BEARER_TOKEN,
            'OPENAI_API_KEY': OPENAI_API_KEY,
            'XAI_API_KEY': XAI_API_KEY
        }
        
        missing_keys = []
        for key_name, key_value in keys_to_check.items():
            if not key_value or key_value.strip() == "":
                missing_keys.append(key_name)
        
        if missing_keys:
            print("❌ Chaves de API faltando ou vazias:")
            for key in missing_keys:
                print(f"   • {key}")
            return False
        
        print("✅ Todas as chaves de API estão configuradas")
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar chaves: {e}")
        print("💡 Verifique se o arquivo keys.py existe e está correto")
        return False

def create_initial_files():
    """Cria arquivos iniciais necessários se não existirem"""
    files_to_create = {
        'last_seen_ids.json': {},
        'processed_tweets.json': [],
        'bot_stats.json': {
            "tweets_processed": 0,
            "responses_sent": 0,
            "tokens_used": 0,
            "last_reset": datetime.now().isoformat(),
            "daily_responses": {},
            "keyword_stats": {},
            "model_usage": {},
            "error_log": [],
            "performance_metrics": {
                "avg_response_time": 0,
                "success_rate": 0,
                "token_efficiency": 0
            }
        }
    }
    
    created_files = []
    for filename, default_content in files_to_create.items():
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump(default_content, f, indent=2)
            created_files.append(filename)
    
    if created_files:
        print(f"📁 Arquivos criados: {', '.join(created_files)}")
    else:
        print("✅ Todos os arquivos necessários já existem")

def show_menu():
    """Mostra menu de opções"""
    print("\n" + "="*50)
    print("🤖 BOT X.COM - MENU DE INICIALIZAÇÃO")
    print("="*50)
    print("1. 🚀 Iniciar bot melhorado (bot_improved.py)")
    print("2. 🔄 Iniciar bot original (bot.py)")
    print("3. 📊 Ver relatório de estatísticas")
    print("4. 🔧 Testar configurações")
    print("5. 🧹 Limpar dados antigos")
    print("6. ❌ Sair")
    print("="*50)

def test_configuration():
    """Testa a configuração do bot"""
    print("\n🔧 TESTANDO CONFIGURAÇÃO...")
    
    # Testa conexão com X/Twitter
    try:
        import tweepy
        from keys import X_BEARER_TOKEN
        
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN)
        me = client.get_me()
        print(f"✅ Conexão com X/Twitter OK - Usuário: @{me.data.username}")
        
    except Exception as e:
        print(f"❌ Erro na conexão com X/Twitter: {e}")
        return False
    
    # Testa conexão com OpenAI
    try:
        import openai
        from keys import OPENAI_API_KEY
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        # Teste simples
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Teste"}],
            max_tokens=5
        )
        print("✅ Conexão com OpenAI OK")
        
    except Exception as e:
        print(f"❌ Erro na conexão com OpenAI: {e}")
        return False
    
    # Testa conexão com xAI (Grok)
    try:
        import requests
        from keys import XAI_API_KEY
        
        headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
        response = requests.get("https://api.x.ai/v1/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Conexão com xAI (Grok) OK")
        else:
            print(f"⚠️  Conexão com xAI retornou status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na conexão com xAI: {e}")
    
    return True

def clean_old_data():
    """Limpa dados antigos"""
    print("\n🧹 LIMPANDO DADOS ANTIGOS...")
    
    files_to_clean = [
        'processed_tweets.json',
        'bot_stats.json'
    ]
    
    for filename in files_to_clean:
        if os.path.exists(filename):
            backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(filename, backup_name)
            print(f"📦 Backup criado: {backup_name}")
    
    # Recria arquivos limpos
    create_initial_files()
    print("✅ Dados antigos limpos e arquivos recriados")

def main():
    """Função principal"""
    print("🤖 Verificando sistema...")
    
    # Verificações iniciais
    if not check_dependencies():
        print("\n❌ Instale as dependências antes de continuar")
        return
    
    if not check_api_keys():
        print("\n❌ Configure as chaves de API antes de continuar")
        return
    
    # Cria arquivos necessários
    create_initial_files()
    
    # Menu principal
    while True:
        show_menu()
        choice = input("\n👉 Escolha uma opção (1-6): ").strip()
        
        if choice == '1':
            print("\n🚀 Iniciando bot melhorado...")
            try:
                from bot_improved import SmartXBot
                bot = SmartXBot()
                bot.run()
            except KeyboardInterrupt:
                print("\n👋 Bot encerrado pelo usuário")
            except Exception as e:
                print(f"\n❌ Erro ao executar bot: {e}")
        
        elif choice == '2':
            print("\n🔄 Iniciando bot original...")
            try:
                subprocess.run([sys.executable, "bot.py"])
            except KeyboardInterrupt:
                print("\n👋 Bot encerrado pelo usuário")
            except Exception as e:
                print(f"\n❌ Erro ao executar bot: {e}")
        
        elif choice == '3':
            print("\n📊 Gerando relatório...")
            try:
                from bot_monitor import BotMonitor
                monitor = BotMonitor()
                print(monitor.generate_report())
            except Exception as e:
                print(f"\n❌ Erro ao gerar relatório: {e}")
        
        elif choice == '4':
            test_configuration()
        
        elif choice == '5':
            confirm = input("\n⚠️  Tem certeza que quer limpar os dados? (s/n): ").lower()
            if confirm == 's':
                clean_old_data()
        
        elif choice == '6':
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n❌ Opção inválida")
        
        input("\n📱 Pressione Enter para continuar...")

if __name__ == "__main__":
    main()