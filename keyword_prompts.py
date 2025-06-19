# keyword_prompts.py
# VERSÃO ATUALIZADA PARA MONITORAR MÚLTIPLOS ALVOS

# =================================================================================
# 1. DEFINIÇÃO DOS USUÁRIOS-ALVO
# =================================================================================
# Agora usamos uma LISTA de IDs para monitorar várias contas ao mesmo tempo.
# Basta adicionar quantos IDs você quiser, entre aspas e separados por vírgula.

TARGET_USER_IDS = [
    "1473123053047529472",  # ID do perfil "pedrorouseff"
    "174518646",            # ID do perfil do @SomenteOrestes
    "31139434"               # ID do perfil do @gleisi
    # Adicione mais IDs aqui
]


# =================================================================================
# 2. DICIONÁRIO DE PROMPTS COM MÚLTIPLAS PALAVRAS-CHAVE (ALIASES)
# =================================================================================
# Esta parte não muda. O bot aplicará estas mesmas regras para todos os alvos.

prompts_com_aliases = {

    # --- TEMA BOLSONARO ---
    ("Bolsonaro", "Bozo"): {
        "prompt": "Aja como um comentarista cético e com um humor ácido. Seu objetivo é questionar a veracidade da informação no tweet: '{tweet_text}'. "
                  "Se o tweet parecer sensacionalista ou não citar fontes, questione a falta delas de forma irônica. "
                  "Seu tom deve ser zombador. Máximo de 150 caracteres."
    },

    # --- TEMA LULA ---
    ("Lula", "Lulinha"): {
        "prompt": "Aja como um comentarista cético e crítico. Analise o tweet: '{tweet_text}'. "
                  "Seu objetivo é questionar a validade da notícia. "
                  "Se for algo positivo sobre o governo, encontre um contraponto com dados ou fatos que mostrem uma perspectiva negativa ou um problema relacionado. "
                  "Mantenha um tom zombador. Use no máximo 180 caracteres."
    },
    
    # ... (o resto dos seus prompts continua aqui sem alteração) ...
    ("Dilma", "Dilminha", "Dilmãe"): {
        "prompt": "Analise o tweet: '{tweet_text}'. Se o post elogia a Dilma, responda com uma de suas famosas frases fora de contexto ou 'gafes' icônicas. "
                  "Seu comentário deve ser puramente uma citação dela, para soar absurdo e engraçado. "
                  "Exemplos: 'Não vamos colocar uma meta. Vamos deixar a meta aberta, mas, quando atingirmos a meta, vamos dobrar a meta.' ou 'Estocar vento'. "
                  "Seja curto e direto. Máximo de 150 caracteres."
    },
}