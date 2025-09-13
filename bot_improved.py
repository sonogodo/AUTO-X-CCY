# bot_improved.py
# VERSÃO 4.0 - BOT INTELIGENTE COM ECONOMIA DE TOKENS E MELHOR PERFORMANCE

import tweepy
import openai
import requests
import time
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importações locais
from keys import *
from keyword_prompts import prompts_com_aliases, TARGET_USER_IDS, USER_ID_TO_NAME_MAP

class SmartXBot:
    def __init__(self):
        self.setup_clients()
        self.setup_prompts()
        self.load_state()
        self.response_cache = {}  # Cache para evitar respostas duplicadas
        self.rate_limit_tracker = {}
        
    def setup_clients(self):
        """Inicializa clientes das APIs com tratamento de erro robusto"""
        try:
            # Cliente OpenAI
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Cliente X/Twitter para posting (v2)
            self.twitter_client = tweepy.Client(
                bearer_token=X_BEARER_TOKEN,
                consumer_key=X_API_KEY,
                consumer_secret=X_API_SECRET,
                access_token=X_ACCESS_TOKEN,
                access_token_secret=X_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True  # Aguarda automaticamente quando atinge rate limit
            )
            
            logger.info("✅ Clientes de API inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO na inicialização: {e}")
            raise
    
    def setup_prompts(self):
        """Configura prompts de forma otimizada"""
        self.keyword_prompts = {}
        for keywords_tuple, prompt_data in prompts_com_aliases.items():
            for keyword in keywords_tuple:
                self.keyword_prompts[keyword.lower()] = prompt_data
        
        logger.info(f"📝 {len(self.keyword_prompts)} prompts carregados para {len(TARGET_USER_IDS)} usuários")
    
    def load_state(self):
        """Carrega estado persistente do bot"""
        # IDs dos últimos tweets vistos
        try:
            with open("last_seen_ids.json", "r") as f:
                self.last_seen_ids = json.load(f)
        except FileNotFoundError:
            self.last_seen_ids = {}
        
        # Cache de tweets já processados (evita duplicatas)
        try:
            with open("processed_tweets.json", "r") as f:
                self.processed_tweets = set(json.load(f))
        except FileNotFoundError:
            self.processed_tweets = set()
        
        # Estatísticas do bot
        try:
            with open("bot_stats.json", "r") as f:
                self.stats = json.load(f)
        except FileNotFoundError:
            self.stats = {
                "tweets_processed": 0,
                "responses_sent": 0,
                "tokens_used": 0,
                "last_reset": datetime.now().isoformat()
            }
    
    def save_state(self):
        """Salva estado persistente"""
        with open("last_seen_ids.json", "w") as f:
            json.dump(self.last_seen_ids, f, indent=2)
        
        with open("processed_tweets.json", "w") as f:
            json.dump(list(self.processed_tweets), f)
        
        with open("bot_stats.json", "w") as f:
            json.dump(self.stats, f, indent=2)
    
    def is_worth_responding(self, tweet_text: str, user_id: str) -> bool:
        """
        INTELIGÊNCIA PARA ECONOMIZAR TOKENS
        Decide se vale a pena gastar tokens respondendo a um tweet
        """
        # Filtros básicos para economizar tokens
        
        # 1. Tweet muito curto (provavelmente não tem conteúdo substancial)
        if len(tweet_text.strip()) < 20:
            return False
        
        # 2. Tweet é apenas RT sem comentário
        if tweet_text.startswith("RT @") and len(tweet_text.split(":")) < 2:
            return False
        
        # 3. Tweet tem muitas hashtags (provavelmente spam)
        hashtag_count = tweet_text.count("#")
        if hashtag_count > 5:
            return False
        
        # 4. Tweet tem muitas menções (provavelmente conversa privada)
        mention_count = tweet_text.count("@")
        if mention_count > 3:
            return False
        
        # 5. Tweet é muito similar a outros recentes (evita spam)
        tweet_hash = hashlib.md5(tweet_text.lower().encode()).hexdigest()
        if tweet_hash in self.response_cache:
            cache_time = self.response_cache[tweet_hash]
            if datetime.now() - cache_time < timedelta(hours=6):
                return False
        
        # 6. Verifica se o usuário não está postando demais
        user_posts_today = self.get_user_post_count_today(user_id)
        if user_posts_today > 10:  # Limite de respostas por usuário por dia
            return False
        
        return True
    
    def get_user_post_count_today(self, user_id: str) -> int:
        """Conta quantas vezes respondemos a este usuário hoje"""
        today = datetime.now().date().isoformat()
        key = f"{user_id}_{today}"
        return self.stats.get("daily_responses", {}).get(key, 0)
    
    def increment_user_post_count(self, user_id: str):
        """Incrementa contador de respostas para o usuário"""
        today = datetime.now().date().isoformat()
        key = f"{user_id}_{today}"
        if "daily_responses" not in self.stats:
            self.stats["daily_responses"] = {}
        self.stats["daily_responses"][key] = self.stats["daily_responses"].get(key, 0) + 1
    
    def generate_smart_comment(self, tweet_text: str, prompt_template: str, user_id: str) -> Optional[str]:
        """
        Geração inteligente de comentários com alternância de modelos e cache
        """
        # Verifica cache primeiro
        cache_key = hashlib.md5(f"{tweet_text}{prompt_template}".encode()).hexdigest()
        
        # Escolhe modelo baseado em critérios inteligentes
        model_name = self.choose_optimal_model(tweet_text, user_id)
        
        try:
            if model_name.startswith("gpt"):
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Você é um assistente especialista em gerar comentários concisos e inteligentes para X/Twitter. Seja natural, relevante e dentro do limite de caracteres."
                        },
                        {
                            "role": "user", 
                            "content": prompt_template.format(tweet_text=tweet_text)
                        }
                    ],
                    max_tokens=60,  # Reduzido para economizar
                    temperature=0.7
                )
                comment = response.choices[0].message.content.strip()
                self.stats["tokens_used"] += response.usage.total_tokens
                
            else:  # Grok
                headers = {
                    "Authorization": f"Bearer {XAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é Grok. Gere comentários concisos e inteligentes para X com seu toque característico de humor."
                        },
                        {
                            "role": "user",
                            "content": prompt_template.format(tweet_text=tweet_text)
                        }
                    ],
                    "max_tokens": 60,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                comment = response.json()["choices"][0]["message"]["content"].strip()
                self.stats["tokens_used"] += 60  # Estimativa para Grok
            
            # Adiciona ao cache
            self.response_cache[cache_key] = datetime.now()
            
            logger.info(f"💬 Comentário gerado com {model_name}: '{comment[:50]}...'")
            return comment
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar comentário com {model_name}: {e}")
            return None
    
    def choose_optimal_model(self, tweet_text: str, user_id: str) -> str:
        """
        Escolhe o modelo mais adequado baseado no contexto
        """
        # Critérios para escolha do modelo:
        
        # 1. Para tweets políticos complexos, usa GPT-4
        political_keywords = ["governo", "política", "eleição", "democracia", "congresso"]
        if any(keyword in tweet_text.lower() for keyword in political_keywords):
            return "gpt-4o"
        
        # 2. Para tweets mais casuais ou humorísticos, usa Grok
        casual_indicators = ["kkkk", "haha", "😂", "🤣", "meme"]
        if any(indicator in tweet_text.lower() for indicator in casual_indicators):
            return "grok-1"
        
        # 3. Alternância baseada no tempo para distribuir carga
        hour = datetime.now().hour
        if hour % 2 == 0:
            return "gpt-4o"
        else:
            return "grok-1"
    
    def check_and_reply_smart(self):
        """
        Versão inteligente da verificação e resposta
        """
        logger.info("🔍 Iniciando verificação inteligente...")
        
        for user_id in TARGET_USER_IDS:
            username = USER_ID_TO_NAME_MAP.get(user_id, f"ID:{user_id}")
            
            try:
                # Verifica rate limit para este usuário
                if self.is_rate_limited(user_id):
                    logger.info(f"⏳ Rate limit ativo para {username}, pulando...")
                    continue
                
                last_id = self.last_seen_ids.get(user_id)
                
                # Busca tweets mais recentes
                response = self.twitter_client.get_users_tweets(
                    id=user_id,
                    since_id=last_id,
                    max_results=10,  # Aumentado para capturar mais tweets
                    tweet_fields=["created_at", "text", "public_metrics"],
                    exclude=["retweets", "replies"]  # Exclui RTs e replies para focar em conteúdo original
                )
                
                if not response.data:
                    logger.info(f"📭 Nenhum tweet novo de {username}")
                    continue
                
                # Processa tweets em ordem cronológica
                tweets = sorted(response.data, key=lambda x: x.created_at)
                processed_count = 0
                
                for tweet in tweets:
                    # Atualiza último ID visto
                    self.last_seen_ids[user_id] = max(
                        self.last_seen_ids.get(user_id, 0), 
                        int(tweet.id)
                    )
                    
                    # Verifica se já processamos este tweet
                    if tweet.id in self.processed_tweets:
                        continue
                    
                    # Filtro inteligente para economizar tokens
                    if not self.is_worth_responding(tweet.text, user_id):
                        logger.info(f"⏭️  Tweet {tweet.id} filtrado (não vale a pena responder)")
                        self.processed_tweets.add(tweet.id)
                        continue
                    
                    # Procura palavras-chave
                    keyword_found = None
                    for keyword, prompt_data in self.keyword_prompts.items():
                        if keyword in tweet.text.lower():
                            keyword_found = keyword
                            break
                    
                    if keyword_found:
                        logger.info(f"🎯 Palavra-chave '{keyword_found}' encontrada em tweet de {username}")
                        
                        # Gera e posta resposta
                        comment = self.generate_smart_comment(
                            tweet.text, 
                            self.keyword_prompts[keyword_found]["prompt"],
                            user_id
                        )
                        
                        if comment and self.post_reply(tweet.id, comment):
                            processed_count += 1
                            self.increment_user_post_count(user_id)
                            self.stats["responses_sent"] += 1
                            
                            # Limite de respostas por ciclo para evitar spam
                            if processed_count >= 2:
                                logger.info(f"🛑 Limite de respostas por ciclo atingido para {username}")
                                break
                    
                    self.processed_tweets.add(tweet.id)
                    self.stats["tweets_processed"] += 1
                
                # Pausa entre usuários
                time.sleep(3)
                
            except tweepy.TooManyRequests:
                logger.warning(f"⚠️  Rate limit atingido para {username}")
                self.set_rate_limit(user_id, 15)  # 15 minutos de pausa
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar {username}: {e}")
                continue
        
        # Salva estado após cada ciclo
        self.save_state()
        self.cleanup_old_data()
        
        logger.info(f"✅ Ciclo completo. Stats: {self.stats['responses_sent']} respostas enviadas, {self.stats['tokens_used']} tokens usados")
    
    def post_reply(self, tweet_id: str, comment: str) -> bool:
        """Posta resposta com tratamento de erro robusto"""
        try:
            self.twitter_client.create_tweet(
                text=comment,
                in_reply_to_tweet_id=tweet_id
            )
            logger.info(f"✅ Resposta postada ao tweet {tweet_id}")
            return True
            
        except tweepy.Forbidden as e:
            logger.error(f"🚫 Resposta proibida ao tweet {tweet_id}: {e}")
            return False
            
        except tweepy.TooManyRequests:
            logger.warning("⚠️  Rate limit atingido ao postar")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao postar resposta: {e}")
            return False
    
    def is_rate_limited(self, user_id: str) -> bool:
        """Verifica se usuário está em rate limit"""
        if user_id in self.rate_limit_tracker:
            return datetime.now() < self.rate_limit_tracker[user_id]
        return False
    
    def set_rate_limit(self, user_id: str, minutes: int):
        """Define rate limit para usuário"""
        self.rate_limit_tracker[user_id] = datetime.now() + timedelta(minutes=minutes)
    
    def cleanup_old_data(self):
        """Limpa dados antigos para manter performance"""
        # Remove tweets processados há mais de 7 dias
        cutoff = datetime.now() - timedelta(days=7)
        
        # Limpa cache de respostas antigas
        old_keys = [
            key for key, timestamp in self.response_cache.items()
            if timestamp < cutoff
        ]
        for key in old_keys:
            del self.response_cache[key]
        
        # Limpa contadores diários antigos
        if "daily_responses" in self.stats:
            today = datetime.now().date()
            old_dates = [
                key for key in self.stats["daily_responses"].keys()
                if datetime.fromisoformat(key.split("_")[1]).date() < today - timedelta(days=7)
            ]
            for key in old_dates:
                del self.stats["daily_responses"][key]
    
    def run(self):
        """Loop principal do bot"""
        logger.info("🚀 Bot inteligente iniciado!")
        
        while True:
            try:
                self.check_and_reply_smart()
                
                # Intervalo inteligente baseado na atividade
                next_check = datetime.now() + timedelta(minutes=10)
                logger.info(f"😴 Próxima verificação às {next_check.strftime('%H:%M:%S')}")
                
                time.sleep(600)  # 10 minutos
                
            except KeyboardInterrupt:
                logger.info("👋 Bot encerrado pelo usuário")
                self.save_state()
                break
                
            except Exception as e:
                logger.error(f"❌ Erro inesperado: {e}")
                time.sleep(300)  # 5 minutos em caso de erro

if __name__ == "__main__":
    bot = SmartXBot()
    bot.run()