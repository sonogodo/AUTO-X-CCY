# start_mention_bot.py
# INICIALIZADOR DO BOT DE MENÇÕES COM INTERFACE AMIGÁVEL

import os
import sys
import json
from datetime import datetime
import subprocess

def check_dependencies():
    """Verifica dependências específicas do bot de menções"""
    required_packages = ['tweepy', 'openai', 'requests']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Pacotes faltando: {', '.join(missing)}")
        print(f"💡 Instale com: pip install {' '.join(missing)}")
        return False
    
    print("✅ Todas as dependências estão OK")
    return True

def check_api_keys():
    """Verifica chaves de API"""
    try:
        from keys import X_BEARER_TOKEN, OPENAI_API_KEY, XAI_API_KEY
        
        keys = {
            'X_BEARER_TOKEN': X_BEARER_TOKEN,
            'OPENAI_API_KEY': OPENAI_API_KEY, 
            'XAI_API_KEY': XAI_API_KEY
        }
        
        missing = [name for name, key in keys.items() if not key or key.strip() == ""]
        
        if missing:
            print(f"❌ Chaves faltando: {', '.join(missing)}")
            return False
        
        print("✅ Chaves de API configuradas")
        return True
        
    except ImportError:
        print("❌ Arquivo keys.py não encontrado")
        return False

def get_username():
    """Solicita e valida username"""
    print("\n🤖 CONFIGURAÇÃO DO BOT DE MENÇÕES")
    print("=" * 40)
    
    # Verifica se já existe configuração salva
    if os.path.exists("mention_bot_config.json"):
        try:
            with open("mention_bot_config.json", "r") as f:
                config = json.load(f)
                saved_username = config.get("username", "")
                
                if saved_username:
                    print(f"Username salvo: @{saved_username}")
                    use_saved = input("Usar este username? (s/n): ").lower().strip()
                    if use_saved == 's':
                        return saved_username
        except:
            pass
    
    # Solicita novo username
    while True:
        username = input("\nDigite seu username do X (sem @): ").strip()
        
        if not username:
            print("❌ Username é obrigatório!")
            continue
        
        # Remove @ se o usuário digitou
        username = username.replace('@', '')
        
        # Validação básica
        if len(username) < 1 or len(username) > 15:
            print("❌ Username deve ter entre 1 e 15 caracteres!")
            continue
        
        # Confirma
        print(f"\nUsername: @{username}")
        confirm = input("Confirma? (s/n): ").lower().strip()
        
        if confirm == 's':
            # Salva configuração
            config = {"username": username, "created_at": datetime.now().isoformat()}
            with open("mention_bot_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            return username

def test_twitter_connection(username):
    """Testa conexão com Twitter e verifica se o username existe"""
    try:
        import tweepy
        from keys import X_BEARER_TOKEN
        
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN)
        
        # Verifica se o username existe
        try:
            user = client.get_user(username=username)
            print(f"✅ Usuário encontrado: @{user.data.username} ({user.data.name})")
            return True
        except tweepy.NotFound:
            print(f"❌ Usuário @{username} não encontrado no X!")
            return False
        except tweepy.Unauthorized:
            print("❌ Erro de autorização - verifique suas chaves de API")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False

def show_usage_stats():
    """Mostra estatísticas de uso dos modelos"""
    try:
        with open("model_usage_stats.json", "r") as f:
            stats = json.load(f)
        
        total_uses = stats["chatgpt_uses"] + stats["xai_uses"]
        total_tokens = stats["chatgpt_tokens"] + stats["xai_tokens"]
        
        if total_uses == 0:
            print("📊 Nenhuma resposta gerada ainda")
            return
        
        print("\n📊 ESTATÍSTICAS DE USO")
        print("-" * 30)
        print(f"Total de respostas: {total_uses}")
        print(f"Total de tokens: {total_tokens:,}")
        print(f"\nChatGPT:")
        print(f"  • Usos: {stats['chatgpt_uses']} ({stats['chatgpt_uses']/total_uses*100:.1f}%)")
        print(f"  • Tokens: {stats['chatgpt_tokens']:,}")
        print(f"\nxAI (Grok):")
        print(f"  • Usos: {stats['xai_uses']} ({stats['xai_uses']/total_uses*100:.1f}%)")
        print(f"  • Tokens: {stats['xai_tokens']:,}")
        
        balance = abs(stats['chatgpt_uses'] - stats['xai_uses'])
        print(f"\nBalanceamento: {balance} diferença entre modelos")
        
        if balance <= 2:
            print("✅ Modelos bem balanceados!")
        elif balance <= 5:
            print("⚠️  Pequeno desbalanceamento")
        else:
            print("❌ Modelos desbalanceados - um está sendo usado muito mais")
            
    except FileNotFoundError:
        print("📊 Nenhuma estatística disponível ainda")
    except Exception as e:
        print(f"❌ Erro ao carregar estatísticas: {e}")

