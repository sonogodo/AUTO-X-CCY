# start_sentiment_system.py
# INICIALIZADOR DO SISTEMA DE ANÁLISE DE SENTIMENTO

import os
import sys
import json
import subprocess
from datetime import datetime

def check_dependencies():
    """Verifica dependências do sistema de sentimento"""
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
    
    print("✅ Dependências OK")
    return True

def check_api_keys():
    """Verifica chaves de API"""
    try:
        from keys import X_BEARER_TOKEN, OPENAI_API_KEY
        
        if not X_BEARER_TOKEN or not X_BEARER_TOKEN.strip():
            print("❌ X_BEARER_TOKEN não configurado")
            return False
        
        if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
            print("❌ OPENAI_API_KEY não configurado")
            return False
        
        print("✅ Chaves de API configuradas")
        return True
        
    except ImportError:
        print("❌ Arquivo keys.py não encontrado")
        return False

def get_username():
    """Obtém username do usuário"""
    # Verifica se já existe configuração
    if os.path.exists("sentiment_config.json"):
        try:
            with open("sentiment_config.json", "r") as f:
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
        
        username = username.replace('@', '')
        
        if len(username) < 1 or len(username) > 15:
            print("❌ Username deve ter entre 1 e 15 caracteres!")
            continue
        
        print(f"\nUsername: @{username}")
        confirm = input("Confirma? (s/n): ").lower().strip()
        
        if confirm == 's':
            return username

def test_twitter_connection(username):
    """Testa conexão com Twitter"""
    try:
        import tweepy
        from keys import X_BEARER_TOKEN
        
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN)
        user = client.get_user(username=username)
        
        print(f"✅ Usuário encontrado: @{user.data.username} ({user.data.name})")
        return True
        
    except tweepy.NotFound:
        print(f"❌ Usuário @{username} não encontrado!")
        return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def show_system_status():
    """Mostra status do sistema de sentimento"""
    print("\n📊 STATUS DO SISTEMA DE SENTIMENTO")
    print("-" * 40)
    
    # Verifica arquivos
    files_status = {
        "sentiment_monitor.py": "Monitor principal",
        "target_manager.py": "Gerenciador de targets",
        "negative_targets.json": "Base de targets",
        "sentiment_config.json": "Configurações",
        "target_suggestions.json": "Sugestões pendentes"
    }
    
    for filename, description in files_status.items():
        if os.path.exists(filename):
            print(f"✅ {description}: {filename}")
        else:
            print(f"❌ {description}: {filename} (será criado)")
    
    # Estatísticas se disponível
    try:
        with open("negative_targets.json", "r") as f:
            data = json.load(f)
            
        targets = data.get("targets", {})
        stats = data.get("stats", {})
        
        if targets or stats:
            print(f"\n📈 ESTATÍSTICAS:")
            print(f"• Targets identificados: {len(targets)}")
            print(f"• Tweets analisados: {stats.get('total_analyzed', 0)}")
            print(f"• Negativos detectados: {stats.get('negative_detected', 0)}")
            
            if stats.get('last_analysis'):
                last_analysis = stats['last_analysis'][:19]
                print(f"• Última análise: {last_analysis}")
                
    except FileNotFoundError:
        print(f"\n📈 Nenhuma estatística disponível ainda")

