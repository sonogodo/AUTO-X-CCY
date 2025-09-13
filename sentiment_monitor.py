# sentiment_monitor.py
# MONITOR DE SENTIMENTO - DETECTA CRÍTICAS NEGATIVAS E ADICIONA COMO TARGETS

import tweepy
import openai
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sentiment_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importações locais
from keys import *

class SentimentMonitor:
    def __init__(self, my_username: str):
        """
        Inicializa o monitor de sentimento
        
        Args:
            my_username: Seu username no X (sem @)
        """
        self.my_username = my_username.lower().replace('@', '')
        self.setup_clients()
        self.load_state()
        self.load_sentiment_config()
        
    def setup_clients(self):
        """Configura clientes das APIs"""
        try:
            # Cliente OpenAI para análise de sentimento
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
            
            logger.info(f"✅ Monitor inicializado para @{self.my_username} (ID: {self.my_user_id})")
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    def load_state(self):
        """Carrega estado persistente"""
        # Targets identificados
        try:
            with open("negative_targets.json", "r") as f:
                self.negative_targets = json.load(f)
        except FileNotFoundError:
            self.negative_targets = {
                "targets": {},  # user_id: {info, reason, added_date, tweet_examples}
                "stats": {
                    "total_analyzed": 0,
                    "negative_detected": 0,
                    "targets_added": 0,
                    "last_analysis": None
                }
            }
        
        # Tweets já analisados
        try:
            with open("analyzed_replies.json", "r") as f:
                self.analyzed_replies = set(json.load(f))
        except FileNotFoundError:
            self.analyzed_replies = set()
        
        # Último ID de tweet próprio verificado
        try:
            with open("last_own_tweet_id.json", "r") as f:
                data = json.load(f)
                self.last_own_tweet_id = data.get("last_id")
        except FileNotFoundError:
            self.last_own_tweet_id = None
    
    def save_state(self):
        """Salva estado persistente"""
        with open("negative_targets.json", "w") as f:
            json.dump(self.negative_targets, f, indent=2, ensure_ascii=False)
        
        with open("analyzed_replies.json", "w") as f:
            json.dump(list(self.analyzed_replies), f)
        
        with open("last_own_tweet_id.json", "w") as f:
            json.dump({"last_id": self.last_own_tweet_id}, f)
    
    def load_sentiment_config(self):
        """Carrega configuração de análise de sentimento"""
        try:
            with open("sentiment_config.json", "r", encoding='utf-8') as f:
                self.sentiment_config = json.load(f)
        except FileNotFoundError:
            self.sentiment_config = self.create_default_sentiment_config()
            self.save_sentiment_config()
    
    def create_default_sentiment_config(self) -> Dict:
        """Cria configuração padrão para análise de sentimento"""
        return {
            "analysis_criteria": {
                "negative_threshold": -0.3,  # -1 a 1, onde -1 é muito negativo
                "criticism_keywords": [
                    "errado", "mentira", "falso", "ridículo", "absurdo",
                    "burro", "idiota", "ignorante", "patético", "vergonhoso",
                    "lixo", "nojento", "horrível", "péssimo", "terrível"
                ],
                "toxic_patterns": [
                    "você não sabe",
                    "que vergonha",
                    "completamente errado",
                    "não entende nada",
                    "pura ignorância"
                ]
            },
            "target_criteria": {
                "min_negativity_score": -0.4,
                "require_personal_attack": True,
                "exclude_constructive_criticism": True,
                "min_follower_count": 10,  # Evita bots óbvios
                "max_follower_count": 1000000  # Evita contas muito grandes
            },
            "monitoring_settings": {
                "check_interval_minutes": 5,
                "max_replies_per_check": 20,
                "days_to_keep_targets": 30,
                "auto_add_to_keyword_bot": True
            }
        }
    
    def save_sentiment_config(self):
        """Salva configuração de sentimento"""
        with open("sentiment_config.json", "w", encoding='utf-8') as f:
            json.dump(self.sentiment_config, f, indent=2, ensure_ascii=False)
    
    def analyze_sentiment_with_ai(self, tweet_text: str, context: str = "") -> Dict:
        """
        Analisa sentimento usando IA
        """
        prompt = f"""
Analise o sentimento e tom deste tweet/resposta:

Tweet: "{tweet_text}"
{f"Contexto: {context}" if context else ""}

Avalie em uma escala de -1 a 1:
- -1: Muito negativo/hostil/ofensivo
- 0: Neutro
- 1: Muito positivo/construtivo

Também identifique:
1. É uma crítica pessoal/ataque?
2. É construtivo ou destrutivo?
3. Contém linguagem tóxica?
4. É spam ou bot?

Responda APENAS em formato JSON:
{{
    "sentiment_score": 0.0,
    "is_personal_attack": false,
    "is_constructive": true,
    "is_toxic": false,
    "is_spam_bot": false,
    "confidence": 0.9,
    "reasoning": "breve explicação"
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de sentimento e detecção de toxicidade em redes sociais. Seja preciso e objetivo."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1  # Baixa temperatura para consistência
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Tenta extrair JSON da resposta
            try:
                # Remove possíveis marcadores de código
                result_text = result_text.replace('```json', '').replace('```', '').strip()
                result = json.loads(result_text)
                
                # Valida campos obrigatórios
                required_fields = ['sentiment_score', 'is_personal_attack', 'is_constructive', 'is_toxic', 'confidence']
                if all(field in result for field in required_fields):
                    return result
                else:
                    logger.warning(f"Campos faltando na análise: {result}")
                    return self.fallback_sentiment_analysis(tweet_text)
                    
            except json.JSONDecodeError:
                logger.warning(f"Resposta não é JSON válido: {result_text}")
                return self.fallback_sentiment_analysis(tweet_text)
                
        except Exception as e:
            logger.error(f"❌ Erro na análise de sentimento: {e}")
            return self.fallback_sentiment_analysis(tweet_text)
    
    def fallback_sentiment_analysis(self, tweet_text: str) -> Dict:
        """
        Análise de sentimento básica como fallback
        """
        text_lower = tweet_text.lower()
        
        # Conta palavras negativas
        negative_words = self.sentiment_config["analysis_criteria"]["criticism_keywords"]
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Verifica padrões tóxicos
        toxic_patterns = self.sentiment_config["analysis_criteria"]["toxic_patterns"]
        toxic_found = any(pattern in text_lower for pattern in toxic_patterns)
        
        # Calcula score básico
        sentiment_score = -0.2 * negative_count
        if toxic_found:
            sentiment_score -= 0.3
        
        # Limita entre -1 e 1
        sentiment_score = max(-1, min(1, sentiment_score))
        
        return {
            "sentiment_score": sentiment_score,
            "is_personal_attack": toxic_found or negative_count > 2,
            "is_constructive": sentiment_score > -0.2,
            "is_toxic": toxic_found,
            "is_spam_bot": False,
            "confidence": 0.6,
            "reasoning": "Análise básica por palavras-chave"
        }
    
    def should_add_as_target(self, analysis: Dict, user_info: Dict) -> bool:
        """
        Decide se deve adicionar usuário como target
        """
        criteria = self.sentiment_config["target_criteria"]
        
        # Verifica score de negatividade
        if analysis["sentiment_score"] > criteria["min_negativity_score"]:
            return False
        
        # Verifica se é ataque pessoal (se requerido)
        if criteria["require_personal_attack"] and not analysis["is_personal_attack"]:
            return False
        
        # Exclui crítica construtiva (se configurado)
        if criteria["exclude_constructive_criticism"] and analysis["is_constructive"]:
            return False
        
        # Verifica se é spam/bot
        if analysis.get("is_spam_bot", False):
            return False
        
        # Verifica contagem de seguidores
        follower_count = user_info.get("public_metrics", {}).get("followers_count", 0)
        if follower_count < criteria["min_follower_count"]:
            return False
        if follower_count > criteria["max_follower_count"]:
            return False
        
        return True
    
    def add_target(self, user_id: str, user_info: Dict, analysis: Dict, tweet_text: str, original_tweet_id: str):
        """
        Adiciona usuário como target
        """
        target_data = {
            "user_id": user_id,
            "username": user_info.get("username", "unknown"),
            "name": user_info.get("name", "Unknown"),
            "followers_count": user_info.get("public_metrics", {}).get("followers_count", 0),
            "added_date": datetime.now().isoformat(),
            "reason": "Crítica negativa detectada",
            "sentiment_score": analysis["sentiment_score"],
            "is_personal_attack": analysis["is_personal_attack"],
            "is_toxic": analysis["is_toxic"],
            "confidence": analysis["confidence"],
            "original_tweet_id": original_tweet_id,
            "negative_tweet_example": tweet_text,
            "status": "active"
        }
        
        self.negative_targets["targets"][user_id] = target_data
        self.negative_targets["stats"]["targets_added"] += 1
        
        logger.info(f"🎯 Novo target adicionado: @{target_data['username']} (Score: {analysis['sentiment_score']:.2f})")
        
        # Auto-adiciona ao bot de palavras-chave se configurado
        if self.sentiment_config["monitoring_settings"]["auto_add_to_keyword_bot"]:
            self.add_to_keyword_bot_targets(user_id, target_data)
    
    def add_to_keyword_bot_targets(self, user_id: str, target_data: Dict):
        """
        Adiciona target ao bot de palavras-chave automaticamente
        """
        try:
            # Tenta carregar configuração do bot de palavras-chave
            from keyword_prompts_improved import TARGET_USER_IDS, USER_ID_TO_NAME_MAP
            
            # Verifica se já está na lista
            if user_id not in TARGET_USER_IDS:
                # Adiciona à lista (isso requer modificação do arquivo)
                logger.info(f"📝 Target @{target_data['username']} deve ser adicionado manualmente ao keyword_prompts_improved.py")
                
                # Salva sugestão para adição manual
                self.save_target_suggestion(user_id, target_data)
            else:
                logger.info(f"✅ Target @{target_data['username']} já está no bot de palavras-chave")
                
        except ImportError:
            logger.warning("⚠️  Não foi possível importar configuração do bot de palavras-chave")
    
    def save_target_suggestion(self, user_id: str, target_data: Dict):
        """
        Salva sugestão de target para adição manual
        """
        try:
            with open("target_suggestions.json", "r") as f:
                suggestions = json.load(f)
        except FileNotFoundError:
            suggestions = {"pending_targets": []}
        
        suggestion = {
            "user_id": user_id,
            "username": target_data["username"],
            "name": target_data["name"],
            "reason": target_data["reason"],
            "added_date": target_data["added_date"],
            "sentiment_score": target_data["sentiment_score"],
            "code_to_add": f'    "{user_id}",            # @{target_data["username"]} - {target_data["reason"]}'
        }
        
        # Evita duplicatas
        existing_ids = [s["user_id"] for s in suggestions["pending_targets"]]
        if user_id not in existing_ids:
            suggestions["pending_targets"].append(suggestion)
            
            with open("target_suggestions.json", "w") as f:
                json.dump(suggestions, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Sugestão de target salva: @{target_data['username']}")
    
    def check_my_tweets_for_replies(self):
        """
        Verifica respostas aos meus tweets
        """
        logger.info("🔍 Verificando respostas aos meus tweets...")
        
        try:
            # Busca meus tweets recentes
            my_tweets = self.twitter_client.get_users_tweets(
                id=self.my_user_id,
                since_id=self.last_own_tweet_id,
                max_results=10,
                tweet_fields=["created_at", "conversation_id", "public_metrics"]
            )
            
            if not my_tweets.data:
                logger.info("📭 Nenhum tweet novo meu para verificar")
                return
            
            # Processa cada tweet meu
            for my_tweet in my_tweets.data:
                # Atualiza último ID
                self.last_own_tweet_id = max(
                    self.last_own_tweet_id or 0,
                    int(my_tweet.id)
                )
                
                logger.info(f"📝 Verificando respostas ao tweet {my_tweet.id}")
                
                # Busca respostas a este tweet
                self.analyze_replies_to_tweet(my_tweet.id, my_tweet.text)
                
                # Pausa entre tweets
                time.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar meus tweets: {e}")
    
    def analyze_replies_to_tweet(self, tweet_id: str, original_text: str):
        """
        Analisa respostas a um tweet específico
        """
        try:
            # Busca respostas usando search
            query = f"conversation_id:{tweet_id} -from:{self.my_username}"
            
            replies = self.twitter_client.search_recent_tweets(
                query=query,
                max_results=self.sentiment_config["monitoring_settings"]["max_replies_per_check"],
                tweet_fields=["created_at", "author_id", "conversation_id", "in_reply_to_user_id"],
                user_fields=["username", "name", "public_metrics", "verified"],
                expansions=["author_id"]
            )
            
            if not replies.data:
                logger.info(f"💬 Nenhuma resposta encontrada para tweet {tweet_id}")
                return
            
            # Processa cada resposta
            for reply in replies.data:
                # Pula se já foi analisado
                if reply.id in self.analyzed_replies:
                    continue
                
                # Pula se é minha própria resposta
                if str(reply.author_id) == self.my_user_id:
                    continue
                
                # Obtém informações do autor
                author_info = None
                if replies.includes and 'users' in replies.includes:
                    for user in replies.includes['users']:
                        if user.id == reply.author_id:
                            author_info = user.data
                            break
                
                if not author_info:
                    logger.warning(f"⚠️  Não foi possível obter info do autor {reply.author_id}")
                    continue
                
                logger.info(f"🔍 Analisando resposta de @{author_info['username']}: {reply.text[:50]}...")
                
                # Analisa sentimento
                analysis = self.analyze_sentiment_with_ai(
                    reply.text,
                    f"Resposta ao tweet: '{original_text[:100]}...'"
                )
                
                # Atualiza estatísticas
                self.negative_targets["stats"]["total_analyzed"] += 1
                
                if analysis["sentiment_score"] < self.sentiment_config["analysis_criteria"]["negative_threshold"]:
                    self.negative_targets["stats"]["negative_detected"] += 1
                    
                    logger.info(f"😠 Sentimento negativo detectado: {analysis['sentiment_score']:.2f}")
                    
                    # Verifica se deve adicionar como target
                    if self.should_add_as_target(analysis, author_info):
                        self.add_target(
                            str(reply.author_id),
                            author_info,
                            analysis,
                            reply.text,
                            tweet_id
                        )
                    else:
                        logger.info(f"⏭️  @{author_info['username']} não atende critérios para target")
                else:
                    logger.info(f"😊 Sentimento neutro/positivo: {analysis['sentiment_score']:.2f}")
                
                # Marca como analisado
                self.analyzed_replies.add(reply.id)
                
                # Pausa entre análises
                time.sleep(1)
            
            # Atualiza timestamp da última análise
            self.negative_targets["stats"]["last_analysis"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar respostas: {e}")
    
    def cleanup_old_targets(self):
        """
        Remove targets antigos baseado na configuração
        """
        days_to_keep = self.sentiment_config["monitoring_settings"]["days_to_keep_targets"]
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        targets_to_remove = []
        
        for user_id, target_data in self.negative_targets["targets"].items():
            added_date = datetime.fromisoformat(target_data["added_date"])
            if added_date < cutoff_date:
                targets_to_remove.append(user_id)
        
        for user_id in targets_to_remove:
            removed_target = self.negative_targets["targets"].pop(user_id)
            logger.info(f"🗑️  Target removido (expirado): @{removed_target['username']}")
        
        if targets_to_remove:
            logger.info(f"🧹 {len(targets_to_remove)} target(s) antigo(s) removido(s)")
    
    def get_targets_summary(self) -> Dict:
        """
        Retorna resumo dos targets
        """
        active_targets = [t for t in self.negative_targets["targets"].values() if t.get("status") == "active"]
        
        return {
            "total_targets": len(active_targets),
            "total_analyzed": self.negative_targets["stats"]["total_analyzed"],
            "negative_detected": self.negative_targets["stats"]["negative_detected"],
            "targets_added": self.negative_targets["stats"]["targets_added"],
            "last_analysis": self.negative_targets["stats"]["last_analysis"],
            "recent_targets": sorted(active_targets, key=lambda x: x["added_date"], reverse=True)[:5]
        }
    
    def run(self):
        """
        Loop principal do monitor
        """
        logger.info(f"🚀 Monitor de sentimento iniciado para @{self.my_username}")
        
        while True:
            try:
                # Verifica respostas aos meus tweets
                self.check_my_tweets_for_replies()
                
                # Limpa targets antigos
                self.cleanup_old_targets()
                
                # Salva estado
                self.save_state()
                
                # Mostra resumo a cada 10 verificações
                if hasattr(self, '_check_count'):
                    self._check_count += 1
                else:
                    self._check_count = 1
                
                if self._check_count % 10 == 0:
                    summary = self.get_targets_summary()
                    logger.info(f"📊 Resumo: {summary['total_targets']} targets ativos, "
                              f"{summary['negative_detected']} negativos de {summary['total_analyzed']} analisados")
                
                # Próxima verificação
                interval = self.sentiment_config["monitoring_settings"]["check_interval_minutes"]
                next_check = datetime.now() + timedelta(minutes=interval)
                logger.info(f"😴 Próxima verificação às {next_check.strftime('%H:%M:%S')}")
                
                time.sleep(interval * 60)
                
            except KeyboardInterrupt:
                logger.info("👋 Monitor encerrado pelo usuário")
                self.save_state()
                break
                
            except Exception as e:
                logger.error(f"❌ Erro inesperado: {e}")
                time.sleep(300)  # 5 minutos em caso de erro

def main():
    """
    Função principal
    """
    print("😠 MONITOR DE SENTIMENTO - DETECTOR DE CRÍTICAS")
    print("=" * 50)
    
    username = input("Digite seu username do X (sem @): ").strip()
    
    if not username:
        print("❌ Username é obrigatório!")
        return
    
    try:
        monitor = SentimentMonitor(username)
        monitor.run()
    except Exception as e:
        print(f"❌ Erro ao iniciar monitor: {e}")

if __name__ == "__main__":
    main()