def show_recent_mentions():
    """Mostra menções recentes processadas"""
    try:
        with open("processed_mentions.json", "r") as f:
            mentions = json.load(f)
        
        if not mentions:
            print("📭 Nenhuma menção processada ainda")
            return
        
        print(f"\n📨 MENÇÕES PROCESSADAS: {len(mentions)}")
        print("(Últimas 5)")
        print("-" * 30)
        
        # Mostra apenas os últimos 5 IDs
        recent = mentions[-5:] if len(mentions) > 5 else mentions
        for mention_id in recent:
            print(f"• Tweet ID: {mention_id}")
            
    except FileNotFoundError:
        print("📭 Nenhuma menção processada ainda")
    except Exception as e:
        print(f"❌ Erro ao carregar menções: {e}")

def main_menu():
    """Menu principal"""
    while True:
        print("\n" + "="*50)
        print("🤖 BOT DE MENÇÕES X.COM")
        print("="*50)
        print("1. 🚀 Iniciar bot de menções")
        print("2. 🛠️  Personalizar prompt e diretrizes")
        print("3. 📊 Ver estatísticas de uso")
        print("4. 📨 Ver menções recentes")
        print("5. 🔧 Testar configurações")
        print("6. 🧹 Limpar dados")
        print("7. ❓ Ajuda")
        print("8. ❌ Sair")
        
        choice = input("\n👉 Escolha uma opção (1-8): ").strip()
        
        if choice == "1":
            # Verifica dependências
            if not check_dependencies() or not check_api_keys():
                print("\n❌ Resolva os problemas acima antes de continuar")
                continue
            
            # Obtém username
            username = get_username()
            
            # Testa conexão
            if not test_twitter_connection(username):
                print("\n❌ Não foi possível conectar. Verifique o username e as chaves de API")
                continue
            
            # Inicia o bot
            print(f"\n🚀 Iniciando bot para @{username}...")
            try:
                from mention_bot import MentionBot
                bot = MentionBot(username)
                bot.run()
            except KeyboardInterrupt:
                print("\n👋 Bot encerrado pelo usuário")
            except Exception as e:
                print(f"\n❌ Erro ao executar bot: {e}")
        
        elif choice == "2":
            print("\n🛠️  Abrindo customizador de prompt...")
            try:
                subprocess.run([sys.executable, "customize_prompt.py"])
            except Exception as e:
                print(f"❌ Erro ao abrir customizador: {e}")
        
        elif choice == "3":
            show_usage_stats()
        
        elif choice == "4":
            show_recent_mentions()
        
        elif choice == "5":
            print("\n🔧 Testando configurações...")
            if check_dependencies() and check_api_keys():
                username = input("Username para testar (sem @): ").strip()
                if username:
                    test_twitter_connection(username)
        
        elif choice == "6":
            print("\n🧹 LIMPEZA DE DADOS")
            print("⚠️  Isso irá apagar:")
            print("• Estatísticas de uso dos modelos")
            print("• Lista de menções processadas")
            print("• Último ID de menção")
            
            confirm = input("\nTem certeza? (digite 'CONFIRMO'): ").strip()
            if confirm == "CONFIRMO":
                files_to_clean = [
                    "model_usage_stats.json",
                    "processed_mentions.json", 
                    "last_mention_id.json"
                ]
                
                cleaned = 0
                for filename in files_to_clean:
                    if os.path.exists(filename):
                        os.remove(filename)
                        cleaned += 1
                        print(f"🗑️  Removido: {filename}")
                
                print(f"✅ {cleaned} arquivo(s) limpos")
            else:
                print("❌ Limpeza cancelada")
        
        elif choice == "7":
            print("\n❓ AJUDA - BOT DE MENÇÕES")
            print("-" * 40)
            print("Este bot monitora menções à sua conta no X e responde automaticamente.")
            print("\n🔧 Como funciona:")
            print("• Verifica menções a cada 2 minutos")
            print("• Alterna entre ChatGPT e xAI para distribuir tokens")
            print("• Usa prompt personalizado com suas diretrizes")
            print("• Considera contexto da conversa")
            print("\n💡 Dicas:")
            print("• Personalize o prompt na opção 2")
            print("• Monitore as estatísticas na opção 3")
            print("• O bot não responde a si mesmo")
            print("• Mantém histórico para evitar duplicatas")
            print("\n📁 Arquivos importantes:")
            print("• mention_prompt_config.json - Configuração do prompt")
            print("• model_usage_stats.json - Estatísticas de uso")
            print("• mention_bot.log - Log de atividades")
        
        elif choice == "8":
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")
        
        if choice != "8":
            input("\n📱 Pressione Enter para continuar...")

def main():
    """Função principal"""
    print("🤖 Inicializando Bot de Menções...")
    
    # Verificação inicial rápida
    if not os.path.exists("keys.py"):
        print("❌ Arquivo keys.py não encontrado!")
        print("💡 Crie o arquivo com suas chaves de API")
        return
    
    main_menu()

if __name__ == "__main__":
    main()