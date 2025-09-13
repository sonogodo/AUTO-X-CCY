# mention_bot.py
# BOT ESPECIALIZADO EM RESPONDER MENÇÕES COM DISTRIBUIÇÃO INTELIGENTE DE TOKENS

import tweepy
import openai
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import hashlib

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mention_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importações locais
from keys import *

class MentionBot:
    def __init__(self, my_username: str):
        """
        Inicializa o bot de menções
        
        Args:
            my_username: Seu username no X (sem @), ex: "meuuser"
        """
        self.my_username = my_username.lower().replace('@', '')
        self.setup_clients()
        self.load_state()
        self.load_prompt_config()
        
    def setup_clients(self):
        """Configura clientes das APIs"""
        try:
            # Cliente OpenAI
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Cliente X/Twitter
            self.twitter_client = tweepy.Client(
                bearer_token=X_BEARER_TOKEN,
                consumer_key=X_API_KEY,
                consumer_secret=X_API_SECRET,
                access_token=X_ACCESS_TOKEN,
                access_token_secret=X_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            
            # Pega informações da própria conta
            me = self.twitter_client.get_me()
            self.my_user_id = str(me.data.id)
            self.my_display_name = me.data.name
            
            logger.info(f"✅ Bot inicializado para @{self.my_username} (ID: {self.my_user_id})")
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    def load_state(self):
        """Carrega estado persistente do bot"""
        # Estatísticas de uso dos modelos
        try:
            with open("model_usage_stats.json", "r") as f:
                self.model_stats = json.load(f)
        except FileNotFoundError:
            self.model_stats = {
                "chatgpt_uses": 0,
                "xai_uses": 0,
                "chatgpt_tokens": 0,
                "xai_tokens": 0,
                "last_reset": datetime.now().isoformat()
            }
        
        # Menções já processadas
        try:
            with open("processed_mentions.json", "r") as f:
                self.processed_mentions = set(json.load(f))
        except FileNotFoundError:
            self.processed_mentions = set()
        
        # Último ID de menção processado
        try:
            with open("last_mention_id.json", "r") as f:
                data = json.load(f)
                self.last_mention_id = data.get("last_id")
        except FileNotFoundError:
            self.last_mention_id = None
    
    def save_state(self):
        """Salva estado persistente"""
        # Salva estatísticas dos modelos
        with open("model_usage_stats.json", "w") as f:
            json.dump(self.model_stats, f, indent=2)
        
        # Salva menções processadas
        with open("processed_mentions.json", "w") as f:
            json.dump(list(self.processed_mentions), f)
        
        # Salva último ID
        with open("last_mention_id.json", "w") as f:
            json.dump({"last_id": self.last_mention_id}, f)
    
    def load_prompt_config(self):
        """Carrega configuração do prompt personalizado"""
        try:
            with open("mention_prompt_config.json", "r", encoding='utf-8') as f:
                self.prompt_config = json.load(f)
        except FileNotFoundError:
            # Cria configuração padrão
            self.prompt_config = self.create_default_prompt_config()
            self.save_prompt_config()
    
    def create_default_prompt_config(self) -> Dict:
        """Cria configuração padrão do prompt"""
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
    
    def save_prompt_config(self):
        """Salva configuração do prompt"""
        with open("mention_prompt_config.json", "w", encoding='utf-8') as f:
            json.dump(self.prompt_config, f, indent=2, ensure_ascii=False)
    
    def choose_optimal_model(self) -> str:
        """
        Escolhe o modelo com base no uso anterior para distribuir tokens
        """
        chatgpt_uses = self.model_stats["chatgpt_uses"]
        xai_uses = self.model_stats["xai_uses"]
        
        # Se a diferença for muito grande, usa o menos utilizado
        if abs(chatgpt_uses - xai_uses) > 5:
            if chatgpt_uses < xai_uses:
                return "chatgpt"
            else:
                return "xai"
        
        # Se estão equilibrados, alterna baseado no horário
        hour = datetime.now().hour
        if hour % 2 == 0:
            return "chatgpt"
        else:
            return "xai"
    
    def build_context_prompt(self, mention_tweet: str, author_info: str, thread_context: str = "") -> str:
        """
        Constrói o prompt completo com base na configuração
        """
        config = self.prompt_config
        
        # Prompt base com personalidade
        base_prompt = f"""
Você é um assistente inteligente que representa @{self.my_username} no X (Twitter).

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
Autor: {author_info}
Tweet que me mencionou: "{mention_tweet}"
{f"Contexto da conversa: {thread_context}" if thread_context else ""}

TAREFA:
Responda à menção de forma {config['base_personality']['tone']}, seguindo suas diretrizes.
Máximo de {config['base_personality']['max_length']} caracteres.
Seja relevante ao contexto e mantenha sua personalidade consistente.
"""
        
        return base_prompt.strip()
    
    def generate_response(self, mention_tweet: str, author_info: str, thread_context: str = "") -> Optional[str]:
        """
        Gera resposta usando o modelo escolhido
        """
        model_choice = self.choose_optimal_model()
        prompt = self.build_context_prompt(mention_tweet, author_info, thread_context)
        
        logger.info(f"🤖 Usando modelo: {model_choice}")
        
        try:
            if model_choice == "chatgpt":
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é um assistente especializado em responder menções no X de forma inteligente e contextual."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                
                comment = response.choices[0].message.content.strip()
                tokens_used = response.usage.total_tokens
                
                # Atualiza estatísticas
                self.model_stats["chatgpt_uses"] += 1
                self.model_stats["chatgpt_tokens"] += tokens_used
                
            else:  # xAI
                headers = {
                    "Authorization": f"Bearer {XAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "grok-1",
                    "messages": [
                        {"role": "system", "content": "Você é Grok, respondendo menções de forma inteligente e com personalidade única."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                comment = result["choices"][0]["message"]["content"].strip()
                tokens_used = 100  # Estimativa para xAI
                
                # Atualiza estatísticas
                self.model_stats["xai_uses"] += 1
                self.model_stats["xai_tokens"] += tokens_used
            
            logger.info(f"💬 Resposta gerada ({tokens_used} tokens): {comment[:50]}...")
            return comment
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta com {model_choice}: {e}")
            return None
    
    def get_thread_context(self, tweet_id: str) -> str:
        """
        Obtém contexto da conversa (thread)
        """
        try:
            # Busca o tweet original se for uma resposta
            tweet = self.twitter_client.get_tweet(
                tweet_id, 
                tweet_fields=["conversation_id", "in_reply_to_user_id", "referenced_tweets"]
            )
            
            if tweet.data.referenced_tweets:
                # É uma resposta, busca o tweet original
                original_id = tweet.data.referenced_tweets[0].id
                original = self.twitter_client.get_tweet(original_id)
                return f"Tweet original: {original.data.text[:100]}..."
            
            return ""
            
        except Exception as e:
            logger.warning(f"⚠️  Não foi possível obter contexto: {e}")
            return ""
    
    def check_mentions(self):
        """
        Verifica novas menções e responde
        """
        logger.info("🔍 Verificando novas menções...")
        
        try:
            # Busca menções recentes
            mentions = self.twitter_client.get_users_mentions(
                id=self.my_user_id,
                since_id=self.last_mention_id,
                max_results=10,
                tweet_fields=["created_at", "author_id", "conversation_id", "in_reply_to_user_id"],
                user_fields=["username", "name"]
            )
            
            if not mentions.data:
                logger.info("📭 Nenhuma menção nova")
                return
            
            # Processa menções em ordem cronológica
            mentions_list = sorted(mentions.data, key=lambda x: x.created_at)
            
            for mention in mentions_list:
                # Atualiza último ID processado
                self.last_mention_id = mention.id
                
                # Verifica se já foi processado
                if mention.id in self.processed_mentions:
                    continue
                
                # Não responde a si mesmo
                if str(mention.author_id) == self.my_user_id:
                    continue
                
                # Obtém informações do autor
                author = mentions.includes.get('users', [{}])[0]
                author_info = f"@{author.username} ({author.name})"
                
                logger.info(f"📨 Nova menção de {author_info}: {mention.text}")
                
                # Obtém contexto da conversa
                thread_context = self.get_thread_context(mention.id)
                
                # Gera resposta
                response = self.generate_response(
                    mention.text, 
                    author_info, 
                    thread_context
                )
                
                if response:
                    # Posta resposta
                    try:
                        self.twitter_client.create_tweet(
                            text=response,
                            in_reply_to_tweet_id=mention.id
                        )
                        
                        logger.info(f"✅ Resposta enviada para {author_info}")
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao postar resposta: {e}")
                
                # Marca como processado
                self.processed_mentions.add(mention.id)
                
                # Pausa entre respostas
                time.sleep(5)
            
            # Salva estado
            self.save_state()
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar menções: {e}")
    
    def get_usage_stats(self) -> Dict:
        """
        Retorna estatísticas de uso dos modelos
        """
        total_uses = self.model_stats["chatgpt_uses"] + self.model_stats["xai_uses"]
        total_tokens = self.model_stats["chatgpt_tokens"] + self.model_stats["xai_tokens"]
        
        if total_uses == 0:
            return {"message": "Nenhuma resposta gerada ainda"}
        
        return {
            "total_responses": total_uses,
            "total_tokens": total_tokens,
            "chatgpt": {
                "uses": self.model_stats["chatgpt_uses"],
                "tokens": self.model_stats["chatgpt_tokens"],
                "percentage": (self.model_stats["chatgpt_uses"] / total_uses) * 100
            },
            "xai": {
                "uses": self.model_stats["xai_uses"], 
                "tokens": self.model_stats["xai_tokens"],
                "percentage": (self.model_stats["xai_uses"] / total_uses) * 100
            },
            "balance": abs(self.model_stats["chatgpt_uses"] - self.model_stats["xai_uses"])
        }
    
    def run(self):
        """
        Loop principal do bot
        """
        logger.info(f"🚀 Bot de menções iniciado para @{self.my_username}")
        
        while True:
            try:
                self.check_mentions()
                
                # Mostra estatísticas a cada 10 verificações
                if hasattr(self, '_check_count'):
                    self._check_count += 1
                else:
                    self._check_count = 1
                
                if self._check_count % 10 == 0:
                    stats = self.get_usage_stats()
                    if "total_responses" in stats:
                        logger.info(f"📊 Stats: {stats['total_responses']} respostas, "
                                  f"ChatGPT: {stats['chatgpt']['percentage']:.1f}%, "
                                  f"xAI: {stats['xai']['percentage']:.1f}%")
                
                # Próxima verificação em 2 minutos
                next_check = datetime.now() + timedelta(minutes=2)
                logger.info(f"😴 Próxima verificação às {next_check.strftime('%H:%M:%S')}")
                
                time.sleep(120)  # 2 minutos
                
            except KeyboardInterrupt:
                logger.info("👋 Bot encerrado pelo usuário")
                self.save_state()
                break
                
            except Exception as e:
                logger.error(f"❌ Erro inesperado: {e}")
                time.sleep(300)  # 5 minutos em caso de erro

def main():
    """
    Função principal - solicita username e inicia o bot
    """
    print("🤖 BOT DE MENÇÕES X.COM")
    print("=" * 30)
    
    # Solicita username
    username = input("Digite seu username do X (sem @): ").strip()
    
    if not username:
        print("❌ Username é obrigatório!")
        return
    
    try:
        bot = MentionBot(username)
        bot.run()
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")

if __name__ == "__main__":
    main()