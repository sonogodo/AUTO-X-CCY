# target_manager.py
# GERENCIADOR DE TARGETS - VISUALIZA E GERENCIA USUÁRIOS CRÍTICOS

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
import sys

class TargetManager:
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Carrega dados dos targets"""
        try:
            with open("negative_targets.json", "r") as f:
                self.targets_data = json.load(f)
        except FileNotFoundError:
            self.targets_data = {"targets": {}, "stats": {}}
        
        try:
            with open("target_suggestions.json", "r") as f:
                self.suggestions_data = json.load(f)
        except FileNotFoundError:
            self.suggestions_data = {"pending_targets": []}
    
    def save_data(self):
        """Salva dados dos targets"""
        with open("negative_targets.json", "w") as f:
            json.dump(self.targets_data, f, indent=2, ensure_ascii=False)
        
        with open("target_suggestions.json", "w") as f:
            json.dump(self.suggestions_data, f, indent=2, ensure_ascii=False)
    
    def show_targets_summary(self):
        """Mostra resumo dos targets"""
        targets = self.targets_data.get("targets", {})
        stats = self.targets_data.get("stats", {})
        
        print("\n📊 RESUMO DOS TARGETS")
        print("=" * 40)
        
        if not targets:
            print("Nenhum target identificado ainda")
            return
        
        # Estatísticas gerais
        active_targets = [t for t in targets.values() if t.get("status") == "active"]
        
        print(f"Total de targets: {len(active_targets)}")
        print(f"Tweets analisados: {stats.get('total_analyzed', 0)}")
        print(f"Negativos detectados: {stats.get('negative_detected', 0)}")
        print(f"Última análise: {stats.get('last_analysis', 'Nunca')}")
        
        # Distribuição por score de sentimento
        if active_targets:
            scores = [t.get("sentiment_score", 0) for t in active_targets]
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            
            print(f"\nScore médio de negatividade: {avg_score:.2f}")
            print(f"Score mais negativo: {min_score:.2f}")
        
        # Targets mais recentes
        recent_targets = sorted(active_targets, key=lambda x: x.get("added_date", ""), reverse=True)[:5]
        
        print(f"\n🎯 TARGETS MAIS RECENTES:")
        for i, target in enumerate(recent_targets, 1):
            username = target.get("username", "unknown")
            score = target.get("sentiment_score", 0)
            date = target.get("added_date", "")[:10]  # Apenas a data
            reason = target.get("reason", "")
            
            print(f"{i}. @{username} (Score: {score:.2f}) - {date}")
            print(f"   Razão: {reason}")
    
    def show_detailed_targets(self):
        """Mostra lista detalhada de targets"""
        targets = self.targets_data.get("targets", {})
        
        if not targets:
            print("📭 Nenhum target encontrado")
            return
        
        print("\n🎯 LISTA DETALHADA DE TARGETS")
        print("=" * 60)
        
        # Ordena por data de adição (mais recentes primeiro)
        sorted_targets = sorted(
            targets.items(),
            key=lambda x: x[1].get("added_date", ""),
            reverse=True
        )
        
        for i, (user_id, target) in enumerate(sorted_targets, 1):
            status_icon = "🔴" if target.get("status") == "active" else "⚪"
            
            print(f"\n{status_icon} {i}. @{target.get('username', 'unknown')}")
            print(f"   Nome: {target.get('name', 'Unknown')}")
            print(f"   ID: {user_id}")
            print(f"   Seguidores: {target.get('followers_count', 0):,}")
            print(f"   Score: {target.get('sentiment_score', 0):.2f}")
            print(f"   Adicionado: {target.get('added_date', '')[:19]}")
            print(f"   Razão: {target.get('reason', '')}")
            
            if target.get("is_personal_attack"):
                print("   ⚠️  Ataque pessoal detectado")
            if target.get("is_toxic"):
                print("   ☠️  Linguagem tóxica detectada")
            
            # Mostra exemplo do tweet negativo
            example = target.get("negative_tweet_example", "")
            if example:
                print(f"   Exemplo: \"{example[:80]}{'...' if len(example) > 80 else ''}\"")
    
    def show_pending_suggestions(self):
        """Mostra sugestões pendentes para adicionar ao bot de palavras-chave"""
        suggestions = self.suggestions_data.get("pending_targets", [])
        
        if not suggestions:
            print("📭 Nenhuma sugestão pendente")
            return
        
        print("\n💡 SUGESTÕES PARA ADICIONAR AO BOT DE PALAVRAS-CHAVE")
        print("=" * 60)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. @{suggestion.get('username', 'unknown')}")
            print(f"   ID: {suggestion.get('user_id')}")
            print(f"   Score: {suggestion.get('sentiment_score', 0):.2f}")
            print(f"   Razão: {suggestion.get('reason', '')}")
            print(f"   Código para adicionar:")
            print(f"   {suggestion.get('code_to_add', '')}")
    
    def add_suggestion_to_keyword_bot(self, suggestion_index: int):
        """Adiciona sugestão ao arquivo do bot de palavras-chave"""
        suggestions = self.suggestions_data.get("pending_targets", [])
        
        if suggestion_index < 1 or suggestion_index > len(suggestions):
            print("❌ Índice inválido!")
            return
        
        suggestion = suggestions[suggestion_index - 1]
        user_id = suggestion.get("user_id")
        username = suggestion.get("username")
        
        print(f"\n🔧 Adicionando @{username} ao bot de palavras-chave...")
        
        try:
            # Lê o arquivo atual
            with open("keyword_prompts_improved.py", "r", encoding='utf-8') as f:
                content = f.read()
            
            # Procura a lista TARGET_USER_IDS
            if "TARGET_USER_IDS = [" in content:
                # Adiciona o novo ID à lista
                new_line = f'    "{user_id}",            # @{username} - Target automático (crítica negativa)\n'
                
                # Encontra o final da lista
                lines = content.split('\n')
                new_lines = []
                in_target_list = False
                
                for line in lines:
                    if "TARGET_USER_IDS = [" in line:
                        in_target_list = True
                        new_lines.append(line)
                    elif in_target_list and line.strip() == "]":
                        # Adiciona o novo target antes de fechar a lista
                        new_lines.append(new_line.rstrip())
                        new_lines.append(line)
                        in_target_list = False
                    else:
                        new_lines.append(line)
                
                # Salva o arquivo modificado
                with open("keyword_prompts_improved.py", "w", encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                
                # Adiciona ao mapeamento de nomes também
                self.add_to_name_mapping(user_id, username)
                
                # Remove da lista de sugestões
                suggestions.pop(suggestion_index - 1)
                self.save_data()
                
                print(f"✅ @{username} adicionado com sucesso!")
                print("💡 Reinicie o bot de palavras-chave para aplicar as mudanças")
                
            else:
                print("❌ Não foi possível encontrar TARGET_USER_IDS no arquivo")
                
        except Exception as e:
            print(f"❌ Erro ao modificar arquivo: {e}")
    
    def add_to_name_mapping(self, user_id: str, username: str):
        """Adiciona ao mapeamento de nomes"""
        try:
            with open("keyword_prompts_improved.py", "r", encoding='utf-8') as f:
                content = f.read()
            
            # Procura o dicionário USER_ID_TO_NAME_MAP
            if "USER_ID_TO_NAME_MAP = {" in content:
                lines = content.split('\n')
                new_lines = []
                in_mapping = False
                
                for line in lines:
                    if "USER_ID_TO_NAME_MAP = {" in line:
                        in_mapping = True
                        new_lines.append(line)
                    elif in_mapping and line.strip() == "}":
                        # Adiciona o novo mapeamento antes de fechar
                        new_mapping = f'    "{user_id}": "@{username}",'
                        new_lines.append(new_mapping)
                        new_lines.append(line)
                        in_mapping = False
                    else:
                        new_lines.append(line)
                
                # Salva o arquivo
                with open("keyword_prompts_improved.py", "w", encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                    
        except Exception as e:
            print(f"⚠️  Erro ao adicionar mapeamento de nome: {e}")
    
    def remove_target(self, target_index: int):
        """Remove um target"""
        targets = list(self.targets_data.get("targets", {}).items())
        
        if target_index < 1 or target_index > len(targets):
            print("❌ Índice inválido!")
            return
        
        user_id, target_data = targets[target_index - 1]
        username = target_data.get("username", "unknown")
        
        confirm = input(f"Tem certeza que quer remover @{username}? (s/n): ").lower().strip()
        
        if confirm == 's':
            del self.targets_data["targets"][user_id]
            self.save_data()
            print(f"✅ Target @{username} removido")
        else:
            print("❌ Remoção cancelada")
    
    def export_targets_for_keyword_bot(self):
        """Exporta todos os targets para fácil adição ao bot de palavras-chave"""
        targets = self.targets_data.get("targets", {})
        
        if not targets:
            print("📭 Nenhum target para exportar")
            return
        
        export_file = f"targets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(export_file, "w", encoding='utf-8') as f:
            f.write("# TARGETS PARA ADICIONAR AO BOT DE PALAVRAS-CHAVE\n")
            f.write("# Copie as linhas abaixo para TARGET_USER_IDS em keyword_prompts_improved.py\n\n")
            
            f.write("# IDs para TARGET_USER_IDS:\n")
            for user_id, target in targets.items():
                if target.get("status") == "active":
                    username = target.get("username", "unknown")
                    reason = target.get("reason", "")
                    score = target.get("sentiment_score", 0)
                    f.write(f'    "{user_id}",            # @{username} - {reason} (Score: {score:.2f})\n')
            
            f.write("\n# Mapeamentos para USER_ID_TO_NAME_MAP:\n")
            for user_id, target in targets.items():
                if target.get("status") == "active":
                    username = target.get("username", "unknown")
                    f.write(f'    "{user_id}": "@{username}",\n')
        
        print(f"📄 Targets exportados para: {export_file}")
        print("💡 Copie o conteúdo para keyword_prompts_improved.py")
    
    def show_statistics(self):
        """Mostra estatísticas detalhadas"""
        targets = self.targets_data.get("targets", {})
        stats = self.targets_data.get("stats", {})
        
        print("\n📈 ESTATÍSTICAS DETALHADAS")
        print("=" * 40)
        
        if not targets:
            print("Nenhum dado disponível")
            return
        
        active_targets = [t for t in targets.values() if t.get("status") == "active"]
        
        # Estatísticas gerais
        print(f"Total analisado: {stats.get('total_analyzed', 0)} tweets")
        print(f"Negativos detectados: {stats.get('negative_detected', 0)}")
        print(f"Taxa de negatividade: {(stats.get('negative_detected', 0) / max(stats.get('total_analyzed', 1), 1)) * 100:.1f}%")
        print(f"Targets adicionados: {len(active_targets)}")
        
        if active_targets:
            # Análise por período
            now = datetime.now()
            last_24h = sum(1 for t in active_targets 
                          if datetime.fromisoformat(t.get("added_date", "1970-01-01")) > now - timedelta(days=1))
            last_7d = sum(1 for t in active_targets 
                         if datetime.fromisoformat(t.get("added_date", "1970-01-01")) > now - timedelta(days=7))
            
            print(f"\nTargets nas últimas 24h: {last_24h}")
            print(f"Targets nos últimos 7 dias: {last_7d}")
            
            # Análise de sentimento
            scores = [t.get("sentiment_score", 0) for t in active_targets]
            print(f"\nScore médio: {sum(scores) / len(scores):.2f}")
            print(f"Score mais negativo: {min(scores):.2f}")
            print(f"Score menos negativo: {max(scores):.2f}")
            
            # Tipos de problemas
            personal_attacks = sum(1 for t in active_targets if t.get("is_personal_attack"))
            toxic_language = sum(1 for t in active_targets if t.get("is_toxic"))
            
            print(f"\nAtaques pessoais: {personal_attacks}")
            print(f"Linguagem tóxica: {toxic_language}")
    
    def show_menu(self):
        """Menu principal"""
        while True:
            print("\n" + "="*50)
            print("🎯 GERENCIADOR DE TARGETS")
            print("="*50)
            print("1. 📊 Resumo dos targets")
            print("2. 📋 Lista detalhada")
            print("3. 💡 Sugestões pendentes")
            print("4. ➕ Adicionar sugestão ao bot")
            print("5. ➖ Remover target")
            print("6. 📤 Exportar targets")
            print("7. 📈 Estatísticas detalhadas")
            print("8. 🚀 Iniciar monitor de sentimento")
            print("9. 🔄 Recarregar dados")
            print("10. ❌ Sair")
            
            choice = input("\n👉 Escolha uma opção (1-10): ").strip()
            
            if choice == "1":
                self.show_targets_summary()
            
            elif choice == "2":
                self.show_detailed_targets()
            
            elif choice == "3":
                self.show_pending_suggestions()
            
            elif choice == "4":
                self.show_pending_suggestions()
                if self.suggestions_data.get("pending_targets"):
                    try:
                        index = int(input("\nNúmero da sugestão para adicionar: "))
                        self.add_suggestion_to_keyword_bot(index)
                    except ValueError:
                        print("❌ Digite um número válido!")
            
            elif choice == "5":
                self.show_detailed_targets()
                if self.targets_data.get("targets"):
                    try:
                        index = int(input("\nNúmero do target para remover: "))
                        self.remove_target(index)
                    except ValueError:
                        print("❌ Digite um número válido!")
            
            elif choice == "6":
                self.export_targets_for_keyword_bot()
            
            elif choice == "7":
                self.show_statistics()
            
            elif choice == "8":
                print("\n🚀 Iniciando monitor de sentimento...")
                try:
                    subprocess.run([sys.executable, "sentiment_monitor.py"])
                except Exception as e:
                    print(f"❌ Erro ao iniciar monitor: {e}")
            
            elif choice == "9":
                self.load_data()
                print("🔄 Dados recarregados")
            
            elif choice == "10":
                print("👋 Até logo!")
                break
            
            else:
                print("❌ Opção inválida!")
            
            if choice != "10":
                input("\n📱 Pressione Enter para continuar...")

def main():
    """Função principal"""
    manager = TargetManager()
    manager.show_menu()

if __name__ == "__main__":
    main()