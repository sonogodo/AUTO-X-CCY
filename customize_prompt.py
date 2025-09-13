# customize_prompt.py
# FERRAMENTA PARA PERSONALIZAR O PROMPT DO BOT DE MENÇÕES

import json
import os
from typing import Dict, List

class PromptCustomizer:
    def __init__(self):
        self.config_file = "mention_prompt_config.json"
        self.load_config()
    
    def load_config(self):
        """Carrega configuração atual"""
        try:
            with open(self.config_file, "r", encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self.create_default_config()
            self.save_config()
    
    def save_config(self):
        """Salva configuração"""
        with open(self.config_file, "w", encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuração salva em {self.config_file}")
    
    def create_default_config(self) -> Dict:
        """Cria configuração padrão personalizável"""
        return {
            "base_personality": {
                "tone": "inteligente, respeitoso mas firme",
                "style": "direto e factual", 
                "emotion": "equilibrado, nem muito formal nem muito casual",
                "max_length": 280
            },
            "core_beliefs": [
                "Defende a democracia e o Estado de Direito",
                "Valoriza dados e evidências científicas", 
                "Promove o diálogo respeitoso e construtivo",
                "Questiona desinformação de forma educativa",
                "Apoia transparência e accountability"
            ],
            "response_guidelines": [
                "Sempre peça fontes quando alguém faz afirmações sem evidência",
                "Use dados oficiais quando disponíveis (IBGE, TSE, etc.)",
                "Mantenha o foco no argumento, não na pessoa",
                "Seja educativo, não apenas crítico", 
                "Evite linguagem ofensiva ou polarizante"
            ],
            "topics_expertise": {
                "politica": "Conhecimento profundo de instituições e processos democráticos",
                "economia": "Foco em dados oficiais e análise técnica",
                "ciencia": "Valoriza peer review e consenso científico",
                "tecnologia": "Entende impactos sociais da tecnologia",
                "educacao": "Defende educação pública e de qualidade"
            },
            "context_awareness": {
                "check_tweet_context": True,
                "consider_thread": True,
                "analyze_sentiment": True,
                "detect_sarcasm": True
            },
            "custom_instructions": "Você representa uma voz da razão no debate público. Seja sempre construtivo, mesmo quando discorda. Seu objetivo é elevar o nível do debate, não vencer discussões."
        }
    
    def show_current_config(self):
        """Mostra configuração atual"""
        print("\n" + "="*60)
        print("🤖 CONFIGURAÇÃO ATUAL DO BOT")
        print("="*60)
        
        print(f"\n📝 PERSONALIDADE BASE:")
        for key, value in self.config["base_personality"].items():
            print(f"  • {key.title()}: {value}")
        
        print(f"\n💭 VALORES FUNDAMENTAIS ({len(self.config['core_beliefs'])}):")
        for i, belief in enumerate(self.config["core_beliefs"], 1):
            print(f"  {i}. {belief}")
        
        print(f"\n📋 DIRETRIZES DE RESPOSTA ({len(self.config['response_guidelines'])}):")
        for i, guideline in enumerate(self.config["response_guidelines"], 1):
            print(f"  {i}. {guideline}")
        
        print(f"\n🎯 ÁREAS DE EXPERTISE:")
        for topic, description in self.config["topics_expertise"].items():
            print(f"  • {topic.title()}: {description}")
        
        print(f"\n🧠 CONSCIÊNCIA CONTEXTUAL:")
        for feature, enabled in self.config["context_awareness"].items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {feature.replace('_', ' ').title()}")
        
        print(f"\n📜 INSTRUÇÕES PERSONALIZADAS:")
        print(f"  {self.config['custom_instructions']}")
    
    def edit_personality(self):
        """Edita personalidade base"""
        print("\n🎭 EDITANDO PERSONALIDADE BASE")
        print("-" * 40)
        
        personality = self.config["base_personality"]
        
        print(f"Tom atual: {personality['tone']}")
        new_tone = input("Novo tom (Enter para manter): ").strip()
        if new_tone:
            personality['tone'] = new_tone
        
        print(f"Estilo atual: {personality['style']}")
        new_style = input("Novo estilo (Enter para manter): ").strip()
        if new_style:
            personality['style'] = new_style
        
        print(f"Emoção atual: {personality['emotion']}")
        new_emotion = input("Nova emoção (Enter para manter): ").strip()
        if new_emotion:
            personality['emotion'] = new_emotion
        
        print(f"Tamanho máximo atual: {personality['max_length']}")
        new_length = input("Novo tamanho máximo (Enter para manter): ").strip()
        if new_length and new_length.isdigit():
            personality['max_length'] = int(new_length)
        
        print("✅ Personalidade atualizada!")
    
    def edit_beliefs(self):
        """Edita valores fundamentais"""
        print("\n💭 EDITANDO VALORES FUNDAMENTAIS")
        print("-" * 40)
        
        while True:
            print(f"\nValores atuais ({len(self.config['core_beliefs'])}):")
            for i, belief in enumerate(self.config["core_beliefs"], 1):
                print(f"  {i}. {belief}")
            
            print("\nOpções:")
            print("1. Adicionar valor")
            print("2. Remover valor")
            print("3. Editar valor")
            print("4. Voltar")
            
            choice = input("\nEscolha (1-4): ").strip()
            
            if choice == "1":
                new_belief = input("Novo valor: ").strip()
                if new_belief:
                    self.config["core_beliefs"].append(new_belief)
                    print("✅ Valor adicionado!")
            
            elif choice == "2":
                try:
                    index = int(input("Número do valor para remover: ")) - 1
                    if 0 <= index < len(self.config["core_beliefs"]):
                        removed = self.config["core_beliefs"].pop(index)
                        print(f"✅ Removido: {removed}")
                    else:
                        print("❌ Número inválido!")
                except ValueError:
                    print("❌ Digite um número válido!")
            
            elif choice == "3":
                try:
                    index = int(input("Número do valor para editar: ")) - 1
                    if 0 <= index < len(self.config["core_beliefs"]):
                        current = self.config["core_beliefs"][index]
                        print(f"Valor atual: {current}")
                        new_value = input("Novo valor: ").strip()
                        if new_value:
                            self.config["core_beliefs"][index] = new_value
                            print("✅ Valor editado!")
                    else:
                        print("❌ Número inválido!")
                except ValueError:
                    print("❌ Digite um número válido!")
            
            elif choice == "4":
                break
    
    def edit_guidelines(self):
        """Edita diretrizes de resposta"""
        print("\n📋 EDITANDO DIRETRIZES DE RESPOSTA")
        print("-" * 40)
        
        while True:
            print(f"\nDiretrizes atuais ({len(self.config['response_guidelines'])}):")
            for i, guideline in enumerate(self.config["response_guidelines"], 1):
                print(f"  {i}. {guideline}")
            
            print("\nOpções:")
            print("1. Adicionar diretriz")
            print("2. Remover diretriz")
            print("3. Editar diretriz")
            print("4. Voltar")
            
            choice = input("\nEscolha (1-4): ").strip()
            
            if choice == "1":
                new_guideline = input("Nova diretriz: ").strip()
                if new_guideline:
                    self.config["response_guidelines"].append(new_guideline)
                    print("✅ Diretriz adicionada!")
            
            elif choice == "2":
                try:
                    index = int(input("Número da diretriz para remover: ")) - 1
                    if 0 <= index < len(self.config["response_guidelines"]):
                        removed = self.config["response_guidelines"].pop(index)
                        print(f"✅ Removida: {removed}")
                    else:
                        print("❌ Número inválido!")
                except ValueError:
                    print("❌ Digite um número válido!")
            
            elif choice == "3":
                try:
                    index = int(input("Número da diretriz para editar: ")) - 1
                    if 0 <= index < len(self.config["response_guidelines"]):
                        current = self.config["response_guidelines"][index]
                        print(f"Diretriz atual: {current}")
                        new_value = input("Nova diretriz: ").strip()
                        if new_value:
                            self.config["response_guidelines"][index] = new_value
                            print("✅ Diretriz editada!")
                    else:
                        print("❌ Número inválido!")
                except ValueError:
                    print("❌ Digite um número válido!")
            
            elif choice == "4":
                break
    
    def edit_custom_instructions(self):
        """Edita instruções personalizadas"""
        print("\n📜 EDITANDO INSTRUÇÕES PERSONALIZADAS")
        print("-" * 40)
        
        print(f"Instruções atuais:")
        print(f"{self.config['custom_instructions']}")
        
        print(f"\nDigite as novas instruções (ou Enter para manter):")
        new_instructions = input().strip()
        
        if new_instructions:
            self.config['custom_instructions'] = new_instructions
            print("✅ Instruções atualizadas!")
    
    def create_preset(self, name: str):
        """Cria preset personalizado"""
        presets = {
            "politico_progressista": {
                "tone": "firme mas respeitoso, progressista",
                "core_beliefs": [
                    "Defende direitos humanos e igualdade social",
                    "Apoia políticas públicas inclusivas",
                    "Valoriza diversidade e representatividade",
                    "Promove justiça social e econômica",
                    "Defende meio ambiente e sustentabilidade"
                ],
                "custom_instructions": "Você é uma voz progressista que defende mudanças sociais positivas. Seja firme em seus valores mas sempre respeitoso no debate."
            },
            "analista_tecnico": {
                "tone": "técnico, analítico, baseado em dados",
                "core_beliefs": [
                    "Decisões baseadas em evidências e dados",
                    "Metodologia científica é fundamental",
                    "Transparência em análises e conclusões",
                    "Ceticismo saudável com afirmações sem fonte",
                    "Precisão técnica acima de retórica"
                ],
                "custom_instructions": "Você é um analista técnico que prioriza dados e evidências. Sempre peça fontes e questione metodologias de forma construtiva."
            },
            "educador_democratico": {
                "tone": "educativo, paciente, democrático",
                "core_beliefs": [
                    "Educação é a base da democracia",
                    "Diálogo respeitoso constrói consensos",
                    "Informação de qualidade é direito de todos",
                    "Instituições democráticas devem ser fortalecidas",
                    "Participação cidadã é essencial"
                ],
                "custom_instructions": "Você é um educador que busca informar e elevar o debate. Seja sempre didático e construtivo, mesmo com quem discorda."
            }
        }
        
        if name in presets:
            preset = presets[name]
            
            # Aplica configurações do preset
            self.config["base_personality"]["tone"] = preset["tone"]
            self.config["core_beliefs"] = preset["core_beliefs"]
            self.config["custom_instructions"] = preset["custom_instructions"]
            
            print(f"✅ Preset '{name}' aplicado!")
            return True
        
        return False
    
    def show_menu(self):
        """Mostra menu principal"""
        while True:
            print("\n" + "="*50)
            print("🛠️  CUSTOMIZADOR DE PROMPT - BOT DE MENÇÕES")
            print("="*50)
            print("1. 👀 Ver configuração atual")
            print("2. 🎭 Editar personalidade")
            print("3. 💭 Editar valores fundamentais")
            print("4. 📋 Editar diretrizes de resposta")
            print("5. 📜 Editar instruções personalizadas")
            print("6. 🎨 Aplicar preset")
            print("7. 💾 Salvar configuração")
            print("8. 🧪 Testar prompt")
            print("9. ❌ Sair")
            
            choice = input("\n👉 Escolha uma opção (1-9): ").strip()
            
            if choice == "1":
                self.show_current_config()
            
            elif choice == "2":
                self.edit_personality()
            
            elif choice == "3":
                self.edit_beliefs()
            
            elif choice == "4":
                self.edit_guidelines()
            
            elif choice == "5":
                self.edit_custom_instructions()
            
            elif choice == "6":
                print("\nPresets disponíveis:")
                print("1. politico_progressista")
                print("2. analista_tecnico") 
                print("3. educador_democratico")
                
                preset_choice = input("\nEscolha um preset (1-3): ").strip()
                presets = ["politico_progressista", "analista_tecnico", "educador_democratico"]
                
                try:
                    preset_index = int(preset_choice) - 1
                    if 0 <= preset_index < len(presets):
                        self.create_preset(presets[preset_index])
                    else:
                        print("❌ Opção inválida!")
                except ValueError:
                    print("❌ Digite um número válido!")
            
            elif choice == "7":
                self.save_config()
            
            elif choice == "8":
                self.test_prompt()
            
            elif choice == "9":
                print("👋 Até logo!")
                break
            
            else:
                print("❌ Opção inválida!")
            
            input("\n📱 Pressione Enter para continuar...")
    
    def test_prompt(self):
        """Testa o prompt com um exemplo"""
        print("\n🧪 TESTE DO PROMPT")
        print("-" * 30)
        
        # Exemplo de menção
        example_mention = input("Digite um exemplo de menção para testar: ").strip()
        if not example_mention:
            example_mention = "@seuuser o que você acha sobre a nova política econômica?"
        
        # Constrói o prompt
        from mention_bot import MentionBot
        
        # Simula construção do prompt
        config = self.config
        
        prompt = f"""
Você é um assistente inteligente que representa @seuuser no X (Twitter).

PERSONALIDADE E TOM:
- Tom: {config['base_personality']['tone']}
- Estilo: {config['base_personality']['style']}  
- Emoção: {config['base_personality']['emotion']}

VALORES FUNDAMENTAIS:
{chr(10).join(f"• {belief}" for belief in config['core_beliefs'])}

DIRETRIZES DE RESPOSTA:
{chr(10).join(f"• {guideline}" for guideline in config['response_guidelines'])}

INSTRUÇÕES ESPECIAIS:
{config['custom_instructions']}

CONTEXTO DO TWEET:
Autor: @usuario_exemplo
Tweet que me mencionou: "{example_mention}"

TAREFA:
Responda à menção de forma {config['base_personality']['tone']}, seguindo suas diretrizes.
Máximo de {config['base_personality']['max_length']} caracteres.
Seja relevante ao contexto e mantenha sua personalidade consistente.
"""
        
        print("\n📝 PROMPT GERADO:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"• Tamanho do prompt: {len(prompt)} caracteres")
        print(f"• Valores fundamentais: {len(config['core_beliefs'])}")
        print(f"• Diretrizes: {len(config['response_guidelines'])}")

def main():
    """Função principal"""
    customizer = PromptCustomizer()
    customizer.show_menu()

if __name__ == "__main__":
    main()