# bot_simple_working.py
# BOT SIMPLES E FUNCIONAL - VERSÃO QUE FUNCIONA GARANTIDO

import tweepy
import openai
import requests
import time
import json
import os
from datetime import datetime

# Importações locais
from keys import *
from keyword_prompts import prompts_com_aliases, TARGET_USER_IDS, USER_ID_TO_NAME_MAP

print("🚀 Iniciando Bot Simples e Funcional...")

# Configuração dos clientes
try:
    # Cliente OpenAI
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    # Cliente Twitter/X (apenas o que funciona)
    client = tweepy.Client(
        bearer_token=X_BEARER_TOKEN,
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    
    print("✅ Clientes configurados com sucesso")
    
except Exception as e:
    print(f"❌ Erro na configuração: {e}")
    exit()

# Prepara prompts
keyword_prompts = {}
for keywords_tuple, prompt_data in prompts_com_aliases.items():
    for keyword in keywords_tuple:
        keyword_prompts[keyword.lower()] = prompt_data

print(f"📝 {len(keyword_prompts)} palavras-chave carregadas")

# Carrega último ID visto
def load_last_ids():
    try:
        with open("simple_bot_ids.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_last_ids(ids):
    with open("simple_bot_ids.json", "w") as f:
        json.dump(ids, f, indent=2)

# Gera comentário
def generate_comment(tweet_text, prompt_template):
    try:
        # Usa sempre GPT-4o-mini para economizar
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente que gera comentários concisos para Twitter/X. Seja direto e relevante."},
                {"role": "user", "content": prompt_template.format(tweet_text=tweet_text)}
            ],
            max_tokens=60,
            temperature=0.7
        )
        
        comment = response.choices[0].message.content.strip()
        print(f"💬 Comentário gerado: {comment[:50]}...")
        return comment
        
    except Exception as e:
        print(f"❌ Erro ao gerar comentário: {e}")
        return None

# Função principal
def check_and_reply():
    print(f"\n🔍 Verificando tweets... {datetime.now().strftime('%H:%M:%S')}")
    
    last_ids = load_last_ids()
    responses_sent = 0
    
    for user_id in TARGET_USER_IDS:
        username = USER_ID_TO_NAME_MAP.get(user_id, f"ID:{user_id}")
        last_id = last_ids.get(user_id)
        
        try:
            print(f"👤 Verificando {username}...")
            
            # Busca tweets recentes
            tweets = client.get_users_tweets(
                id=user_id,
                since_id=last_id,
                max_results=5,
                tweet_fields=["created_at"]
            )
            
            if not tweets.data:
                print(f"   📭 Nenhum tweet novo")
                continue
            
            # Processa tweets
            for tweet in tweets.data:
                # Atualiza último ID
                last_ids[user_id] = max(last_ids.get(user_id, 0), int(tweet.id))
                
                print(f"   📝 Tweet: {tweet.text[:50]}...")
                
                # Verifica palavras-chave
                found_keyword = None
                for keyword in keyword_prompts.keys():
                    if keyword in tweet.text.lower():
                        found_keyword = keyword
                        break
                
                if found_keyword:
                    print(f"   🎯 Palavra-chave encontrada: {found_keyword}")
                    
                    # Gera resposta
                    comment = generate_comment(tweet.text, keyword_prompts[found_keyword]["prompt"])
                    
                    if comment:
                        try:
                            # Posta resposta
                            client.create_tweet(
                                text=comment,
                                in_reply_to_tweet_id=tweet.id
                            )
                            
                            print(f"   ✅ RESPOSTA POSTADA!")
                            responses_sent += 1
                            
                            # Pausa entre respostas
                            time.sleep(5)
                            
                        except Exception as e:
                            print(f"   ❌ Erro ao postar: {e}")
                else:
                    print(f"   ⏭️  Nenhuma palavra-chave encontrada")
            
            # Pausa entre usuários
            time.sleep(3)
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {username}: {e}")
            continue
    
    # Salva IDs atualizados
    save_last_ids(last_ids)
    
    print(f"✅ Ciclo completo: {responses_sent} respostas enviadas")
    return responses_sent

# Loop principal
if __name__ == "__main__":
    print("🤖 BOT SIMPLES INICIADO")
    print("=" * 40)
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            print(f"\n🔄 CICLO {cycle_count}")
            
            # Executa verificação
            responses = check_and_reply()
            
            # Próxima verificação em 2 minutos
            next_check = datetime.now()
            next_check = next_check.replace(second=0, microsecond=0)
            next_check = next_check.replace(minute=next_check.minute + 2)
            
            print(f"😴 Próxima verificação às {next_check.strftime('%H:%M:%S')}")
            time.sleep(120)  # 2 minutos
            
        except KeyboardInterrupt:
            print("\n👋 Bot encerrado pelo usuário")
            break
            
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("⏳ Aguardando 5 minutos antes de tentar novamente...")
            time.sleep(300)