# keyword_prompts.py
# VERSÃO ATUALIZADA COM MAPEAMENTO DE ID PARA USERNAME

# =================================================================================
# 1. DEFINIÇÃO DOS USUÁRIOS-ALVO
# =================================================================================
# A lista de IDs que o bot deve monitorar.
TARGET_USER_IDS = [
    "1473123053047529472",  # @pedrorouseff
    "174518646",            # @SomenteOrestes
    "31139434",             # @gleisi
    "54341363",             # @JornalOGlobo
    "8802752",              # @Jg1
    "1875980871746179072",  # @analise2025
    "206222507",            # @zehdeabreu
    "248890506",            # @brasil247
    "63118359",             # @mariadorosario
    "22864100",             # @pimenta13br
    "1563897907446747136",  # @_Janoninho
    "4550317786",           # @DilmaResiste
    "131574396",            # @dilmabr
    "1652708826980794369",  # @solangealvvs
    "1004511711251099653",  # @DudaSalabert
    "1802012191270338561",  # @Mandsfra25
    "888811861814247424",   # @CatarinaAguiar1
    "14594813",             # @folha
    "16794066"              # @blogdonoblat
]

# NOVO DICIONÁRIO: Mapa de ID para @Username para logs mais legíveis
USER_ID_TO_NAME_MAP = {
    "1473123053047529472": "@pedrorouseff",
    "174518646": "@SomenteOrestes",
    "31139434": "@gleisi",
    "54341363": "@JornalOGlobo",
    "8802752": "@Jg1",
    "1875980871746179072": "@analise2025",
    "206222507": "@zehdeabreu",
    "248890506": "@brasil247",
    "63118359": "@mariadorosario",
    "22864100": "@pimenta13br",
    "1563897907446747136": "@_Janoninho",
    "4550317786": "@DilmaResiste",
    "131574396": "@dilmabr",
    "1652708826980794369": "@solangealvvs",
    "1004511711251099653": "@DudaSalabert",
    "1802012191270338561": "@Mandsfra25",
    "888811861814247424": "@CatarinaAguiar1",
    "14594813": "@folha",
    "16794066": "@blogdonoblat"
}




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

    # --- TEMA Nikolas ---
    ("Nikolas", "Nikolas Ferreira"): {
        "prompt": "Aja como um comentarista cético e com um humor ácido. Seu objetivo é questionar a veracidade da informação no tweet: '{tweet_text}'. "
                  "Se o tweet parecer sensacionalista ou não citar fontes, questione a falta delas de forma irônica. "
                  "Seu tom deve ser zombador. Máximo de 180 caracteres."
    },
    
    # ... (o resto dos seus prompts continua aqui sem alteração) ...
    ("Dilma", "Dilminha", "Dilmãe"): {
        "prompt": "Analise o tweet: '{tweet_text}'. Se o post elogia a Dilma, responda com uma de suas famosas frases fora de contexto ou 'gafes' icônicas. "
                  "Seu comentário deve ser puramente uma citação dela, para soar absurdo e engraçado. "
                  "Exemplos: 'Não vamos colocar uma meta. Vamos deixar a meta aberta, mas, quando atingirmos a meta, vamos dobrar a meta.' ou 'Estocar vento'. "
                  "Seja curto e direto. Máximo de 150 caracteres."
    },
}