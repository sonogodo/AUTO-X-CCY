# bot_manager.py
# GERENCIADOR CENTRAL DE TODOS OS BOTS

import os
import sys
import subprocess
import json
from datetime import datetime

class BotManager:
    def __init__(self):
        self.bots_available = {
            "keyword_bot": {
                "name": "Bot de Palavras-Chave",
                "description": "Responde a tweets com palavras-chave específicas",
                "script": "bot_improved.py",
                "config": "keyword_prompts_improved.py"
            },
            "mention_bot": {
                "name": "Bot de Menções", 
                "description": "Responde quando sua conta é mencionada",
                "script": "mention_bot.py",
                "config": "mention_prompt_config.json"
            },
            "original_bot": {
                "name": "Bot Original (Corrigido)",
                "description": "Versão original com correções",
                "script": "bot.py", 
                "config": "keyword_prompts.py"
            },
            "sentiment_system": {
                "name": "Sistema de Análise de Sentimento",
                "description": "Detecta críticas negativas e adiciona como targets",
                "script": "sentiment_monitor.py",
                "config": "sentiment_config.json"
            },
            "optimized_bot": {
                "name": "Bot Otimizado com Rate Limiting Adaptativo",
                "description": "Bot com ciclo de sleep inteligente e auto-otimização",
                "script": "bot_optimized.py",
                "config": "adaptive_rate_limiter.py"
            }
        }
    
    def check_system_status(self):
        """Verifica status geral do sistema"""
        print("🔍 VERIFICANDO STATUS DO SISTEMA...")
        print("-" * 40)
        
        # Verifica dependências
        required_packages = ['tweepy', 'openai', 'requests']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package}")
        
        # Verifica chaves de API
        try:
            from keys import X_BEARER_TOKEN, OPENAI_API_KEY, XAI_API_KEY
            
            keys_status = {
                'X_BEARER_TOKEN': bool(X_BEARER_TOKEN and X_BEARER_TOKEN.strip()),
                'OPENAI_API_KEY': bool(OPENAI_API_KEY and OPENAI_API_KEY.strip()),
                'XAI_API_KEY': bool(XAI_API_KEY and XAI_API_KEY.strip())
            }
            
            print(f"\n🔑 CHAVES DE API:")
            for key_name, status in keys_status.items():
                status_icon = "✅" if status else "❌"
                print(f"{status_icon} {key_name}")
                
        except ImportError:
            print("❌ Arquivo keys.py não encontrado")
            keys_status = {}
        
        # Verifica arquivos dos bots
        print(f"\n📁 ARQUIVOS DOS BOTS:")
        for bot_id, bot_info in self.bots_available.items():
            script_exists = os.path.exists(bot_info["script"])
            status_icon = "✅" if script_exists else "❌"
            print(f"{status_icon} {bot_info['name']}: {bot_info['script']}")
        
        # Status geral
        all_packages_ok = len(missing_packages) == 0
        all_keys_ok = all(keys_status.values()) if keys_status else False
        
        print(f"\n📊 STATUS GERAL:")
        if all_packages_ok and all_keys_ok:
            print("🎉 Sistema pronto para uso!")
            return True
        else:
            print("⚠️  Sistema precisa de configuração")
            if missing_packages:
                print(f"   • Instale: pip install {' '.join(missing_packages)}")
            if not all_keys_ok:
                print("   • Configure chaves de API em keys.py")
            return False
    
    def show_bot_status(self):
        """Mostra status individual de cada bot"""
        print("\n🤖 STATUS DOS BOTS")
        print("-" * 40)
        
        for bot_id, bot_info in self.bots_available.items():
            print(f"\n📋 {bot_info['name']}")
            print(f"   Descrição: {bot_info['description']}")
            print(f"   Script: {bot_info['script']}")
            
            # Verifica se o script existe
            if os.path.exists(bot_info['script']):
                print("   Status: ✅ Disponível")
                
                # Verifica logs específicos
                log_file = bot_info['script'].replace('.py', '.log')
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            if lines:
                                last_line = lines[-1].strip()
                                print(f"   Último log: {last_line[:50]}...")
                    except:
                        pass
                
                # Verifica arquivos de estado
                if bot_id == "mention_bot":
                    stats_file = "model_usage_stats.json"
                    if os.path.exists(stats_file):
                        try:
                            with open(stats_file, 'r') as f:
                                stats = json.load(f)
                                total = stats.get('chatgpt_uses', 0) + stats.get('xai_uses', 0)
                                print(f"   Respostas enviadas: {total}")
                        except:
                            pass
                
                elif bot_id == "keyword_bot":
                    stats_file = "bot_stats.json"
                    if os.path.exists(stats_file):
                        try:
                            with open(stats_file, 'r') as f:
                                stats = json.load(f)
                                print(f"   Tweets processados: {stats.get('tweets_processed', 0)}")
                                print(f"   Respostas enviadas: {stats.get('responses_sent', 0)}")
                        except:
                            pass
            else:
                print("   Status: ❌ Arquivo não encontrado")
    
    def launch_bot(self, bot_id):
        """Lança um bot específico"""
        if bot_id not in self.bots_available:
            print(f"❌ Bot '{bot_id}' não encontrado")
            return
        
        bot_info = self.bots_available[bot_id]
        script = bot_info["script"]
        
        if not os.path.exists(script):
            print(f"❌ Arquivo {script} não encontrado")
            return
        
        print(f"🚀 Iniciando {bot_info['name']}...")
        print(f"📝 Script: {script}")
        print("⏹️  Pressione Ctrl+C para parar")
        print("-" * 40)
        
        try:
            if bot_id == "mention_bot":
                # Bot de menções precisa de configuração especial
                subprocess.run([sys.executable, "start_mention_bot.py"])
            else:
                # Outros bots podem ser executados diretamente
                subprocess.run([sys.executable, script])
                
        except KeyboardInterrupt:
            print(f"\n👋 {bot_info['name']} encerrado pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro ao executar {bot_info['name']}: {e}")
    
    def show_logs(self, bot_id=None):
        """Mostra logs dos bots"""
        if bot_id and bot_id in self.bots_available:
            # Log específico
            log_file = self.bots_available[bot_id]["script"].replace('.py', '.log')
            if os.path.exists(log_file):
                print(f"\n📄 LOG: {self.bots_available[bot_id]['name']}")
                print("-" * 50)
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        # Mostra últimas 20 linhas
                        for line in lines[-20:]:
                            print(line.strip())
                except Exception as e:
                    print(f"❌ Erro ao ler log: {e}")
            else:
                print(f"📄 Nenhum log encontrado para {self.bots_available[bot_id]['name']}")
        else:
            # Todos os logs
            print("\n📄 LOGS DISPONÍVEIS")
            print("-" * 30)
            
            log_files = [f for f in os.listdir('.') if f.endswith('.log')]
            
            if not log_files:
                print("Nenhum arquivo de log encontrado")
                return
            
            for log_file in log_files:
                print(f"\n📋 {log_file}")
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"   Última entrada: {lines[-1].strip()}")
                            print(f"   Total de linhas: {len(lines)}")
                        else:
                            print("   Arquivo vazio")
                except Exception as e:
                    print(f"   ❌ Erro ao ler: {e}")
    
    def cleanup_data(self):
        """Limpa dados antigos de todos os bots"""
        print("🧹 LIMPEZA DE DADOS")
        print("-" * 30)
        
        files_to_clean = [
            # Bot de palavras-chave
            "last_seen_ids.json",
            "processed_tweets.json", 
            "bot_stats.json",
            
            # Bot de menções
            "model_usage_stats.json",
            "processed_mentions.json",
            "last_mention_id.json",
            
            # Logs
            "bot.log",
            "mention_bot.log",
            "bot_improved.log"
        ]
        
        print("⚠️  Arquivos que serão removidos:")
        existing_files = []
        for filename in files_to_clean:
            if os.path.exists(filename):
                existing_files.append(filename)
                print(f"   • {filename}")
        
        if not existing_files:
            print("Nenhum arquivo para limpar")
            return
        
        confirm = input(f"\nRemover {len(existing_files)} arquivo(s)? (digite 'CONFIRMO'): ").strip()
        
        if confirm == "CONFIRMO":
            removed = 0
            for filename in existing_files:
                try:
                    # Cria backup antes de remover
                    backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    os.rename(filename, backup_name)
                    print(f"📦 {filename} → {backup_name}")
                    removed += 1
                except Exception as e:
                    print(f"❌ Erro ao processar {filename}: {e}")
            
            print(f"✅ {removed} arquivo(s) processados (backups criados)")
        else:
            print("❌ Limpeza cancelada")
    
    def show_main_menu(self):
        """Menu principal do gerenciador"""
        while True:
            print("\n" + "="*60)
            print("🤖 GERENCIADOR DE BOTS X.COM")
            print("="*60)
            print("1. 🔍 Verificar status do sistema")
            print("2. 📊 Status dos bots")
            print("3. 🚀 Iniciar Bot de Palavras-Chave")
            print("4. 💬 Iniciar Bot de Menções")
            print("5. 🔄 Iniciar Bot Original")
            print("6. ⚡ Iniciar Bot Otimizado (Rate Limiting Adaptativo)")
            print("7. 😠 Sistema de Análise de Sentimento")
            print("8. 🧪 Testar Rate Limits")
            print("9. 📄 Ver logs")
            print("10. 🛠️  Personalizar Bot de Menções")
            print("11. 🎯 Gerenciar Targets")
            print("12. 📈 Monitorar performance")
            print("13. 🧹 Limpar dados antigos")
            print("14. ❓ Ajuda")
            print("15. ❌ Sair")
            
            choice = input("\n👉 Escolha uma opção (1-15): ").strip()
            
            if choice == "1":
                self.check_system_status()
            
            elif choice == "2":
                self.show_bot_status()
            
            elif choice == "3":
                self.launch_bot("keyword_bot")
            
            elif choice == "4":
                self.launch_bot("mention_bot")
            
            elif choice == "5":
                self.launch_bot("original_bot")
            
            elif choice == "6":
                self.launch_bot("optimized_bot")
            
            elif choice == "7":
                try:
                    subprocess.run([sys.executable, "start_sentiment_system.py"])
                except Exception as e:
                    print(f"❌ Erro ao abrir sistema de sentimento: {e}")
            
            elif choice == "8":
                try:
                    subprocess.run([sys.executable, "rate_limit_tester.py"])
                except Exception as e:
                    print(f"❌ Erro ao abrir testador de rate limit: {e}")
            
            elif choice == "9":
                print("\nQual log deseja ver?")
                print("1. Todos os logs")
                print("2. Bot de Palavras-Chave")
                print("3. Bot de Menções")
                print("4. Bot Original")
                print("5. Sistema de Sentimento")
                print("6. Bot Otimizado")
                
                log_choice = input("Escolha (1-6): ").strip()
                if log_choice == "1":
                    self.show_logs()
                elif log_choice == "2":
                    self.show_logs("keyword_bot")
                elif log_choice == "3":
                    self.show_logs("mention_bot")
                elif log_choice == "4":
                    self.show_logs("original_bot")
                elif log_choice == "5":
                    self.show_logs("sentiment_system")
                elif log_choice == "6":
                    self.show_logs("optimized_bot")
            
            elif choice == "10":
                try:
                    subprocess.run([sys.executable, "customize_prompt.py"])
                except Exception as e:
                    print(f"❌ Erro ao abrir customizador: {e}")
            
            elif choice == "11":
                try:
                    subprocess.run([sys.executable, "target_manager.py"])
                except Exception as e:
                    print(f"❌ Erro ao abrir gerenciador de targets: {e}")
            
            elif choice == "12":
                try:
                    subprocess.run([sys.executable, "bot_monitor.py"])
                except Exception as e:
                    print(f"❌ Erro ao abrir monitor: {e}")
            
            elif choice == "13":
                self.cleanup_data()
            
            elif choice == "14":
                self.show_help()
            
            elif choice == "15":
                print("\n👋 Até logo!")
                break
            
            else:
                print("❌ Opção inválida!")
            
            if choice != "15":
                input("\n📱 Pressione Enter para continuar...")
    
    def show_help(self):
        """Mostra ajuda detalhada"""
        print("\n❓ AJUDA - GERENCIADOR DE BOTS")
        print("="*50)
        
        print("\n🤖 TIPOS DE BOT DISPONÍVEIS:")
        print("\n1. Bot de Palavras-Chave:")
        print("   • Monitora tweets de usuários específicos")
        print("   • Responde quando encontra palavras-chave")
        print("   • Usa filtros inteligentes para economizar tokens")
        print("   • Arquivo: bot_improved.py")
        
        print("\n2. Bot de Menções:")
        print("   • Responde quando sua conta é mencionada")
        print("   • Distribui tokens entre ChatGPT e xAI")
        print("   • Prompt totalmente personalizável")
        print("   • Arquivo: mention_bot.py")
        
        print("\n3. Bot Original:")
        print("   • Versão original com correções")
        print("   • Funcionalidade básica")
        print("   • Arquivo: bot.py")
        
        print("\n🔧 CONFIGURAÇÃO INICIAL:")
        print("1. Configure suas chaves de API em keys.py")
        print("2. Execute 'Verificar status do sistema'")
        print("3. Personalize os prompts conforme necessário")
        print("4. Inicie o bot desejado")
        
        print("\n📊 MONITORAMENTO:")
        print("• Use 'Status dos bots' para visão geral")
        print("• 'Ver logs' mostra atividade detalhada")
        print("• 'Monitorar performance' para estatísticas")
        
        print("\n🛠️  MANUTENÇÃO:")
        print("• 'Limpar dados antigos' remove arquivos desnecessários")
        print("• Logs são rotacionados automaticamente")
        print("• Backups são criados antes de limpezas")
        
        print("\n📁 ARQUIVOS IMPORTANTES:")
        print("• keys.py - Suas chaves de API")
        print("• *_config.json - Configurações dos bots")
        print("• *.log - Logs de atividade")
        print("• *_stats.json - Estatísticas de uso")

def main():
    """Função principal"""
    manager = BotManager()
    manager.show_main_menu()

if __name__ == "__main__":
    main()