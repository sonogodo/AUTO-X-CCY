# rate_limit_manager.py
# GERENCIADOR DE RATE LIMITS - SOLUÇÃO PARA CAPS ATINGIDOS

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

class RateLimitManager:
    def __init__(self):
        self.load_limits()
        self.current_usage = self.load_usage()
    
    def load_limits(self):
        """Carrega limites conhecidos da API do X"""
        self.limits = {
            "monthly_posts": 100,  # Seu limite atual
            "daily_posts": 10,     # Estimativa conservadora
            "hourly_posts": 5,     # Muito conservador
            "posts_per_15min": 2   # Extremamente conservador
        }
    
    def load_usage(self) -> Dict:
        """Carrega uso atual"""
        try:
            with open("rate_limit_usage.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "monthly_posts": 106,  # Você já usou 106
                "daily_posts": 0,
                "hourly_posts": 0,
                "last_reset_check": datetime.now().isoformat(),
                "next_monthly_reset": "2024-09-19T00:00:00"  # Seu reset
            }
    
    def save_usage(self):
        """Salva uso atual"""
        with open("rate_limit_usage.json", "w") as f:
            json.dump(self.current_usage, f, indent=2)
    
    def can_post(self) -> tuple[bool, str]:
        """Verifica se pode postar e retorna razão se não pode"""
        now = datetime.now()
        
        # Verifica se passou do reset mensal
        next_reset = datetime.fromisoformat(self.current_usage["next_monthly_reset"])
        if now >= next_reset:
            # Reset mensal aconteceu
            self.current_usage["monthly_posts"] = 0
            self.current_usage["daily_posts"] = 0
            self.current_usage["hourly_posts"] = 0
            
            # Próximo reset (assumindo mensal)
            next_month_reset = next_reset + timedelta(days=30)
            self.current_usage["next_monthly_reset"] = next_month_reset.isoformat()
            
            self.save_usage()
            return True, "Reset mensal aplicado"
        
        # Verifica limite mensal
        if self.current_usage["monthly_posts"] >= self.limits["monthly_posts"]:
            days_until_reset = (next_reset - now).days
            hours_until_reset = int((next_reset - now).total_seconds() / 3600)
            return False, f"Limite mensal atingido. Reset em {days_until_reset} dias ({hours_until_reset}h)"
        
        # Verifica limite diário (reset a cada 24h)
        last_check = datetime.fromisoformat(self.current_usage["last_reset_check"])
        if (now - last_check).total_seconds() >= 86400:  # 24 horas
            self.current_usage["daily_posts"] = 0
            self.current_usage["hourly_posts"] = 0
        
        if self.current_usage["daily_posts"] >= self.limits["daily_posts"]:
            return False, "Limite diário atingido"
        
        # Verifica limite horário
        if (now - last_check).total_seconds() >= 3600:  # 1 hora
            self.current_usage["hourly_posts"] = 0
        
        if self.current_usage["hourly_posts"] >= self.limits["hourly_posts"]:
            return False, "Limite horário atingido"
        
        return True, "OK para postar"
    
    def record_post(self):
        """Registra que um post foi feito"""
        self.current_usage["monthly_posts"] += 1
        self.current_usage["daily_posts"] += 1
        self.current_usage["hourly_posts"] += 1
        self.current_usage["last_reset_check"] = datetime.now().isoformat()
        self.save_usage()
    
    def get_status(self) -> Dict:
        """Retorna status atual dos limites"""
        now = datetime.now()
        next_reset = datetime.fromisoformat(self.current_usage["next_monthly_reset"])
        
        return {
            "monthly_usage": f"{self.current_usage['monthly_posts']}/{self.limits['monthly_posts']}",
            "daily_usage": f"{self.current_usage['daily_posts']}/{self.limits['daily_posts']}",
            "hourly_usage": f"{self.current_usage['hourly_posts']}/{self.limits['hourly_posts']}",
            "next_monthly_reset": next_reset.strftime("%Y-%m-%d %H:%M"),
            "days_until_reset": (next_reset - now).days,
            "hours_until_reset": int((next_reset - now).total_seconds() / 3600),
            "can_post_now": self.can_post()[0]
        }