def configure_sentiment_settings():
    """Configura parâmetros de análise de sentimento"""
    print("\n⚙️  CONFIGURAÇÃO DE ANÁLISE DE SENTIMENTO")
    print("-" * 40)
    
    # Configuração padrão
    config = {
        "analysis_criteria": {
            "negative_threshold": -0.3,
            "criticism_keywords": [
                "errado", "mentira", "falso", "ridículo", "absurdo",
                "burro", "idiota", "ignorante", "patético", "vergonhoso"
            ]
        },
        "target_criteria": {
            "min_negativity_score": -0.4,
            "require_personal_attack": True,
            "exclude_constructive_criticism": True
        },
        "monitoring_settings": {
            "check_interval_minutes": 5,
            "max_replies_per_check": 20,
            "days_to_keep_targets": 30
        }
    }
    
    print("Configurações atuais:")
    print(f"• Limite de negatividade: {config['analysis_criteria']['negative_threshold']}")
    print(f"• Score mínimo para target: {config['target_criteria']['min_negativity_score']}")
    print(f"• Intervalo de verificação: {config['monitoring_settings']['check_interval_minutes']} minutos")
    print(f"• Máximo de respostas por verificação: {config['monitoring_settings']['max_replies_per_check']}")
    
    customize = input("\nPersonalizar configurações? (s/n): ").lower().strip()
    
    if customize == 's':
        print("\n🔧 PERSONALIZAÇÃO:")
        
        # Limite de negatividade
        try:
            threshold = float(input(f"Limite de negatividade (-1 a 0, atual: {config['analysis_criteria']['negative_threshold']}): "))
            if -1 <= threshold <= 0:
                config['analysis_criteria']['negative_threshold'] = threshold
        except ValueError:
            print("Mantendo valor atual")
        
        # Score mínimo para target
        try:
            min_score = float(input(f"Score mínimo para virar target (-1 a 0, atual: {config['target_criteria']['min_negativity_score']}): "))
            if -1 <= min_score <= 0:
                config['target_criteria']['min_negativity_score'] = min_score
        except ValueError:
            print("Mantendo valor atual")
        
        # Intervalo de verificação
        try:
            interval = int(input(f"Intervalo de verificação em minutos (atual: {config['monitoring_settings']['check_interval_minutes']}): "))
            if 1 <= interval <= 60:
                config['monitoring_settings']['check_interval_minutes'] = interval
        except ValueError:
            print("Mantendo valor atual")
    
    # Salva configuração
    with open("sentiment_config.json", "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Configurações salvas")
    return config

def show_main_menu():
    """Menu principal do sistema de sentimento"""
    while True:
        print("\n" + "="*60)
        print("😠 SISTEMA DE ANÁLISE DE SENTIMENTO")
        print("="*60)
        print("1. 🚀 Iniciar monitor de sentimento")
        print("2. 🎯 Gerenciar targets identificados")
        print("3. 📊 Ver status do sistema")
        print("4. ⚙️  Configurar parâmetros")
        print("5. 🔧 Testar configurações")
        print("6. 📄 Ver logs do monitor")
        print("7. 🧹 Limpar dados antigos")
        print("8. ❓ Ajuda")
        print("9. ❌ Sair")
        
        choice = input("\n👉 Escolha uma opção (1-9): ").strip()
        
        if choice == "1":
            # Verifica sistema
            if not check_dependencies() or not check_api_keys():
                print("\n❌ Resolva os problemas antes de continuar")
                continue
            
            # Obtém username
            username = get_username()
            
            # Testa conexão
            if not test_twitter_connection(username):
                print("\n❌ Não foi possível conectar")
                continue
            
            # Inicia monitor
            print(f"\n🚀 Iniciando monitor para @{username}...")
            try:
                from sentiment_monitor import SentimentMonitor
                monitor = SentimentMonitor(username)
                monitor.run()
            except KeyboardInterrupt:
                print("\n👋 Monitor encerrado pelo usuário")
            except Exception as e:
                print(f"\n❌ Erro ao executar monitor: {e}")
        
        elif choice == "2":
            print("\n🎯 Abrindo gerenciador de targets...")
            try:
                subprocess.run([sys.executable, "target_manager.py"])
            except Exception as e:
                print(f"❌ Erro ao abrir gerenciador: {e}")
        
        elif choice == "3":
            show_system_status()
        
        elif choice == "4":
            configure_sentiment_settings()
        
        elif choice == "5":
            print("\n🔧 Testando configurações...")
            if check_dependencies() and check_api_keys():
                username = input("Username para testar (sem @): ").strip()
                if username:
                    test_twitter_connection(username)
        
        elif choice == "6":
            print("\n📄 LOGS DO MONITOR")
            print("-" * 30)
            
            if os.path.exists("sentiment_monitor.log"):
                try:
                    with open("sentiment_monitor.log", "r") as f:
                        lines = f.readlines()
                        # Mostra últimas 20 linhas
                        for line in lines[-20:]:
                            print(line.strip())
                except Exception as e:
                    print(f"❌ Erro ao ler log: {e}")
            else:
                print("Nenhum log encontrado")
        
        elif choice == "7":
            print("\n🧹 LIMPEZA DE DADOS")
            print("⚠️  Isso irá remover:")
            print("• Todos os targets identificados")
            print("• Histórico de análises")
            print("• Logs do sistema")
            
            confirm = input("\nTem certeza? (digite 'CONFIRMO'): ").strip()
            if confirm == "CONFIRMO":
                files_to_clean = [
                    "negative_targets.json",
                    "analyzed_replies.json",
                    "last_own_tweet_id.json",
                    "target_suggestions.json",
                    "sentiment_monitor.log"
                ]
                
                cleaned = 0
                for filename in files_to_clean:
                    if os.path.exists(filename):
                        backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        os.rename(filename, backup_name)
                        print(f"📦 {filename} → {backup_name}")
                        cleaned += 1
                
                print(f"✅ {cleaned} arquivo(s) limpos (backups criados)")
            else:
                print("❌ Limpeza cancelada")
        
        elif choice == "8":
            show_help()
        
        elif choice == "9":
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")
        
        if choice != "9":
            input("\n📱 Pressione Enter para continuar...")

