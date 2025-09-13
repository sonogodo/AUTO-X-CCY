# bot.py
# CÓDIGO ATUALIZADO PARA MONITORAR MÚLTIPLOS USUÁRIOS

import tweepy
import openai
import time
import os
import json # Importamos a biblioteca JSON

# 1. IMPORTAÇÃO DAS CONFIGURAÇÕES
from keys import *
# Agora importamos a LISTA de IDs
from keyword_prompts import prompts_com_aliases, TARGET_USER_IDS

# 2. CONFIGURAÇÃO E AUTENTICAÇÃO
print("Iniciando o bot multi-usuário...")
try:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    client_v2 = tweepy.Client(
        bearer_token=X_BEARER_TOKEN, consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET, access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )
    auth_v1 = tweepy.OAuth1UserHandler(
        consumer_key=X_API_KEY, consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_TOKEN_SECRET
    )
    api_v1 = tweepy.API(auth_v1)
    print("Autenticações realizadas com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO: Falha na autenticação. Detalhes: {e}")
    exit()

# Lógica para "achatar" os prompts
keyword_prompts = {}
for keywords_tuple, prompt_data in prompts_com_aliases.items():
    for keyword in keywords_tuple:
        keyword_prompts[keyword.lower()] = prompt_data
print(f"Configuração de prompts carregada. {len(keyword_prompts)} gatilhos ativos para {len(TARGET_USER_IDS)} alvos.")


# =================================================================================
# 3. NOVAS FUNÇÕES AUXILIARES PARA O ARQUIVO JSON
# =================================================================================
# Trocamos as funções antigas por estas, mais inteligentes.

def load_last_seen_ids():
    """Carrega o dicionário de últimos tweets vistos do arquivo JSON."""
    if os.path.exists("last_seen_ids.json"):
        with open("last_seen_ids.json", "r") as f:
            return json.load(f)
    return {} # Retorna um dicionário vazio se o arquivo não existir

def save_last_seen_ids(data):
    """Salva o dicionário de últimos tweets vistos no arquivo JSON."""
    with open("last_seen_ids.json", "w") as f:
        json.dump(data, f, indent=4) # indent=4 deixa o arquivo legível


# A função generate_comment continua a mesma
def generate_comment(tweet_text, prompt_template):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "system", "content": "Você é um assistente especialista em gerar comentários para a rede social X (Twitter). Responda de forma concisa, natural e dentro do limite de caracteres da plataforma."}, {"role": "user", "content": prompt_template.format(tweet_text=tweet_text)}], max_tokens=70, temperature=0.75
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERRO: Falha ao gerar comentário com o GPT. Detalhes: {e}")
        return None

# =================================================================================
# 4. LÓGICA PRINCIPAL DO BOT (ATUALIZADA COM O LOOP)
# =================================================================================
def check_and_reply():
    """
    Função principal atualizada para iterar sobre a lista de usuários-alvo.
    """
    # Carrega todos os IDs vistos de uma vez
    last_seen_ids = load_last_seen_ids()
    print("\nIniciando ciclo de verificação para todos os alvos...")

    # A grande mudança: um loop para passar por cada alvo da nossa lista
    for user_id in TARGET_USER_IDS:
        # Pega o último ID visto para ESTE usuário específico
        last_id = last_seen_ids.get(user_id)
        
        print(f"\n---> Verificando tweets de {user_id} (a partir do ID: {last_id})...")

        try:
            response = client_v2.get_users_tweets(id=user_id, since_id=last_id, max_results=5, tweet_fields=["created_at", "text"])
        except Exception as e:
            print(f"   ERRO: Não foi possível buscar os tweets de {user_id}. Detalhes: {e}")
            time.sleep(5) # Pequena pausa para não sobrecarregar a API em caso de erro
            continue # Pula para o próximo usuário da lista

        if not response.data:
            print(f"   Nenhum tweet novo encontrado para {user_id}.")
            time.sleep(5) # Pausa para ser gentil com a API
            continue

        newest_tweet_id_for_this_user = last_id if last_id else 0
        tweets_to_process = sorted(response.data, key=lambda x: x.created_at)

        for tweet in tweets_to_process:
            print(f"   Analisando tweet ID: {tweet.id} | Texto: {tweet.text}")
            if tweet.id > newest_tweet_id_for_this_user:
                newest_tweet_id_for_this_user = tweet.id

            for keyword, data in keyword_prompts.items():
                if keyword in tweet.text.lower():
                    print(f"   -> Palavra-chave '{keyword}' encontrada!")
                    comment = generate_comment(tweet.text, data["prompt"])
                    if comment:
                        print(f"      GPT Gerou: '{comment}'")
                        try:
                            api_v1.update_status(status=comment, in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True)
                            print(f"      SUCESSO: Resposta postada ao tweet {tweet.id}!")
                        except Exception as e:
                            print(f"      ERRO: Falha ao postar a resposta no X. Detalhes: {e}")
                    break
        
        # Atualiza o dicionário com o último ID visto para este usuário
        if newest_tweet_id_for_this_user > 0:
            last_seen_ids[user_id] = newest_tweet_id_for_this_user
        
        print(f"   Verificação para {user_id} completa.")
        time.sleep(5) # Pausa de 5 segundos entre a verificação de um usuário e outro para não irritar a API

    # Salva todos os IDs atualizados no arquivo JSON de uma só vez, no final do ciclo
    save_last_seen_ids(last_seen_ids)
    print("\nCiclo de verificação de todos os alvos concluído.")

# 5. LOOP DE EXECUÇÃO (if __name__ == "__main__":)
if __name__ == "__main__":
    # DICA: Você pode apagar o arquivo antigo "last_tweet_id.txt" se ele ainda existir.
    print("=========================================")
    print("   BOT DE RESPOSTAS MULTI-ALVO INICIADO")
    print("=========================================")
    while True:
        try:
            check_and_reply()
            print(f"\n--- Próxima verificação geral em 15 minutos (às {time.strftime('%H:%M:%S', time.localtime(time.time() + 900))}) ---")
            time.sleep(900)
        except KeyboardInterrupt:
            print("\nBot encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"ERRO INESPERADO no loop principal: {e}")
            print("Aguardando 15 minutos para tentar novamente...")
            time.sleep(900)