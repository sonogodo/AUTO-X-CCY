# bot.py
# VERSÃO 3.0 - USANDO A API DE STREAMING PARA EFICIÊNCIA MÁXIMA

import tweepy
import openai
import time
import os
import json
import requests

# 1. IMPORTAÇÕES E CONFIGURAÇÕES
from keys import *
from keyword_prompts import prompts_com_aliases, TARGET_USER_IDS, USER_ID_TO_NAME_MAP

print("Iniciando o bot com a API de Streaming...")

# Clientes das APIs
try:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    # O cliente do Tweepy precisa de todas as chaves para poder postar respostas
    tweepy_client_for_posting = tweepy.Client(
        bearer_token=X_BEARER_TOKEN, consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET, access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )
    print("Clientes de API inicializados com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO na inicialização: {e}")
    exit()

# Lógica para "achatar" os prompts
keyword_prompts = {}
for keywords_tuple, prompt_data in prompts_com_aliases.items():
    for keyword in keywords_tuple:
        keyword_prompts[keyword.lower()] = prompt_data
print(f"Configuração de prompts carregada. {len(keyword_prompts)} gatilhos ativos.")

# 2. FUNÇÃO DE GERAÇÃO DE COMENTÁRIO (Não muda)
def generate_comment(tweet_text, prompt_template):
    # Alterna o modelo de forma simples (pode ser aprimorado)
    model_name = "gpt-4o" if time.time() % 20 > 10 else "grok-1"
    print(f"   -> Usando modelo: {model_name}")
    try:
        if model_name.startswith("gpt"):
            response = openai_client.chat.completions.create(
                model=model_name, 
                messages=[
                    {"role": "system", "content": "Você é um assistente especialista em gerar comentários para a rede social X. Responda de forma concisa e natural."}, 
                    {"role": "user", "content": prompt_template.format(tweet_text=tweet_text)}
                ], 
                max_tokens=70, 
                temperature=0.75
            )
            return response.choices[0].message.content.strip()
        else:
            headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": model_name, 
                "messages": [
                    {"role": "system", "content": "Você é Grok. Gere comentários para o X que sejam concisos, inteligentes e com um toque de humor, conforme instruído."}, 
                    {"role": "user", "content": prompt_template.format(tweet_text=tweet_text)}
                ], 
                "max_tokens": 70, 
                "temperature": 0.75
            }
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"   ERRO: Falha ao gerar comentário com o modelo {model_name}. Detalhes: {e}")
        return None

# 3. A CLASSE DO STREAMING (O NOVO CORAÇÃO DO BOT)
class BotStreamer(tweepy.StreamingClient):
    def on_connect(self):
        print("Conectado com sucesso ao Stream do Twitter/X!")

    def on_error(self, status_code):
        print(f"Erro no Stream: {status_code}")
        # Desconecta se for um erro de autenticação
        if status_code == 401:
            return False

    def on_tweet(self, tweet):
        """
        Esta função é chamada AUTOMATICAMENTE toda vez que um tweet
        que corresponde às nossas regras é postado.
        """
        author_id = tweet.author_id
        username = USER_ID_TO_NAME_MAP.get(str(author_id), f"ID {author_id}")
        
        print("\n--- NOVO TWEET RECEBIDO ---")
        print(f"De: {username} (ID: {author_id})")
        print(f"Texto: {tweet.text}")

        # Verifica se alguma palavra-chave está no tweet
        for keyword, data in keyword_prompts.items():
            if keyword in tweet.text.lower():
                print(f"   -> Palavra-chave '{keyword}' encontrada!")
                
                comment = generate_comment(tweet.text, data["prompt"])
                
                if comment:
                    print(f"      Modelo gerou: '{comment}'")
                    try:
                        # Usa o cliente que criamos para postar a resposta
                        tweepy_client_for_posting.create_tweet(text=comment, in_reply_to_tweet_id=tweet.id)
                        print(f"      SUCESSO: Resposta postada ao tweet {tweet.id}!")
                    except tweepy.errors.TweepyException as e:
                        print(f"      ERRO: Falha ao postar a resposta no X. Detalhes: {e}")
                break # Para de procurar outras keywords no mesmo tweet

# 4. LÓGICA PRINCIPAL DE EXECUÇÃO
if __name__ == "__main__":
    # Inicializa o nosso streamer. Ele precisa do Bearer Token para ouvir o stream.
    streamer = BotStreamer(X_BEARER_TOKEN)

    # Limpa as regras antigas para garantir que estamos começando do zero
    rules = streamer.get_rules().data
    if rules:
        rule_ids = [rule.id for rule in rules]
        streamer.delete_rules(rule_ids)
        print("Regras antigas do stream foram limpas.")

    # Constrói a nova regra de filtragem
    # Formato: (palavra1 OR palavra2) (from:usuario1 OR from:usuario2)
    keyword_rule = f"({' OR '.join(keyword_prompts.keys())})"
    user_rule = f"({' OR '.join([f'from:{user_id}' for user_id in TARGET_USER_IDS])})"
    
    final_rule = f"{keyword_rule} {user_rule}"
    
    # Adiciona a nova regra ao stream do Twitter
    streamer.add_rules(tweepy.StreamRule(value=final_rule, tag="regra_principal"))
    print("\nNova regra do stream configurada:")
    print(f"-> {final_rule}")

    # Inicia o filtro. O código ficará aqui, ouvindo indefinidamente.
    print("\nOuvindo o stream de tweets... (Pressione Ctrl+C para parar)")
    streamer.filter(tweet_fields=["author_id"])