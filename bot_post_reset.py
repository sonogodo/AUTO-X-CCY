# bot_post_reset.py
# BOT ULTRA-CONSERVADOR PARA USAR APÓS RESET DOS LIMITES

import tweepy
import openai
import time
import json
from datetime import datetime, timedelta
from rate_limit_manager import RateLimitManager

# Importações locais
from keys import *
from keyword_prompts import prompts_com_aliases, TARGET_USER_IDS, USER_ID_TO_NAME_MAP

class PostResetBot:
    def __init__(self):
        self.setup_clients()
        self.rate_manager = RateLimitManager()
        self.load_config()
        self.load_state()
        
        print("🛡️  Bot Ultra-Conservador Inicializado")
        print(f"   • Máximo {self.config['max_posts_per_day']} posts por dia")
        print(f"   • Máximo {self.config['max_posts_per_hour']} posts por hora")
        print(f"   • {self.config['sleep_between_cycles']/60} minutos entre ciclos")
    
    def setup_clients(self):
        """Configura clientes das APIs"""
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.twitter_client = tweepy.Client(
            bearer_token=X_BEARER_TOKEN,
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
    
    def load_config(self):
        """Carrega configuração ultra-conservadora"""
        try:
            with open("ultra_conservative_config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "max_posts_per_day": 8,
                "max_posts_per_hour": 2,
                "sleep_between_cycles": 1800,  # 30 minutos
                "sleep_between_users": 30,     # 30 segundos
                "max_responses_per_cycle": 1,
                "priority_keywords": ["bolsonaro", "lula", "economia", "dilma"],
                "enable_strict_limits": True
            }
    
    def load_state(self):
        """Carrega estado do bot"""
        try:
            with open("post_reset_bot_state.json", "r") as f:
                self.state = json.load(f)
        except FileNotFoundError:
            self.state = {
                "last_seen_ids": {},
                "posts_today": 0,
                "posts_this_hour": 0,
                "last_post_time": None,
                "daily_reset_time": datetime.now().date().isoformat()
            }
    
    def save_state(self):
        """Salva estado do bot"""
        with open("post_reset_bot_state.json", "w") as f:
            json.dump(self.state, f, indent=2)
    
    def can_post_now(self) -> tuple[bool, str]:
        """Verifica se pode postar considerando todos os limites"""
        # Verifica rate limits da API
        api_can_post, api_reason = self.rate_manager.can_post()
        if not api_can_post:
            return False, f"API: {api_reason}"
        
        # Reset diário
        today = datetime.now().date().isoformat()
        if self.state["daily_reset_time"] != today:
            self.state["posts_today"] = 0
            self.state["posts_this_hour"] = 0
            self.state["daily_reset_time"] = today
        
        # Verifica limite diário
        if self.state["posts_today"] >= self.config["max_posts_per_day"]:
            return False, f"Limite diário atingido ({self.state['posts_today']}/{self.config['max_posts_per_day']})"
        
        # Reset horário
        if self.state["last_post_time"]:
            last_post = datetime.fromisoformat(self.state["last_post_time"])
            if (datetime.now() - last_post).total_seconds() >= 3600:
                self.state["posts_this_hour"] = 0
        
        # Verifica limite horário
        if self.state["posts_this_hour"] >= self.config["max_posts_per_hour"]:
            return False, f"Limite horário atingido ({self.state['posts_this_hour']}/{self.config['max_posts_per_hour']})"
        
        return True, "OK para postar"
    
    def is_priority_keyword(self, text: str) -> bool:
        """Verifica se contém palavra-chave prioritária"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.config["priority_keywords"])
    
    def generate_response(self, tweet_text: str, prompt_template: str) -> str:
        """Gera resposta usando modelo mais barato"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Modelo mais barato
                messages=[
                    {"role": "system", "content": "Gere comentário conciso para Twitter. Máximo 100 caracteres."},
                    {"role": "user", "content": prompt_template.format(tweet_text=tweet_text)}
                ],
                max_tokens=40,  # Muito limitado para economizar
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return None
    
    def process_user_conservatively(self, user_id: str) -> bool:
        """Processa um usuário de forma ultra-conservadora"""
        username = USER_ID_TO_NAME_MAP.get(user_id, f"ID:{user_id}")
        last_id = self.state["last_seen_ids"].get(user_id)
        
        try:
            print(f"🔍 Verificando {username}...")
            
            # Busca apenas 3 tweets mais recentes
            response = self.twitter_client.get_users_tweets(
                id=user_id,
                since_id=last_id,
                max_results=3,
                tweet_fields=["created_at"]
            )
            
            if not response.data:
                print(f"   📭 Nenhum tweet novo")
                return False
            
            # Processa apenas o tweet mais recente
            tweet = response.data[0]
            self.state["last_seen_ids"][user_id] = int(tweet.id)
            
            print(f"   📝 Tweet: {tweet.text[:50]}...")
            
            # Verifica se é prioridade
            if not self.is_priority_keyword(tweet.text):
                print(f"   ⏭️  Não é palavra-chave prioritária")
                return False
            
            # Verifica se pode postar
            can_post, reason = self.can_post_now()
            if not can_post:
                print(f"   🚫 Não pode postar: {reason}")
                return False
            
            # Procura palavra-chave
            keyword_found = None
            for keywords_tuple, prompt_data in prompts_com_aliases.items():
                for keyword in keywords_tuple:
                    if keyword.lower() in tweet.text.lower():
                        keyword_found = keyword
                        break
                if keyword_found:
                    break
            
            if keyword_found:
                print(f"   🎯 Palavra-chave encontrada: {keyword_found}")
                
                # Gera resposta
                comment = self.generate_response(
                    tweet.text, 
                    prompts_com_aliases[keywords_tuple]["prompt"]
                )
                
                if comment:
                    # Posta resposta
                    self.twitter_client.create_tweet(
                        text=comment,
                        in_reply_to_tweet_id=tweet.id
                    )
                    
                    # Registra post
                    self.state["posts_today"] += 1
                    self.state["posts_this_hour"] += 1
                    self.state["last_post_time"] = datetime.now().isoformat()
                    self.rate_manager.record_post()
                    
                    print(f"   ✅ RESPOSTA POSTADA: {comment[:30]}...")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {username}: {e}")
            return False
    
    def run_conservative_cycle(self):
        """Executa um ciclo ultra-conservador"""
        print(f"\n🔄 CICLO CONSERVADOR - {datetime.now().strftime('%H:%M:%S')}")
        
        # Verifica status geral
        status = self.rate_manager.get_status()
        print(f"📊 Status: {status['monthly_usage']} mensal, {status['daily_usage']} diário")
        
        responses_sent = 0
        
        # Processa apenas alguns usuários por ciclo
        users_to_check = TARGET_USER_IDS[:5]  # Apenas primeiros 5
        
        for user_id in users_to_check:
            if self.process_user_conservatively(user_id):
                responses_sent += 1
                
                # Para após primeira resposta (ultra-conservador)
                if responses_sent >= self.config["max_responses_per_cycle"]:
                    print("🛑 Limite de respostas por ciclo atingido")
                    break
            
            # Sleep entre usuários
            print(f"😴 Aguardando {self.config['sleep_between_users']}s...")
            time.sleep(self.config["sleep_between_users"])
        
        self.save_state()
        
        print(f"✅ Ciclo completo: {responses_sent} resposta(s) enviada(s)")
        return responses_sent
    
    def run(self):
        """Loop principal ultra-conservador"""
        print("🛡️  BOT ULTRA-CONSERVADOR INICIADO")
        print("=" * 50)
        
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                
                # Verifica se ainda pode operar
                can_post, reason = self.can_post_now()
                if not can_post:
                    print(f"⏸️  Bot pausado: {reason}")
                    print("😴 Aguardando 1 hora...")
                    time.sleep(3600)
                    continue
                
                # Executa ciclo
                self.run_conservative_cycle()
                
                # Sleep longo entre ciclos
                sleep_minutes = self.config["sleep_between_cycles"] / 60
                next_cycle = datetime.now() + timedelta(seconds=self.config["sleep_between_cycles"])
                
                print(f"😴 Próximo ciclo às {next_cycle.strftime('%H:%M:%S')} ({sleep_minutes} min)")
                time.sleep(self.config["sleep_between_cycles"])
                
            except KeyboardInterrupt:
                print("\n👋 Bot encerrado pelo usuário")
                self.save_state()
                break
                
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
                print("⏳ Aguardando 10 minutos...")
                time.sleep(600)

if __name__ == "__main__":
    bot = PostResetBot()
    bot.run()