def create_waiting_bot():
    """Cria um bot que aguarda o reset dos limites"""
    print("⏳ MODO DE ESPERA - AGUARDANDO RESET DOS LIMITES")
    print("=" * 50)
    
    manager = RateLimitManager()
    
    while True:
        status = manager.get_status()
        
        print(f"\n📊 STATUS ATUAL ({datetime.now().strftime('%H:%M:%S')}):")
        print(f"   Uso mensal: {status['monthly_usage']}")
        print(f"   Uso diário: {status['daily_usage']}")
        print(f"   Uso horário: {status['hourly_usage']}")
        print(f"   Reset em: {status['days_until_reset']} dias ({status['hours_until_reset']}h)")
        
        can_post, reason = manager.can_post()
        
        if can_post:
            print("🎉 LIMITES RESETADOS! Bot pode voltar a funcionar.")
            
            restart = input("❓ Iniciar bot automaticamente? (s/n): ").lower().strip()
            if restart == 's':
                print("🚀 Iniciando bot...")
                import subprocess
                import sys
                subprocess.run([sys.executable, "bot_simple_working.py"])
            break
        else:
            print(f"⏳ Aguardando: {reason}")
            
            # Aguarda 1 hora antes de verificar novamente
            print("😴 Verificando novamente em 1 hora...")
            time.sleep(3600)

def create_conservative_config():
    """Cria configuração ultra-conservadora para não estourar limites"""
    config = {
        "max_posts_per_day": 8,        # Bem abaixo do limite
        "max_posts_per_hour": 2,       # Muito conservador
        "sleep_between_cycles": 1800,  # 30 minutos entre ciclos
        "sleep_between_users": 30,     # 30 segundos entre usuários
        "max_responses_per_cycle": 1,  # Apenas 1 resposta por ciclo
        "enable_strict_limits": True,
        "priority_keywords": [         # Só responde a estas palavras-chave
            "bolsonaro", "lula", "economia"
        ]
    }
    
    with open("ultra_conservative_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("📝 Configuração ultra-conservadora criada!")
    print("   • Máximo 8 posts por dia")
    print("   • Máximo 2 posts por hora") 
    print("   • 30 minutos entre ciclos")
    print("   • Apenas 1 resposta por ciclo")
    print("   • Só palavras-chave prioritárias")

def show_reset_countdown():
    """Mostra countdown até o reset"""
    manager = RateLimitManager()
    
    print("⏰ COUNTDOWN PARA RESET DOS LIMITES")
    print("=" * 40)
    
    try:
        while True:
            status = manager.get_status()
            
            print(f"\r🕒 Reset em: {status['days_until_reset']} dias, {status['hours_until_reset'] % 24} horas", end="", flush=True)
            
            if status['days_until_reset'] <= 0 and status['hours_until_reset'] <= 0:
                print("\n🎉 RESET ACONTECEU! Limites renovados!")
                break
            
            time.sleep(60)  # Atualiza a cada minuto
            
    except KeyboardInterrupt:
        print("\n👋 Countdown interrompido")

def main():
    """Menu principal"""
    print("🚫 GERENCIADOR DE RATE LIMITS")
    print("=" * 40)
    print("Você atingiu o limite mensal de posts (106/100)")
    print("Reset previsto: 19 de Setembro às 00:00 UTC")
    print()
    
    while True:
        print("Opções:")
        print("1. 📊 Ver status atual dos limites")
        print("2. ⏳ Modo de espera (aguarda reset)")
        print("3. ⏰ Countdown até reset")
        print("4. 🛡️  Criar configuração conservadora")
        print("5. 🧪 Testar se limites resetaram")
        print("6. ❌ Sair")
        
        choice = input("\nEscolha (1-6): ").strip()
        
        if choice == "1":
            manager = RateLimitManager()
            status = manager.get_status()
            
            print(f"\n📊 STATUS DOS LIMITES:")
            for key, value in status.items():
                print(f"   {key}: {value}")
        
        elif choice == "2":
            create_waiting_bot()
            break
        
        elif choice == "3":
            show_reset_countdown()
        
        elif choice == "4":
            create_conservative_config()
        
        elif choice == "5":
            manager = RateLimitManager()
            can_post, reason = manager.can_post()
            
            if can_post:
                print("✅ Limites OK! Bot pode funcionar.")
            else:
                print(f"❌ Ainda limitado: {reason}")
        
        elif choice == "6":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()