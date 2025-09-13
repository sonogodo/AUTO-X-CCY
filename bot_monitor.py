# bot_monitor.py
# SISTEMA DE MONITORAMENTO E ANÁLISE DO BOT

import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import os

class BotMonitor:
    def __init__(self):
        self.stats_file = "bot_stats.json"
        self.load_stats()
    
    def load_stats(self):
        """Carrega estatísticas do bot"""
        try:
            with open(self.stats_file, "r") as f:
                self.stats = json.load(f)
        except FileNotFoundError:
            self.stats = self.create_empty_stats()
    
    def create_empty_stats(self):
        """Cria estrutura vazia de estatísticas"""
        return {
            "tweets_processed": 0,
            "responses_sent": 0,
            "tokens_used": 0,
            "last_reset": datetime.now().isoformat(),
            "daily_responses": {},
            "keyword_stats": {},
            "model_usage": {},
            "error_log": [],
            "performance_metrics": {
                "avg_response_time": 0,
                "success_rate": 0,
                "token_efficiency": 0
            }
        }
    
    def generate_report(self) -> str:
        """Gera relatório detalhado do bot"""
        report = []
        report.append("=" * 50)
        report.append("RELATÓRIO DO BOT X.COM")
        report.append("=" * 50)
        
        # Estatísticas gerais
        report.append(f"\n📊 ESTATÍSTICAS GERAIS:")
        report.append(f"• Tweets processados: {self.stats['tweets_processed']:,}")
        report.append(f"• Respostas enviadas: {self.stats['responses_sent']:,}")
        report.append(f"• Tokens utilizados: {self.stats['tokens_used']:,}")
        
        # Taxa de sucesso
        if self.stats['tweets_processed'] > 0:
            success_rate = (self.stats['responses_sent'] / self.stats['tweets_processed']) * 100
            report.append(f"• Taxa de resposta: {success_rate:.1f}%")
        
        # Eficiência de tokens
        if self.stats['responses_sent'] > 0:
            tokens_per_response = self.stats['tokens_used'] / self.stats['responses_sent']
            report.append(f"• Tokens por resposta: {tokens_per_response:.1f}")
        
        # Atividade diária
        report.append(f"\n📅 ATIVIDADE DOS ÚLTIMOS 7 DIAS:")
        daily_data = self.get_last_7_days_activity()
        for date, count in daily_data.items():
            report.append(f"• {date}: {count} respostas")
        
        # Top keywords
        report.append(f"\n🔥 PALAVRAS-CHAVE MAIS ATIVAS:")
        top_keywords = self.get_top_keywords(5)
        for keyword, count in top_keywords:
            report.append(f"• {keyword}: {count} ativações")
        
        # Uso de modelos
        report.append(f"\n🤖 USO DE MODELOS IA:")
        for model, count in self.stats.get('model_usage', {}).items():
            report.append(f"• {model}: {count} usos")
        
        # Erros recentes
        recent_errors = self.get_recent_errors(5)
        if recent_errors:
            report.append(f"\n⚠️  ERROS RECENTES:")
            for error in recent_errors:
                report.append(f"• {error['timestamp']}: {error['message']}")
        
        return "\n".join(report)
    
    def get_last_7_days_activity(self) -> Dict[str, int]:
        """Retorna atividade dos últimos 7 dias"""
        today = datetime.now().date()
        activity = {}
        
        for i in range(7):
            date = today - timedelta(days=i)
            date_str = date.isoformat()
            
            # Soma todas as respostas deste dia
            daily_count = 0
            for key, count in self.stats.get('daily_responses', {}).items():
                if date_str in key:
                    daily_count += count
            
            activity[date_str] = daily_count
        
        return activity
    
    def get_top_keywords(self, limit: int = 10) -> List[tuple]:
        """Retorna as palavras-chave mais ativas"""
        keyword_stats = self.stats.get('keyword_stats', {})
        sorted_keywords = sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:limit]
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Retorna erros recentes"""
        errors = self.stats.get('error_log', [])
        return errors[-limit:] if errors else []
    
    def calculate_token_efficiency(self) -> float:
        """Calcula eficiência de uso de tokens"""
        if self.stats['responses_sent'] == 0:
            return 0
        
        return self.stats['tokens_used'] / self.stats['responses_sent']
    
    def suggest_optimizations(self) -> List[str]:
        """Sugere otimizações baseadas nas estatísticas"""
        suggestions = []
        
        # Verifica eficiência de tokens
        token_efficiency = self.calculate_token_efficiency()
        if token_efficiency > 80:
            suggestions.append("🔧 Considere usar modelos menores ou reduzir max_tokens")
        
        # Verifica taxa de resposta
        if self.stats['tweets_processed'] > 0:
            response_rate = (self.stats['responses_sent'] / self.stats['tweets_processed']) * 100
            if response_rate < 10:
                suggestions.append("📈 Taxa de resposta baixa - considere expandir palavras-chave")
            elif response_rate > 50:
                suggestions.append("⚡ Taxa de resposta alta - considere filtros mais rigorosos")
        
        # Verifica uso de modelos
        model_usage = self.stats.get('model_usage', {})
        if model_usage:
            total_uses = sum(model_usage.values())
            gpt4_usage = model_usage.get('gpt-4o', 0) / total_uses * 100 if total_uses > 0 else 0
            if gpt4_usage > 70:
                suggestions.append("💰 Uso alto do GPT-4 - considere usar gpt-4o-mini para temas simples")
        
        # Verifica erros
        recent_errors = self.get_recent_errors(10)
        if len(recent_errors) > 5:
            suggestions.append("🚨 Muitos erros recentes - verifique configurações da API")
        
        return suggestions
    
    def export_data_for_analysis(self, filename: str = "bot_data_export.json"):
        """Exporta dados para análise externa"""
        export_data = {
            "export_date": datetime.now().isoformat(),
            "stats": self.stats,
            "summary": {
                "total_tweets_processed": self.stats['tweets_processed'],
                "total_responses_sent": self.stats['responses_sent'],
                "total_tokens_used": self.stats['tokens_used'],
                "token_efficiency": self.calculate_token_efficiency(),
                "top_keywords": self.get_top_keywords(10),
                "last_7_days": self.get_last_7_days_activity()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Dados exportados para {filename}")
    
    def reset_daily_stats(self):
        """Reseta estatísticas diárias (para executar à meia-noite)"""
        today = datetime.now().date().isoformat()
        
        # Limpa dados antigos (mais de 30 dias)
        cutoff_date = datetime.now() - timedelta(days=30)
        
        if 'daily_responses' in self.stats:
            old_keys = [
                key for key in self.stats['daily_responses'].keys()
                if datetime.fromisoformat(key.split('_')[1]).date() < cutoff_date.date()
            ]
            for key in old_keys:
                del self.stats['daily_responses'][key]
        
        # Salva estatísticas
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        print(f"🔄 Estatísticas diárias resetadas para {today}")

def main():
    """Função principal para executar relatórios"""
    monitor = BotMonitor()
    
    print(monitor.generate_report())
    print("\n" + "=" * 50)
    
    # Sugestões de otimização
    suggestions = monitor.suggest_optimizations()
    if suggestions:
        print("\n💡 SUGESTÕES DE OTIMIZAÇÃO:")
        for suggestion in suggestions:
            print(f"  {suggestion}")
    else:
        print("\n✅ Bot funcionando de forma otimizada!")
    
    # Pergunta se quer exportar dados
    export = input("\n📊 Exportar dados para análise? (s/n): ").lower().strip()
    if export == 's':
        monitor.export_data_for_analysis()

if __name__ == "__main__":
    main()