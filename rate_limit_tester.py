# rate_limit_tester.py
# FERRAMENTA PARA TESTAR E ENCONTRAR O RATE LIMIT MÍNIMO OTIMIZADO

import tweepy
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import pandas as pd

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from keys import *

class RateLimitTester:
    def __init__(self):
        self.setup_client()
        self.test_results = []
        self.current_limits = {}
        
    def setup_client(self):
        """Configura cliente do Twitter"""
        try:
            self.client = tweepy.Client(
                bearer_token=X_BEARER_TOKEN,
                consumer_key=X_API_KEY,
                consumer_secret=X_API_SECRET,
                access_token=X_ACCESS_TOKEN,
                access_token_secret=X_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=False  # Não aguarda automaticamente
            )
            
            # Testa conexão
            me = self.client.get_me()
            logger.info(f"✅ Conectado como @{me.data.username}")
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            raise
    
    def get_rate_limit_status(self) -> Dict:
        """Obtém status atual dos rate limits"""
        try:
            # Faz uma chamada simples para obter headers
            response = self.client.get_me()
            
            # Tenta extrair informações de rate limit dos headers
            if hasattr(response, 'meta') and hasattr(response.meta, 'headers'):
                headers = response.meta.headers
            else:
                headers = {}
            
            limit_info = {
                'limit': headers.get('x-rate-limit-limit', 'unknown'),
                'remaining': headers.get('x-rate-limit-remaining', 'unknown'),
                'reset': headers.get('x-rate-limit-reset', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
            
            if limit_info['reset'] != 'unknown':
                reset_time = datetime.fromtimestamp(int(limit_info['reset']))
                limit_info['reset_time'] = reset_time.isoformat()
                limit_info['minutes_until_reset'] = (reset_time - datetime.now()).total_seconds() / 60
            
            return limit_info
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter rate limit status: {e}")
            return {}
    
    def test_single_interval(self, sleep_seconds: int, test_duration_minutes: int = 5) -> Dict:
        """
        Testa um intervalo específico de sleep
        """
        logger.info(f"🧪 Testando intervalo de {sleep_seconds}s por {test_duration_minutes} minutos...")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=test_duration_minutes)
        
        results = {
            'sleep_seconds': sleep_seconds,
            'start_time': start_time.isoformat(),
            'requests_made': 0,
            'successful_requests': 0,
            'rate_limit_hits': 0,
            'errors': 0,
            'avg_response_time': 0,
            'total_response_time': 0,
            'rate_limit_info': []
        }
        
        while datetime.now() < end_time:
            request_start = time.time()
            
            try:
                # Faz uma chamada de teste (get_me é leve)
                response = self.client.get_me()
                
                # Registra tempo de resposta
                response_time = time.time() - request_start
                results['total_response_time'] += response_time
                results['requests_made'] += 1
                results['successful_requests'] += 1
                
                # Obtém informações de rate limit
                rate_info = self.get_rate_limit_status()
                if rate_info:
                    results['rate_limit_info'].append(rate_info)
                
                logger.debug(f"✅ Request {results['requests_made']}: {response_time:.2f}s")
                
                # Sleep do teste
                time.sleep(sleep_seconds)
                
            except tweepy.TooManyRequests as e:
                logger.warning(f"⚠️  Rate limit atingido após {results['requests_made']} requests")
                results['rate_limit_hits'] += 1
                results['requests_made'] += 1
                
                # Pausa até o reset (ou máximo 15 minutos)
                reset_time = getattr(e.response.headers, 'x-rate-limit-reset', None)
                if reset_time:
                    wait_time = min(int(reset_time) - int(time.time()), 900)  # Máximo 15 min
                    logger.info(f"⏳ Aguardando {wait_time}s para reset do rate limit...")
                    time.sleep(wait_time)
                else:
                    time.sleep(900)  # 15 minutos padrão
                
            except Exception as e:
                logger.error(f"❌ Erro na request: {e}")
                results['errors'] += 1
                results['requests_made'] += 1
                time.sleep(sleep_seconds)
        
        # Calcula estatísticas finais
        if results['successful_requests'] > 0:
            results['avg_response_time'] = results['total_response_time'] / results['successful_requests']
        
        results['end_time'] = datetime.now().isoformat()
        results['actual_duration'] = (datetime.now() - start_time).total_seconds() / 60
        results['success_rate'] = results['successful_requests'] / max(results['requests_made'], 1)
        results['requests_per_minute'] = results['successful_requests'] / results['actual_duration']
        
        logger.info(f"📊 Resultado: {results['successful_requests']}/{results['requests_made']} sucessos "
                   f"({results['success_rate']:.2%}), {results['requests_per_minute']:.1f} req/min")
        
        return results
    
    def run_comprehensive_test(self, test_intervals: List[int] = None) -> List[Dict]:
        """
        Executa teste abrangente com múltiplos intervalos
        """
        if test_intervals is None:
            test_intervals = [10, 15, 20, 30, 45, 60, 90, 120, 180]
        
        logger.info(f"🚀 Iniciando teste abrangente com intervalos: {test_intervals}")
        
        all_results = []
        
        for interval in test_intervals:
            try:
                result = self.test_single_interval(interval, test_duration_minutes=3)
                all_results.append(result)
                
                # Salva resultados parciais
                self.save_results(all_results, f"partial_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                
                # Pausa entre testes
                logger.info("😴 Pausa de 30s entre testes...")
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("⏹️  Teste interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no teste do intervalo {interval}s: {e}")
                continue
        
        return all_results
    
    def find_optimal_interval(self, results: List[Dict]) -> Dict:
        """
        Analisa resultados e encontra o intervalo ótimo
        """
        if not results:
            return {"error": "Nenhum resultado para analisar"}
        
        # Filtra apenas resultados com boa taxa de sucesso
        good_results = [r for r in results if r['success_rate'] >= 0.9]
        
        if not good_results:
            logger.warning("⚠️  Nenhum resultado com taxa de sucesso >= 90%")
            good_results = [r for r in results if r['success_rate'] >= 0.8]
        
        if not good_results:
            logger.error("❌ Nenhum resultado confiável encontrado")
            return {"error": "Nenhum resultado confiável"}
        
        # Encontra o menor intervalo com boa performance
        optimal = min(good_results, key=lambda x: x['sleep_seconds'])
        
        # Calcula estatísticas
        analysis = {
            'optimal_interval': optimal['sleep_seconds'],
            'optimal_success_rate': optimal['success_rate'],
            'optimal_requests_per_minute': optimal['requests_per_minute'],
            'optimal_avg_response_time': optimal['avg_response_time'],
            'total_tests': len(results),
            'reliable_tests': len(good_results),
            'recommendation': self.get_recommendation(optimal['sleep_seconds']),
            'all_results_summary': [
                {
                    'interval': r['sleep_seconds'],
                    'success_rate': r['success_rate'],
                    'req_per_min': r['requests_per_minute']
                }
                for r in sorted(results, key=lambda x: x['sleep_seconds'])
            ]
        }
        
        return analysis
    
    def get_recommendation(self, optimal_interval: int) -> str:
        """Gera recomendação baseada no intervalo ótimo"""
        if optimal_interval <= 20:
            return "AGRESSIVO - Use com cuidado, monitore rate limits"
        elif optimal_interval <= 60:
            return "BALANCEADO - Boa performance com segurança"
        elif optimal_interval <= 120:
            return "CONSERVADOR - Seguro mas mais lento"
        else:
            return "MUITO CONSERVADOR - Considere otimizar"
    
    def save_results(self, results: List[Dict], filename: str = None):
        """Salva resultados em arquivo JSON"""
        if filename is None:
            filename = f"rate_limit_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Resultados salvos em: {filename}")
    
    def generate_report(self, results: List[Dict], analysis: Dict):
        """Gera relatório detalhado"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE TESTE DE RATE LIMIT")
        print("="*60)
        
        print(f"\n🎯 RESULTADO ÓTIMO:")
        print(f"• Intervalo recomendado: {analysis['optimal_interval']}s")
        print(f"• Taxa de sucesso: {analysis['optimal_success_rate']:.2%}")
        print(f"• Requests por minuto: {analysis['optimal_requests_per_minute']:.1f}")
        print(f"• Tempo médio de resposta: {analysis['optimal_avg_response_time']:.2f}s")
        print(f"• Recomendação: {analysis['recommendation']}")
        
        print(f"\n📈 RESUMO DE TODOS OS TESTES:")
        print("Intervalo | Taxa Sucesso | Req/Min")
        print("-" * 35)
        for result in analysis['all_results_summary']:
            print(f"{result['interval']:8}s | {result['success_rate']:10.1%} | {result['req_per_min']:6.1f}")
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"• Total de testes: {analysis['total_tests']}")
        print(f"• Testes confiáveis: {analysis['reliable_tests']}")
        
        # Recomendações específicas
        print(f"\n💡 RECOMENDAÇÕES:")
        if analysis['optimal_interval'] <= 30:
            print("• ⚡ Performance alta detectada - use modo agressivo")
            print("• ⚠️  Monitore rate limits de perto")
            print("• 🔄 Execute testes regulares para ajustar")
        elif analysis['optimal_interval'] <= 90:
            print("• ⚖️  Configuração balanceada recomendada")
            print("• 📊 Boa relação performance/estabilidade")
            print("• 🔧 Pode otimizar gradualmente se necessário")
        else:
            print("• 🛡️  Configuração conservadora necessária")
            print("• 🔍 Verifique se há problemas de conectividade")
            print("• 📞 Considere contatar suporte da API")
    
    def create_visualization(self, results: List[Dict]):
        """Cria gráficos dos resultados"""
        try:
            import matplotlib.pyplot as plt
            
            # Prepara dados
            intervals = [r['sleep_seconds'] for r in results]
            success_rates = [r['success_rate'] * 100 for r in results]
            req_per_min = [r['requests_per_minute'] for r in results]
            
            # Cria gráfico
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Gráfico 1: Taxa de sucesso
            ax1.plot(intervals, success_rates, 'bo-', linewidth=2, markersize=8)
            ax1.set_xlabel('Intervalo de Sleep (segundos)')
            ax1.set_ylabel('Taxa de Sucesso (%)')
            ax1.set_title('Taxa de Sucesso vs Intervalo de Sleep')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 105)
            
            # Gráfico 2: Requests por minuto
            ax2.plot(intervals, req_per_min, 'ro-', linewidth=2, markersize=8)
            ax2.set_xlabel('Intervalo de Sleep (segundos)')
            ax2.set_ylabel('Requests por Minuto')
            ax2.set_title('Throughput vs Intervalo de Sleep')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Salva gráfico
            filename = f"rate_limit_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            logger.info(f"📈 Gráfico salvo em: {filename}")
            
            plt.show()
            
        except ImportError:
            logger.warning("⚠️  Matplotlib não disponível, pulando visualização")
        except Exception as e:
            logger.error(f"❌ Erro ao criar visualização: {e}")

def main():
    """Função principal"""
    print("🧪 TESTADOR DE RATE LIMIT - X.COM BOT")
    print("="*50)
    
    tester = RateLimitTester()
    
    # Menu de opções
    print("\nOpções de teste:")
    print("1. Teste rápido (intervalos: 15, 30, 60, 120s)")
    print("2. Teste completo (intervalos: 10-180s)")
    print("3. Teste personalizado")
    print("4. Teste de um intervalo específico")
    
    choice = input("\nEscolha uma opção (1-4): ").strip()
    
    if choice == "1":
        intervals = [15, 30, 60, 120]
        results = tester.run_comprehensive_test(intervals)
        
    elif choice == "2":
        intervals = [10, 15, 20, 30, 45, 60, 90, 120, 180]
        results = tester.run_comprehensive_test(intervals)
        
    elif choice == "3":
        intervals_input = input("Digite os intervalos separados por vírgula (ex: 10,20,30): ")
        try:
            intervals = [int(x.strip()) for x in intervals_input.split(',')]
            results = tester.run_comprehensive_test(intervals)
        except ValueError:
            print("❌ Formato inválido!")
            return
            
    elif choice == "4":
        try:
            interval = int(input("Digite o intervalo em segundos: "))
            duration = int(input("Digite a duração do teste em minutos (padrão 5): ") or "5")
            result = tester.test_single_interval(interval, duration)
            results = [result]
        except ValueError:
            print("❌ Valores inválidos!")
            return
    else:
        print("❌ Opção inválida!")
        return
    
    if results:
        # Analisa resultados
        analysis = tester.find_optimal_interval(results)
        
        if "error" not in analysis:
            # Gera relatório
            tester.generate_report(results, analysis)
            
            # Salva resultados
            tester.save_results(results)
            
            # Cria visualização
            create_viz = input("\nCriar gráficos? (s/n): ").lower().strip()
            if create_viz == 's':
                tester.create_visualization(results)
            
            print(f"\n🎉 RECOMENDAÇÃO FINAL:")
            print(f"Use intervalo de {analysis['optimal_interval']}s para performance ótima!")
            
        else:
            print(f"❌ {analysis['error']}")
    else:
        print("❌ Nenhum resultado obtido!")

if __name__ == "__main__":
    main()