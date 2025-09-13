# fix_rate_limits.py
# SCRIPT PARA RESOLVER PROBLEMAS DE RATE LIMIT E CONFIGURAÇÃO

import tweepy
import time
import json
from datetime import datetime, timedelta
from keys import *

def check_rate_limit_status():
    """Verifica status detalhado dos rate limits"""
    print("📊 VERIFICANDO STATUS DOS RATE LIMITS")
    print("=" * 50)
    
    try:
        # Usa apenas Bearer Token para verificação básica
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN)
        
        # Tenta uma chamada simples
        me = client.get_me()
        print(f"✅ Conectado como: @{me.data.username}")
        
        print("\n⏳ Aguardando reset dos rate limits...")
        print("   (Rate limits do Twitter resetam a cada 15 minutos)")
        
        # Calcula próximo reset (aproximado)
        now = datetime.now()
        next_reset = now.replace(second=0, microsecond=0)
        
        # Rate limits resetam a cada 15 minutos
        minutes_to_add = 15 - (now.minute % 15)
        next_reset = next_reset + timedelta(minutes=minutes_to_add)
        
        print(f"   Próximo reset estimado: {next_reset.strftime('%H:%M:%S')}")
        
        wait_seconds = (next_reset - now).total_seconds()
        print(f"   Aguardar: {int(wait_seconds/60)} minutos e {int(wait_seconds%60)} segundos")
        
        return wait_seconds
        
    except tweepy.TooManyRequests as e:
        print("❌ Rate limit ainda ativo")
        
        # Tenta extrair tempo de reset dos headers
        if hasattr(e, 'response') and hasattr(e.response, 'headers'):
            reset_time = e.response.headers.get('x-rate-limit-reset')
            if reset_time:
                reset_datetime = datetime.fromtimestamp(int(reset_time))
                wait_seconds = (reset_datetime - datetime.now()).total_seconds()
                print(f"   Reset em: {reset_datetime.strftime('%H:%M:%S')}")
                print(f"   Aguardar: {int(wait_seconds/60)} minutos")
                return max(wait_seconds, 0)
        
        # Fallback: aguarda 15 minutos
        print("   Aguardando 15 minutos (padrão)")
        return 900
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 900

def wait_for_rate_limit_reset(wait_seconds):
    """Aguarda reset do rate limit com progresso"""
    if wait_seconds <= 0:
        print("✅ Rate limits já resetados")
        return
    
    print(f"\n⏳ Aguardando {int(wait_seconds/60)} minutos para reset...")
    
    # Aguarda em chunks de 1 minuto
    while wait_seconds > 0:
        minutes_left = int(wait_seconds / 60)
        seconds_left = int(wait_seconds % 60)
        
        print(f"   ⏰ Restam: {minutes_left:02d}:{seconds_left:02d}")
        
        # Aguarda 1 minuto ou o tempo restante
        sleep_time = min(60, wait_seconds)
        time.sleep(sleep_time)
        wait_seconds -= sleep_time
    
    print("✅ Tempo de espera concluído!")

def test_posting_after_reset():
    """Testa postagem após reset do rate limit"""
    print("\n🧪 TESTANDO POSTAGEM APÓS RESET")
    print("=" * 40)
    
    try:
        client = tweepy.Client(
            bearer_token=X_BEARER_TOKEN,
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_TOKEN_SECRET
        )
        
        # Testa busca primeiro
        me = client.get_me()
        print(f"✅ Busca funcionando: @{me.data.username}")
        
        # Pergunta se quer testar postagem
        test_post = input("❓ Testar postagem de tweet? (s/n): ").lower().strip()
        
        if test_post == 's':
            test_message = f"🤖 Teste pós rate-limit - {datetime.now().strftime('%H:%M:%S')}"
            
            response = client.create_tweet(text=test_message)
            print(f"✅ SUCESSO! Tweet postado: {response.data['id']}")
            
            # Oferece para deletar
            delete_test = input("❓ Deletar tweet de teste? (s/n): ").lower().strip()
            if delete_test == 's':
                client.delete_tweet(response.data['id'])
                print("✅ Tweet deletado")
        
        return True
        
    except Exception as e:
        print(f"❌ Ainda há problemas: {e}")
        return False

def create_conservative_bot_config():
    """Cria configuração conservadora para evitar rate limits"""
    config = {
        "sleep_between_users": 10,  # 10 segundos entre usuários
        "sleep_between_cycles": 300,  # 5 minutos entre ciclos
        "max_requests_per_cycle": 20,  # Máximo 20 requests por ciclo
        "max_responses_per_cycle": 3,  # Máximo 3 respostas por ciclo
        "enable_rate_limit_protection": True,
        "conservative_mode": True
    }
    
    with open("conservative_bot_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("📝 Configuração conservadora criada: conservative_bot_config.json")
    print("   • 10s entre usuários")
    print("   • 5 minutos entre ciclos")
    print("   • Máximo 20 requests por ciclo")
    print("   • Máximo 3 respostas por ciclo")

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE RATE LIMITS")
    print("=" * 50)
    
    # Verifica status atual
    wait_time = check_rate_limit_status()
    
    if wait_time > 60:  # Mais de 1 minuto
        print(f"\n⚠️  Rate limit ativo. Precisa aguardar {int(wait_time/60)} minutos.")
        
        wait_choice = input("❓ Aguardar automaticamente? (s/n): ").lower().strip()
        
        if wait_choice == 's':
            wait_for_rate_limit_reset(wait_time)
            
            # Testa após reset
            if test_posting_after_reset():
                print("\n🎉 PROBLEMA RESOLVIDO!")
                print("   O bot pode ser reiniciado normalmente.")
            else:
                print("\n❌ Ainda há problemas. Verifique as chaves de API.")
        else:
            print(f"\n⏰ Aguarde até {(datetime.now() + timedelta(seconds=wait_time)).strftime('%H:%M:%S')} e tente novamente.")
    
    else:
        print("\n✅ Rate limits OK, testando postagem...")
        if test_posting_after_reset():
            print("\n🎉 TUDO FUNCIONANDO!")
        else:
            print("\n❌ Há outros problemas além do rate limit.")
    
    # Cria configuração conservadora
    print(f"\n🛡️  Criando configuração conservadora para evitar futuros rate limits...")
    create_conservative_bot_config()
    
    print(f"\n💡 RECOMENDAÇÕES:")
    print("   1. Use intervalos maiores entre verificações (5+ minutos)")
    print("   2. Limite respostas por ciclo (máximo 3-5)")
    print("   3. Monitore logs para detectar rate limits cedo")
    print("   4. Use o bot simples (bot_simple_working.py) que é mais conservador")

if __name__ == "__main__":
    main()