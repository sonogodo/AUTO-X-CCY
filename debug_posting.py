# debug_posting.py
# SCRIPT PARA DEBUGAR PROBLEMAS DE POSTAGEM

import tweepy
import openai
import json
from datetime import datetime
from keys import *

def test_twitter_posting():
    """Testa se consegue postar no Twitter"""
    print("🔧 TESTE DE POSTAGEM NO TWITTER")
    print("=" * 40)
    
    try:
        # Configura cliente
        client = tweepy.Client(
            bearer_token=X_BEARER_TOKEN,
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_TOKEN_SECRET
        )
        
        print("✅ Cliente configurado")
        
        # Testa conexão básica
        me = client.get_me()
        print(f"✅ Conectado como: @{me.data.username}")
        
        # Testa busca de tweets
        print("\n🔍 Testando busca de tweets...")
        tweets = client.get_users_tweets(id=me.data.id, max_results=5)
        
        if tweets.data:
            print(f"✅ Encontrados {len(tweets.data)} tweets")
            latest_tweet = tweets.data[0]
            print(f"   Último tweet: {latest_tweet.text[:50]}...")
            
            # Pergunta se quer testar resposta
            test_reply = input("\n❓ Testar postagem de resposta? (s/n): ").lower().strip()
            
            if test_reply == 's':
                test_message = f"🤖 Teste de bot - {datetime.now().strftime('%H:%M:%S')}"
                
                try:
                    response = client.create_tweet(
                        text=test_message,
                        in_reply_to_tweet_id=latest_tweet.id
                    )
                    
                    print(f"✅ SUCESSO! Tweet de teste postado: {response.data['id']}")
                    
                    # Pergunta se quer deletar
                    delete_test = input("❓ Deletar tweet de teste? (s/n): ").lower().strip()
                    if delete_test == 's':
                        try:
                            client.delete_tweet(response.data['id'])
                            print("✅ Tweet de teste deletado")
                        except Exception as e:
                            print(f"⚠️  Não foi possível deletar: {e}")
                    
                except Exception as e:
                    print(f"❌ ERRO ao postar resposta: {e}")
                    print(f"   Tipo do erro: {type(e).__name__}")
                    
                    if hasattr(e, 'response'):
                        print(f"   Status code: {e.response.status_code}")
                        print(f"   Response: {e.response.text}")
            
        else:
            print("❌ Nenhum tweet encontrado")
            
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        print(f"   Tipo: {type(e).__name__}")
        return False
    
    return True

def test_openai_generation():
    """Testa geração de comentários com OpenAI"""
    print("\n🧠 TESTE DE GERAÇÃO DE COMENTÁRIOS")
    print("=" * 40)
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        test_tweet = "A economia brasileira está crescendo este ano."
        test_prompt = "Analise criticamente: '{tweet_text}'. Questione fontes se necessário. Max 100 chars."
        
        print(f"Tweet de teste: {test_tweet}")
        print(f"Prompt: {test_prompt}")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você gera comentários concisos para Twitter."},
                {"role": "user", "content": test_prompt.format(tweet_text=test_tweet)}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        comment = response.choices[0].message.content.strip()
        print(f"✅ Comentário gerado: '{comment}'")
        print(f"   Tokens usados: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO na geração: {e}")
        return False

def check_rate_limits():
    """Verifica status dos rate limits"""
    print("\n📊 VERIFICAÇÃO DE RATE LIMITS")
    print("=" * 40)
    
    try:
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN)
        
        # Faz uma chamada para obter headers
        response = client.get_me()
        
        # Tenta extrair rate limit info
        if hasattr(response, 'meta') and hasattr(response.meta, 'headers'):
            headers = response.meta.headers
            
            limit = headers.get('x-rate-limit-limit', 'N/A')
            remaining = headers.get('x-rate-limit-remaining', 'N/A')
            reset = headers.get('x-rate-limit-reset', 'N/A')
            
            print(f"Rate Limit: {remaining}/{limit}")
            
            if reset != 'N/A':
                reset_time = datetime.fromtimestamp(int(reset))
                print(f"Reset em: {reset_time.strftime('%H:%M:%S')}")
            
            if remaining != 'N/A' and int(remaining) < 10:
                print("⚠️  ATENÇÃO: Poucas requests restantes!")
            else:
                print("✅ Rate limits OK")
        else:
            print("⚠️  Não foi possível obter informações de rate limit")
            
    except Exception as e:
        print(f"❌ Erro ao verificar rate limits: {e}")

def check_keywords_and_targets():
    """Verifica configuração de palavras-chave e targets"""
    print("\n🎯 VERIFICAÇÃO DE CONFIGURAÇÃO")
    print("=" * 40)
    
    try:
        from keyword_prompts import prompts_com_aliases, TARGET_USER_IDS, USER_ID_TO_NAME_MAP
        
        # Conta palavras-chave
        total_keywords = 0
        for keywords_tuple in prompts_com_aliases.keys():
            total_keywords += len(keywords_tuple)
        
        print(f"✅ {len(prompts_com_aliases)} grupos de prompts")
        print(f"✅ {total_keywords} palavras-chave total")
        print(f"✅ {len(TARGET_USER_IDS)} usuários monitorados")
        
        # Mostra alguns exemplos
        print(f"\nPrimeiras palavras-chave:")
        count = 0
        for keywords_tuple in prompts_com_aliases.keys():
            for keyword in keywords_tuple:
                if count < 5:
                    print(f"   • {keyword}")
                    count += 1
        
        print(f"\nPrimeiros usuários:")
        for i, user_id in enumerate(TARGET_USER_IDS[:5]):
            username = USER_ID_TO_NAME_MAP.get(user_id, f"ID:{user_id}")
            print(f"   • {username}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")

def main():
    """Executa todos os testes"""
    print("🔧 DIAGNÓSTICO COMPLETO DO BOT")
    print("=" * 50)
    
    # Testa cada componente
    twitter_ok = test_twitter_posting()
    openai_ok = test_openai_generation()
    
    check_rate_limits()
    check_keywords_and_targets()
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DO DIAGNÓSTICO")
    print("=" * 50)
    
    if twitter_ok and openai_ok:
        print("🎉 TUDO FUNCIONANDO!")
        print("   O bot deveria estar postando normalmente.")
        print("\n💡 Se não está postando, pode ser:")
        print("   • Nenhum tweet novo com palavras-chave")
        print("   • Rate limits atingidos")
        print("   • Tweets já processados anteriormente")
    else:
        print("❌ PROBLEMAS DETECTADOS:")
        if not twitter_ok:
            print("   • Problema com postagem no Twitter")
        if not openai_ok:
            print("   • Problema com geração de comentários")
    
    print(f"\n🕒 Diagnóstico concluído às {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()