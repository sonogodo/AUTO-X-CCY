# adaptive_rate_limiter.py
# SISTEMA ADAPTATIVO DE RATE LIMITING - ENCONTRA O CICLO MÍNIMO OTIMIZADO

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import tweepy
from dataclasses import dataclass

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rate_limiter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RateLimitInfo:
    """Informações sobre rate limit de um endpoint"""
    endpoint: str
    limit: int
    remaining: int
    reset_time: datetime
    window_seconds: int = 900  # 15 minutos padrão

@dataclass
class AdaptiveConfig:
    """Configuração adaptativa do sistema"""
    min_sleep_seconds: int = 30
    max_sleep_seconds: int = 900
    target_remaining_ratio: float = 0.2  # Manter 20% das requests
    aggressive_mode: bool = False
    learning_rate: float = 0.1

class AdaptiveRateLimiter:
    def __init__(self, twitter_client: tweepy.Client):
        self.client = twitter_client
        self.config = AdaptiveConfig()
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.performance_history: List[Dict] = []
        self.current_sleep_time = 120  # Começa com 2 minutos
        self.load_state()
        
    def load_state(self):
        """Carrega estado persistente do rate limiter"""
        try:
            with open("rate_limiter_state.json", "r") as f:
                data = json.load(f)
                self.current_sleep_time = data.get("current_sleep_time", 120)
                self.performance_history = data.get("performance_history", [])[-100:]  # Últimos 100
                
                # Carrega configuração personalizada
                if "config" in data:
                    config_data = data["config"]
                    self.config.min_sleep_seconds = config_data.get("min_sleep_seconds", 30)
                    self.config.max_sleep_seconds = config_data.get("max_sleep_seconds", 900)
                    self.config.target_remaining_ratio = config_data.get("target_remaining_ratio", 0.2)
                    self.config.aggressive_mode = config_data.get("aggressive_mode", False)
                    
                logger.info(f"✅ Estado carregado: sleep atual = {self.current_sleep_time}s")
                
        except FileNotFoundError:
            logger.info("📁 Criando novo estado do rate limiter")
            self.save_state()
    
    def save_state(self):
        """Salva estado persistente"""
        data = {
            "current_sleep_time": self.current_sleep_time,
            "performance_history": self.performance_history[-100:],  # Mantém apenas últimos 100
            "config": {
                "min_sleep_seconds": self.config.min_sleep_seconds,
                "max_sleep_seconds": self.config.max_sleep_seconds,
                "target_remaining_ratio": self.config.target_remaining_ratio,
                "aggressive_mode": self.config.aggressive_mode
            },
            "last_updated": datetime.now().isoformat()
        }
        
        with open("rate_limiter_state.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def extract_rate_limit_info(self, response) -> Optional[RateLimitInfo]:
        """Extrai informações de rate limit da resposta da API"""
        try:
            if hasattr(response, 'meta') and response.meta:
                # Para respostas com meta (search, get_users_tweets, etc.)
                headers = getattr(response.meta, 'headers', {}) if hasattr(response.meta, 'headers') else {}
            else:
                # Tenta acessar headers diretamente
                headers = getattr(response, 'headers', {})
            
            if not headers:
                return None
            
            # Extrai informações dos headers
            limit = headers.get('x-rate-limit-limit')
            remaining = headers.get('x-rate-limit-remaining')
            reset = headers.get('x-rate-limit-reset')
            
            if limit and remaining and reset:
                return RateLimitInfo(
                    endpoint="general",
                    limit=int(limit),
                    remaining=int(remaining),
                    reset_time=datetime.fromtimestamp(int(reset))
                )
                
        except Exception as e:
            logger.debug(f"Não foi possível extrair rate limit info: {e}")
        
        return None
    
    def update_rate_limit_from_response(self, response, endpoint: str = "general"):
        """Atualiza informações de rate limit baseado na resposta"""
        rate_info = self.extract_rate_limit_info(response)
        
        if rate_info:
            rate_info.endpoint = endpoint
            self.rate_limits[endpoint] = rate_info
            
            logger.debug(f"📊 Rate limit {endpoint}: {rate_info.remaining}/{rate_info.limit} restantes")
            
            # Registra performance
            self.record_performance(endpoint, rate_info)
    
    def record_performance(self, endpoint: str, rate_info: RateLimitInfo):
        """Registra performance para análise adaptativa"""
        performance_record = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "remaining": rate_info.remaining,
            "limit": rate_info.limit,
            "remaining_ratio": rate_info.remaining / rate_info.limit,
            "sleep_time_used": self.current_sleep_time,
            "reset_time": rate_info.reset_time.isoformat()
        }
        
        self.performance_history.append(performance_record)
        
        # Mantém apenas últimos 100 registros
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    def calculate_optimal_sleep_time(self) -> int:
        """Calcula tempo de sleep otimizado baseado no histórico"""
        if len(self.performance_history) < 5:
            return self.current_sleep_time
        
        recent_history = self.performance_history[-10:]  # Últimos 10 registros
        
        # Calcula média de remaining ratio
        avg_remaining_ratio = sum(r["remaining_ratio"] for r in recent_history) / len(recent_history)
        
        # Calcula tendência (está melhorando ou piorando?)
        if len(recent_history) >= 5:
            recent_avg = sum(r["remaining_ratio"] for r in recent_history[-3:]) / 3
            older_avg = sum(r["remaining_ratio"] for r in recent_history[-6:-3]) / 3
            trend = recent_avg - older_avg
        else:
            trend = 0
        
        # Lógica adaptativa
        target_ratio = self.config.target_remaining_ratio
        current_sleep = self.current_sleep_time
        
        if avg_remaining_ratio > target_ratio + 0.1:
            # Temos muitas requests sobrando, podemos ser mais agressivos
            adjustment = -max(10, current_sleep * 0.1)
            if trend > 0:  # Tendência positiva, seja ainda mais agressivo
                adjustment *= 1.5
                
        elif avg_remaining_ratio < target_ratio - 0.1:
            # Poucas requests restantes, precisa ser mais conservador
            adjustment = max(15, current_sleep * 0.2)
            if trend < 0:  # Tendência negativa, seja ainda mais conservador
                adjustment *= 1.5
                
        else:
            # Está no range ideal, pequenos ajustes baseados na tendência
            if trend > 0.05:
                adjustment = -max(5, current_sleep * 0.05)
            elif trend < -0.05:
                adjustment = max(5, current_sleep * 0.05)
            else:
                adjustment = 0
        
        # Aplica ajuste com learning rate
        new_sleep_time = current_sleep + (adjustment * self.config.learning_rate)
        
        # Aplica limites
        new_sleep_time = max(self.config.min_sleep_seconds, 
                           min(self.config.max_sleep_seconds, new_sleep_time))
        
        return int(new_sleep_time)
    
    def should_sleep_now(self) -> Tuple[bool, int]:
        """Decide se deve fazer sleep e por quanto tempo"""
        # Verifica se algum endpoint está próximo do limite
        critical_endpoints = []
        
        for endpoint, rate_info in self.rate_limits.items():
            remaining_ratio = rate_info.remaining / rate_info.limit
            
            if remaining_ratio < 0.1:  # Menos de 10% restante
                critical_endpoints.append((endpoint, remaining_ratio))
        
        if critical_endpoints:
            # Há endpoints críticos, usa sleep mais conservador
            critical_ratio = min(ratio for _, ratio in critical_endpoints)
            emergency_sleep = int(self.current_sleep_time * (1 + (0.1 - critical_ratio) * 10))
            emergency_sleep = min(emergency_sleep, 300)  # Máximo 5 minutos de emergência
            
            logger.warning(f"⚠️  Endpoints críticos detectados: {critical_endpoints}")
            logger.warning(f"🛑 Sleep de emergência: {emergency_sleep}s")
            
            return True, emergency_sleep
        
        # Calcula sleep otimizado
        optimal_sleep = self.calculate_optimal_sleep_time()
        
        # Atualiza sleep atual se mudou significativamente
        if abs(optimal_sleep - self.current_sleep_time) > 5:
            old_sleep = self.current_sleep_time
            self.current_sleep_time = optimal_sleep
            
            logger.info(f"🔄 Sleep ajustado: {old_sleep}s → {optimal_sleep}s")
            self.save_state()
        
        return True, self.current_sleep_time
    
    def adaptive_sleep(self, context: str = "general"):
        """Executa sleep adaptativo com logging"""
        should_sleep, sleep_time = self.should_sleep_now()
        
        if should_sleep:
            next_check = datetime.now() + timedelta(seconds=sleep_time)
            
            logger.info(f"😴 Sleep adaptativo ({context}): {sleep_time}s")
            logger.info(f"⏰ Próxima verificação: {next_check.strftime('%H:%M:%S')}")
            
            # Sleep com possibilidade de interrupção
            self.interruptible_sleep(sleep_time)
    
    def interruptible_sleep(self, total_seconds: int):
        """Sleep que pode ser interrompido e mostra progresso"""
        chunk_size = min(30, total_seconds // 4) if total_seconds > 60 else total_seconds
        chunks = total_seconds // chunk_size
        remainder = total_seconds % chunk_size
        
        try:
            for i in range(chunks):
                time.sleep(chunk_size)
                elapsed = (i + 1) * chunk_size
                remaining = total_seconds - elapsed
                
                if i % 4 == 3:  # Log a cada 4 chunks
                    logger.debug(f"💤 Sleep: {elapsed}s/{total_seconds}s (restam {remaining}s)")
            
            if remainder > 0:
                time.sleep(remainder)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Sleep interrompido pelo usuário")
            raise
    
    def get_performance_summary(self) -> Dict:
        """Retorna resumo de performance do rate limiter"""
        if not self.performance_history:
            return {"message": "Nenhum dado de performance disponível"}
        
        recent = self.performance_history[-20:] if len(self.performance_history) >= 20 else self.performance_history
        
        avg_remaining_ratio = sum(r["remaining_ratio"] for r in recent) / len(recent)
        avg_sleep_time = sum(r["sleep_time_used"] for r in recent) / len(recent)
        
        # Calcula eficiência (requests por minuto)
        if len(recent) >= 2:
            time_span = (datetime.fromisoformat(recent[-1]["timestamp"]) - 
                        datetime.fromisoformat(recent[0]["timestamp"])).total_seconds()
            requests_per_minute = (len(recent) / time_span) * 60 if time_span > 0 else 0
        else:
            requests_per_minute = 0
        
        return {
            "current_sleep_time": self.current_sleep_time,
            "avg_remaining_ratio": avg_remaining_ratio,
            "avg_sleep_time": avg_sleep_time,
            "requests_per_minute": requests_per_minute,
            "total_records": len(self.performance_history),
            "target_remaining_ratio": self.config.target_remaining_ratio,
            "efficiency_score": min(100, (avg_remaining_ratio / self.config.target_remaining_ratio) * 100),
            "recent_endpoints": list(set(r["endpoint"] for r in recent))
        }
    
    def optimize_for_speed(self):
        """Otimiza para velocidade máxima (modo agressivo)"""
        self.config.aggressive_mode = True
        self.config.min_sleep_seconds = 15
        self.config.target_remaining_ratio = 0.05  # Usa 95% das requests
        self.config.learning_rate = 0.2
        
        logger.info("🚀 Modo agressivo ativado - otimizando para velocidade máxima")
        self.save_state()
    
    def optimize_for_stability(self):
        """Otimiza para estabilidade (modo conservador)"""
        self.config.aggressive_mode = False
        self.config.min_sleep_seconds = 60
        self.config.target_remaining_ratio = 0.3  # Usa apenas 70% das requests
        self.config.learning_rate = 0.05
        
        logger.info("🛡️  Modo conservador ativado - otimizando para estabilidade")
        self.save_state()
    
    def find_minimum_refresh_rate(self, test_duration_minutes: int = 30) -> Dict:
        """
        Executa teste para encontrar o rate mínimo de refresh
        """
        logger.info(f"🧪 Iniciando teste de rate mínimo por {test_duration_minutes} minutos...")
        
        test_results = []
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=test_duration_minutes)
        
        # Começa com sleep baixo
        test_sleep_times = [15, 30, 45, 60, 90, 120, 180]
        current_test_index = 0
        
        while datetime.now() < end_time and current_test_index < len(test_sleep_times):
            test_sleep = test_sleep_times[current_test_index]
            logger.info(f"🔬 Testando sleep de {test_sleep}s...")
            
            # Testa por alguns ciclos
            test_start = datetime.now()
            test_cycles = 0
            errors = 0
            
            while (datetime.now() - test_start).total_seconds() < 300 and test_cycles < 5:  # 5 min ou 5 ciclos
                try:
                    # Simula uma operação da API
                    response = self.client.get_me()
                    self.update_rate_limit_from_response(response, "test")
                    
                    test_cycles += 1
                    time.sleep(test_sleep)
                    
                except tweepy.TooManyRequests:
                    errors += 1
                    logger.warning(f"⚠️  Rate limit atingido com sleep {test_sleep}s")
                    time.sleep(300)  # 5 minutos de pausa
                    break
                    
                except Exception as e:
                    errors += 1
                    logger.error(f"❌ Erro no teste: {e}")
                    break
            
            # Registra resultado do teste
            success_rate = (test_cycles - errors) / max(test_cycles, 1)
            test_results.append({
                "sleep_time": test_sleep,
                "cycles": test_cycles,
                "errors": errors,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"📊 Resultado: {test_cycles} ciclos, {errors} erros, {success_rate:.2%} sucesso")
            
            # Se teve muitos erros, para o teste
            if success_rate < 0.8:
                logger.warning(f"🛑 Taxa de sucesso baixa ({success_rate:.2%}), parando teste")
                break
            
            current_test_index += 1
        
        # Analisa resultados
        successful_tests = [t for t in test_results if t["success_rate"] >= 0.9]
        
        if successful_tests:
            optimal_sleep = min(t["sleep_time"] for t in successful_tests)
            logger.info(f"🎯 Rate mínimo encontrado: {optimal_sleep}s")
        else:
            optimal_sleep = 120  # Fallback seguro
            logger.warning(f"⚠️  Nenhum rate confiável encontrado, usando fallback: {optimal_sleep}s")
        
        # Atualiza configuração
        self.current_sleep_time = optimal_sleep
        self.config.min_sleep_seconds = max(15, optimal_sleep - 15)
        self.save_state()
        
        return {
            "optimal_sleep_time": optimal_sleep,
            "test_results": test_results,
            "test_duration": (datetime.now() - start_time).total_seconds(),
            "recommendation": "speed" if optimal_sleep <= 60 else "balanced" if optimal_sleep <= 120 else "conservative"
        }

def create_adaptive_bot_wrapper(original_bot_class):
    """
    Wrapper que adiciona rate limiting adaptativo a qualquer bot
    """
    class AdaptiveBotWrapper(original_bot_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.rate_limiter = AdaptiveRateLimiter(self.twitter_client)
            logger.info("🤖 Bot com rate limiting adaptativo inicializado")
        
        def adaptive_sleep(self, context: str = "general"):
            """Sleep adaptativo"""
            self.rate_limiter.adaptive_sleep(context)
        
        def make_api_call_with_rate_limiting(self, api_call, *args, **kwargs):
            """Executa chamada da API com rate limiting adaptativo"""
            try:
                response = api_call(*args, **kwargs)
                self.rate_limiter.update_rate_limit_from_response(response)
                return response
                
            except tweepy.TooManyRequests as e:
                logger.warning("⚠️  Rate limit atingido, ajustando sleep...")
                self.rate_limiter.current_sleep_time = min(
                    self.rate_limiter.current_sleep_time * 1.5, 
                    300
                )
                self.rate_limiter.save_state()
                time.sleep(300)  # 5 minutos de pausa
                raise
        
        def get_performance_summary(self):
            """Retorna resumo de performance"""
            return self.rate_limiter.get_performance_summary()
    
    return AdaptiveBotWrapper

# Exemplo de uso
if __name__ == "__main__":
    from keys import *
    
    # Cria cliente Twitter
    client = tweepy.Client(bearer_token=X_BEARER_TOKEN)
    
    # Cria rate limiter adaptativo
    rate_limiter = AdaptiveRateLimiter(client)
    
    # Executa teste para encontrar rate mínimo
    print("🧪 Executando teste de rate mínimo...")
    results = rate_limiter.find_minimum_refresh_rate(test_duration_minutes=10)
    
    print(f"\n📊 RESULTADOS DO TESTE:")
    print(f"Rate mínimo otimizado: {results['optimal_sleep_time']}s")
    print(f"Recomendação: {results['recommendation']}")
    print(f"Duração do teste: {results['test_duration']:.1f}s")
    
    # Mostra resumo de performance
    summary = rate_limiter.get_performance_summary()
    print(f"\n📈 RESUMO DE PERFORMANCE:")
    for key, value in summary.items():
        print(f"{key}: {value}")