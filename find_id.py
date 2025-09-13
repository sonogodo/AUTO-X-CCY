import tweepy
# Importe suas chaves do seu arquivo de configuração
from keys import X_BEARER_TOKEN

# Peça o nome de usuário no terminal
username_to_find = input("")

# Verifique se o usuário digitou algo
if not username_to_find:
    print("Nenhum nome de usuário fornecido. Encerrando.")
else:
    try:
        # Autentique-se usando a V2 da API do X
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN)

        # Use a função get_user para buscar o usuário pelo username
        response = client.get_user(username=username_to_find)

        # Verifique se o usuário foi encontrado
        if response.data:
            user_object = response.data
            print("\n--- Informações Encontradas ---")
            print(f"Nome de Exibição: {user_object.name}")
            print(f"Nome de Usuário (@): {user_object.username}")
            print(f"ID do Usuário: {user_object.id}")
            print("---------------------------------")
            print("\nCopie o ID do Usuário para o seu arquivo 'keyword_prompts.py'")
        else:
            print(f"\nUsuário '{username_to_find}' não encontrado.")

    except Exception as e:
        print(f"Ocorreu um erro ao se comunicar com a API do X: {e}")