def show_help():
    """Mostra ajuda do sistema"""
    print("\n❓ AJUDA - SISTEMA DE ANÁLISE DE SENTIMENTO")
    print("="*60)
    
    print("\n🎯 COMO FUNCIONA:")
    print("1. O monitor verifica respostas aos seus tweets")
    print("2. Analisa o sentimento usando IA (OpenAI)")
    print("3. Identifica críticas negativas e ataques pessoais")
    print("4. Adiciona automaticamente como 'targets'")
    print("5. Targets podem ser adicionados ao bot de palavras-chave")
    
    print("\n⚙️  CONFIGURAÇÕES IMPORTANTES:")
    print("• Negative Threshold: Limite para considerar negativo (-0.3 padrão)")
    print("• Min Negativity Score: Score mínimo para virar target (-0.4 padrão)")
    print("• Check Interval: Frequência de verificação (5 min padrão)")
    print("• Personal Attack: Se deve exigir ataque pessoal para virar target")
    
    print("\n📊 CRITÉRIOS DE ANÁLISE:")
    print("• Score de -1 (muito negativo) a +1 (muito positivo)")
    print("• Detecta ataques pessoais vs crítica construtiva")
    print("• Identifica linguagem tóxica")
    print("• Filtra spam e bots")
    
    print("\n🎯 GERENCIAMENTO DE TARGETS:")
    print("• Visualize todos os targets identificados")
    print("• Exporte para adicionar ao bot de palavras-chave")
    print("• Remova targets incorretos")
    print("• Veja estatísticas detalhadas")
    
    print("\n📁 ARQUIVOS IMPORTANTES:")
    print("• negative_targets.json - Base de dados dos targets")
    print("• sentiment_config.json - Configurações do sistema")
    print("• target_suggestions.json - Sugestões para o bot")
    print("• sentiment_monitor.log - Log de atividades")
    
    print("\n💡 DICAS:")
    print("• Ajuste o threshold se estiver detectando muitos falsos positivos")
    print("• Use o gerenciador para revisar targets antes de adicionar ao bot")
    print("• Monitore os logs para entender o comportamento do sistema")
    print("• Faça backup dos dados antes de limpezas")

def main():
    """Função principal"""
    print("😠 Inicializando Sistema de Análise de Sentimento...")
    
    if not os.path.exists("keys.py"):
        print("❌ Arquivo keys.py não encontrado!")
        print("💡 Configure suas chaves de API primeiro")
        return
    
    show_main_menu()

if __name__ == "__main__":
    main()