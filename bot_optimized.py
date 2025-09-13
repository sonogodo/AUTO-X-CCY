# bot_optimized.py
# BOT OTIMIZADO COM RATE LIMITING ADAPTATIVO E CICLO DE SLEEP INTELIGENTE

import tweepy
import openai
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from adaptive_rate_limiter import AdaptiveRateLimiter

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importações locais
from keys import *
from keyword_prompts_improved import prompts_com_aliases, TARGET_USER_IDS, USER_ID_TO_NAME_MAP

class OptimizedXBot:
    def __init__(self):
        self.setup_clients()
        self.setup_prompts()
        self.load_state()
        
        # Inicializa rate limiter adaptativo
        self.rate_limiter = AdaptiveRateLimiter(self.twitter_client)
        
        # Configurações de otimização
        self.optimization_config = {
            "auto_adjust_sleep": True,
            "max_requests_per_window": 100,
            "target_efficiency": 0.85,
            "learning_enabled": True,
            "performance_tracking": True
        }
        
        logger.info("🚀 Bot otimizado inicializado com rate limiting adaptativo")
        
    def setup_clients(self):
        """Inicializa clientes das APIs"""
        try:
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            self.twitter_client = tweepy.Client(
                bearer_token=X_BEARER_TOKEN,
                consumer_key=X_API_KEY,
                consumer_secret=X_API_SECRET,
                access_token=X_ACCESS_TOKEN,
                access_token_secret=X_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            
            logger.info("✅ Clientes de API inicializados")
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    def setup_prompts(self):
        """Configura prompts otimizados"""
        self.keyword_prompts = {}
        for keywords_tuple, prompt_data in prompts_com_aliases.items():
            for keyword in keywords_tuple:
                self.keyword_prompts[keyword.lower()] = prompt_data
        
        logger.info(f"📝 {len(self.keyword_prompts)} prompts carregados")
    
    def load_state(self):
        """Carrega estado do bot"""
        try:
            with open("bot_optimized_state.json", "r") as f:
                self.state = json.load(f)
        except FileNotFoundError:
            self.state = {
                "last_seen_ids": {},
                "processed_tweets": [],
                "performance_metrics": {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "rate_limit_hits": 0,
                    "avg_response_time": 0,
                    "last_optimization": None
                },
                "optimization_history": []
            }
    
    def save_state(self):
        """Salva estado do bot"""
        with open("bot_optimized_state.json", "w") as f:
            json.dump(self.state, f, indent=2)
    
    def make_optimized_api_call(self, api_method, *args, **kwargs):
        """
        Executa chamada da API com otimizações e rate limiting
        """
        start_time = time.time()
        
        try:
            # Incrementa contador de requests
            self.state["performance_metrics"]["total_requests"] += 1
            
            # Executa chamada da API
            response = api_method(*args, **kwargs)
            
            # Atualiza rate limiter com a resposta
            self.rate_limiter.update_rate_limit_from_response(response)
            
            # Registra sucesso
            self.state["performance_metrics"]["successful_requests"] += 1
            
            # Calcula tempo de resposta
            response_time = time.time() - start_time
            current_avg = self.state["performance_metrics"]["avg_response_time"]
            total_requests = self.state["performance_metrics"]["total_requests"]
            
            # Atualiza média de tempo de resposta
            self.state["performance_metrics"]["avg_response_time"] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
            
            return response
            
        except tweepy.TooManyRequests:
            logger.warning("⚠️  Rate limit atingido")
            self.state["performance_metrics"]["rate_limit_hits"] += 1
            
            # Ajusta rate limiter para ser mais conservador
            self.rate_limiter.current_sleep_time = min(
                self.rate_limiter.current_sleep_time * 1.2, 
                300
            )
            
            raise
            
        except Exception as e:
            logger.error(f"❌ Erro na API call: {e}")
            raise
    
    def intelligent_tweet_filtering(self, tweets: List) -> List:
        """
        Filtra tweets de forma inteligente para otimizar processamento
        """
        if not tweets:
            return []
        
        filtered_tweets = []
        
        for tweet in tweets:
            # Filtros de qualidade
            if len(tweet.text.strip()) < 20:
                continue
                
            if tweet.text.startswith("RT @") and ":" not in tweet.text:
                continue
                
            if tweet.text.count("#") > 5:
                continue
                
            if tweet.text.count("@") > 3:
                continue
            
            # Verifica se já foi processado recentemente
            if tweet.id in self.state["processed_tweets"]:
                continue
            
            # Verifica se contém palavras-chave relevantes
            has_keyword = any(
                keyword in tweet.text.lower() 
                for keyword in self.keyword_prompts.keys()
            )
            
            if has_keyword:
                filtered_tweets.append(tweet)
        
        logger.info(f"🔍 Filtrados {len(filtered_tweets)} de {len(tweets)} tweets")
        return filtered_tweets
    
    def generate_optimized_response(self, tweet_text: str, prompt_template: str) -> Optional[str]:
        """
        Gera resposta otimizada com escolha inteligente de modelo
        """
        # Escolhe modelo baseado na complexidade do tweet
        if len(tweet_text) > 200 or any(word in tweet_text.lower() for word in ["dados", "pesquisa", "estudo"]):
            model = "gpt-4o"
            max_tokens = 80
        else:
            model = "gpt-4o-mini"  # Modelo mais barato para tweets simples
            max_tokens = 60
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em gerar respostas concisas e inteligentes para X/Twitter."},
                    {"role": "user", "content": prompt_template.format(tweet_text=tweet_text)}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            comment = response.choices[0].message.content.strip()
            logger.info(f"💬 Resposta gerada com {model} ({response.usage.total_tokens} tokens)")
            
            return comment
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta: {e}")
            return None
    
    def process_user_tweets_optimized(self, user_id: str) -> int:
        """
        Processa tweets de um usuário de forma otimizada
        """
        username = USER_ID_TO_NAME_MAP.get(user_id, f"ID:{user_id}")
        last_id = self.state["last_seen_ids"].get(user_id)
        
        try:
            # Busca tweets com rate limiting adaptativo
            response = self.make_optimized_api_call(
                self.twitter_client.get_users_tweets,
                id=user_id,
                since_id=last_id,
                max_results=10,
                tweet_fields=["created_at", "text", "public_metrics"],
                exclude=["retweets", "replies"]
            )
            
            if not response.data:
                logger.debug(f"📭 Nenhum tweet novo de {username}")
                return 0
            
            # Filtra tweets inteligentemente
            filtered_tweets = self.intelligent_tweet_filtering(response.data)
            
            if not filtered_tweets:
                logger.debug(f"🔍 Nenhum tweet relevante de {username}")
                return 0
            
            processed_count = 0
            
            for tweet in filtered_tweets:
                # Atualiza último ID visto
                self.state["last_seen_ids"][user_id] = max(
                    self.state["last_seen_ids"].get(user_id, 0),
                    int(tweet.id)
                )
                
                # Procura palavras-chave
                keyword_found = None
                for keyword, prompt_data in self.keyword_prompts.items():
                    if keyword in tweet.text.lower():
                        keyword_found = keyword
                        break
                
                if keyword_found:
                    logger.info(f"🎯 Palavra-chave '{keyword_found}' em tweet de {username}")
                    
                    # Gera resposta otimizada
                    comment = self.generate_optimized_response(
                        tweet.text,
                        self.keyword_prompts[keyword_found]["prompt"]
                    )
                    
                    if comment:
                        # Posta resposta com rate limiting
                        try:
                            self.make_optimized_api_call(
                                self.twitter_client.create_tweet,
                                text=comment,
                                in_reply_to_tweet_id=tweet.id
                            )
                            
                            logger.info(f"✅ Resposta postada para {username}")
                            processed_count += 1
                            
                        except Exception as e:
                            logger.error(f"❌ Erro ao postar resposta: {e}")
                
                # Adiciona à lista de processados
                self.state["processed_tweets"].append(tweet.id)
                
                # Mantém apenas últimos 1000 tweets processados
                if len(self.state["processed_tweets"]) > 1000:
                    self.state["processed_tweets"] = self.state["processed_tweets"][-1000:]
            
            return processed_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar {username}: {e}")
            return 0
    
    def optimize_performance(self):
        """
        Otimiza performance baseado no histórico
        """
        metrics = self.state["performance_metrics"]
        
        if metrics["total_requests"] < 10:
            return  # Poucos dados para otimizar
        
        # Calcula taxa de sucesso
        success_rate = metrics["successful_requests"] / metrics["total_requests"]
        
        # Calcula eficiência (requests por minuto sem rate limit)
        rate_limit_rate = metrics["rate_limit_hits"] / metrics["total_requests"]
        
        logger.info(f"📊 Performance atual: {success_rate:.2%} sucesso, {rate_limit_rate:.2%} rate limits")
        
        # Otimizações baseadas na performance
        if rate_limit_rate > 0.1:  # Mais de 10% rate limits
            logger.info("🐌 Muitos rate limits, sendo mais conservador")
            self.rate_limiter.optimize_for_stability()
            
        elif rate_limit_rate < 0.02 and success_rate > 0.95:  # Menos de 2% rate limits
            logger.info("🚀 Performance boa, sendo mais agressivo")
            self.rate_limiter.optimize_for_speed()
        
        # Registra otimização
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "rate_limit_rate": rate_limit_rate,
            "avg_response_time": metrics["avg_response_time"],
            "action": "optimized"
        }
        
        self.state["optimization_history"].append(optimization_record)
        self.state["performance_metrics"]["last_optimization"] = datetime.now().isoformat()
        
        # Mantém apenas últimas 50 otimizações
        if len(self.state["optimization_history"]) > 50:
            self.state["optimization_history"] = self.state["optimization_history"][-50:]
    
    def run_optimized_cycle(self):
        """
        Executa um ciclo otimizado de verificação
        """
        cycle_start = time.time()
        total_processed = 0
        
        logger.info("🔄 Iniciando ciclo otimizado...")
        
        # Processa usuários em ordem de prioridade
        for user_id in TARGET_USER_IDS:
            try:
                processed = self.process_user_tweets_optimized(user_id)
                total_processed += processed
                
                # Sleep adaptativo entre usuários
                if processed > 0:
                    self.rate_limiter.adaptive_sleep("between_users")
                else:
                    time.sleep(2)  # Sleep mínimo entre usuários
                    
            except tweepy.TooManyRequests:
                logger.warning("⚠️  Rate limit global atingido, pausando ciclo")
                break
                
            except Exception as e:
                logger.error(f"❌ Erro no processamento: {e}")
                continue
        
        cycle_time = time.time() - cycle_start
        
        logger.info(f"✅ Ciclo completo: {total_processed} respostas em {cycle_time:.1f}s")
        
        # Salva estado
        self.save_state()
        
        # Otimiza performance a cada 10 ciclos
        if self.state["performance_metrics"]["total_requests"] % 50 == 0:
            self.optimize_performance()
        
        return total_processed
    
    def find_optimal_refresh_rate(self, test_duration_minutes: int = 15):
        """
        Encontra o rate de refresh otimizado
        """
        logger.info(f"🧪 Iniciando teste de otimização por {test_duration_minutes} minutos...")
        
        # Usa o rate limiter para encontrar o mínimo
        results = self.rate_limiter.find_minimum_refresh_rate(test_duration_minutes)
        
        logger.info(f"🎯 Rate otimizado encontrado: {results['optimal_sleep_time']}s")
        
        return results
    
    def get_performance_report(self) -> Dict:
        """
        Gera relatório completo de performance
        """
        metrics = self.state["performance_metrics"]
        rate_limiter_summary = self.rate_limiter.get_performance_summary()
        
        return {
            "bot_metrics": {
                "total_requests": metrics["total_requests"],
                "successful_requests": metrics["successful_requests"],
                "success_rate": metrics["successful_requests"] / max(metrics["total_requests"], 1),
                "rate_limit_hits": metrics["rate_limit_hits"],
                "avg_response_time": metrics["avg_response_time"],
                "last_optimization": metrics["last_optimization"]
            },
            "rate_limiter_metrics": rate_limiter_summary,
            "optimization_history": self.state["optimization_history"][-10:],  # Últimas 10
            "current_config": self.optimization_config
        }
    
    def run(self):
        """
        Loop principal otimizado
        """
        logger.info("🚀 Bot otimizado iniciado!")
        
        # Executa teste inicial para encontrar rate ótimo
        if self.optimization_config["learning_enabled"]:
            logger.info("🧪 Executando calibração inicial...")
            self.find_optimal_refresh_rate(test_duration_minutes=5)
        
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                
                # Executa ciclo otimizado
                processed = self.run_optimized_cycle()
                
                # Sleep adaptativo baseado na performance
                self.rate_limiter.adaptive_sleep(f"cycle_{cycle_count}")
                
                # Relatório de performance a cada 20 ciclos
                if cycle_count % 20 == 0:
                    report = self.get_performance_report()
                    logger.info(f"📊 Ciclo {cycle_count}: {report['bot_metrics']['success_rate']:.2%} sucesso")
                
            except KeyboardInterrupt:
                logger.info("👋 Bot encerrado pelo usuário")
                self.save_state()
                break
                
            except Exception as e:
                logger.error(f"❌ Erro inesperado: {e}")
                time.sleep(60)  # Pausa de 1 minuto em caso de erro

if __name__ == "__main__":
    bot = OptimizedXBot()
    bot.run()