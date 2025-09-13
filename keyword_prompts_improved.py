# keyword_prompts_improved.py
# VERSÃO MELHORADA COM PROMPTS MAIS INTELIGENTES E ECONOMIA DE TOKENS

# =================================================================================
# 1. DEFINIÇÃO DOS USUÁRIOS-ALVO (Mantido igual)
# =================================================================================
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
# 2. PROMPTS INTELIGENTES COM METADADOS PARA ECONOMIA DE TOKENS
# =================================================================================

prompts_com_aliases = {
    # --- POLÍTICOS PRINCIPAIS ---
    ("bolsonaro", "bozo", "jair", "capitão", "ex-presidente"): {
        "prompt": "Sobre '{tweet_text}': Questione fontes se necessário. Tom crítico mas factual. Máx 130 chars.",
        "priority": "high",
        "cooldown_minutes": 30,
        "max_daily_responses": 5
    },

    ("lula", "lulinha", "presidente lula", "luiz inácio"): {
        "prompt": "Analisando '{tweet_text}': Peça dados oficiais ou ofereça contraponto baseado em fatos. Tom equilibrado. Máx 130 chars.",
        "priority": "high",
        "cooldown_minutes": 30,
        "max_daily_responses": 5
    },

    ("dilma", "dilminha", "dilmãe", "presidenta"): {
        "prompt": "'{tweet_text}' - Responda apenas com uma frase icônica da Dilma contextualmente engraçada. Só a citação. Máx 100 chars.",
        "priority": "low",
        "cooldown_minutes": 60,
        "max_daily_responses": 2
    },

    # --- TEMAS ECONÔMICOS (ALTA PRIORIDADE) ---
    ("economia", "inflação", "pib", "desemprego", "dólar", "real", "juros"): {
        "prompt": "Dados econômicos: '{tweet_text}'. Peça fonte oficial (IBGE, BC) ou contextualize historicamente. Tom técnico. Máx 140 chars.",
        "priority": "high",
        "cooldown_minutes": 20,
        "max_daily_responses": 8
    },

    ("auxílio", "bolsa família", "benefício", "social"): {
        "prompt": "Programa social: '{tweet_text}'. Compare com dados oficiais ou peça evidências. Tom construtivo. Máx 130 chars.",
        "priority": "medium",
        "cooldown_minutes": 40,
        "max_daily_responses": 4
    },

    # --- FAKE NEWS E DESINFORMAÇÃO (PRIORIDADE MÁXIMA) ---
    ("fake news", "mentira", "desinformação", "falso", "boato"): {
        "prompt": "Possível desinformação: '{tweet_text}'. Peça fontes confiáveis e sugira fact-checking. Tom educativo. Máx 120 chars.",
        "priority": "critical",
        "cooldown_minutes": 10,
        "max_daily_responses": 10
    },

    # --- INSTITUIÇÕES E DEMOCRACIA ---
    ("stf", "supremo", "moraes", "judiciário"): {
        "prompt": "Sobre Judiciário: '{tweet_text}'. Defenda independência dos poderes e Estado de Direito. Tom institucional. Máx 130 chars.",
        "priority": "high",
        "cooldown_minutes": 25,
        "max_daily_responses": 6
    },

    ("eleição", "urna", "voto", "tse", "democracia"): {
        "prompt": "Sistema eleitoral: '{tweet_text}'. Defenda transparência e confiabilidade das urnas com dados do TSE. Máx 130 chars.",
        "priority": "critical",
        "cooldown_minutes": 15,
        "max_daily_responses": 8
    },

    # --- CORRUPÇÃO E INVESTIGAÇÕES ---
    ("corrupção", "propina", "lava jato", "investigação", "pf"): {
        "prompt": "Investigação: '{tweet_text}'. Lembre presunção de inocência e peça fontes oficiais (PF, MPF). Tom jurídico. Máx 130 chars.",
        "priority": "medium",
        "cooldown_minutes": 45,
        "max_daily_responses": 4
    },

    # --- SAÚDE E EDUCAÇÃO ---
    ("sus", "saúde", "hospital", "médico", "vacina"): {
        "prompt": "Saúde pública: '{tweet_text}'. Cite dados do Ministério da Saúde ou estudos científicos. Tom técnico. Máx 130 chars.",
        "priority": "medium",
        "cooldown_minutes": 35,
        "max_daily_responses": 5
    },

    ("educação", "universidade", "escola", "professor", "mec"): {
        "prompt": "Educação: '{tweet_text}'. Compare com dados do MEC/INEP ou estudos educacionais. Tom construtivo. Máx 130 chars.",
        "priority": "medium",
        "cooldown_minutes": 40,
        "max_daily_responses": 4
    },

    # --- MEIO AMBIENTE ---
    ("amazônia", "desmatamento", "clima", "ambiental", "ibama"): {
        "prompt": "Meio ambiente: '{tweet_text}'. Cite dados do INPE/IBAMA ou estudos científicos. Tom urgente mas factual. Máx 130 chars.",
        "priority": "medium",
        "cooldown_minutes": 30,
        "max_daily_responses": 5
    },

    # --- SEGURANÇA ---
    ("violência", "crime", "segurança", "polícia", "homicídio"): {
        "prompt": "Segurança: '{tweet_text}'. Peça dados oficiais (SSP, FBSP) ou contextualize estatisticamente. Tom sério. Máx 130 chars.",
        "priority": "medium",
        "cooldown_minutes": 45,
        "max_daily_responses": 3
    },

    # --- MÍDIA E COMUNICAÇÃO ---
    ("imprensa", "jornalismo", "mídia", "censura", "liberdade"): {
        "prompt": "Liberdade de imprensa: '{tweet_text}'. Defenda transparência e pluralidade informativa. Tom democrático. Máx 130 chars.",
        "priority": "medium",
        "cooldown_minutes": 50,
        "max_daily_responses": 3
    },

    # --- TECNOLOGIA E REDES SOCIAIS ---
    ("twitter", "x", "facebook", "instagram", "rede social"): {
        "prompt": "Redes sociais: '{tweet_text}'. Questione algoritmos ou peça transparência nas políticas. Tom tech. Máx 120 chars.",
        "priority": "low",
        "cooldown_minutes": 60,
        "max_daily_responses": 2
    }
}

# =================================================================================
# 3. CONFIGURAÇÕES INTELIGENTES DO BOT
# =================================================================================

BOT_CONFIG = {
    # Limites globais para economia de tokens
    "max_responses_per_hour": 15,
    "max_responses_per_day": 100,
    "max_tokens_per_day": 5000,
    
    # Filtros de qualidade
    "min_tweet_length": 20,
    "max_hashtags_allowed": 5,
    "max_mentions_allowed": 3,
    
    # Configurações de modelo
    "default_model": "gpt-4o-mini",  # Modelo mais barato como padrão
    "premium_model": "gpt-4o",       # Para temas críticos
    "fallback_model": "grok-1",      # Backup
    
    # Horários de maior atividade (para ajustar frequência)
    "peak_hours": [7, 8, 9, 12, 13, 18, 19, 20, 21],
    "off_peak_multiplier": 1.5,  # Aumenta intervalo fora do pico
    
    # Blacklist de palavras (não responder)
    "blacklist_keywords": [
        "suicídio", "morte", "funeral", "luto", 
        "criança", "menor", "adolescente",
        "estupro", "abuso", "violência sexual"
    ]
}

# =================================================================================
# 4. FUNÇÕES AUXILIARES PARA O BOT INTELIGENTE
# =================================================================================

def get_prompt_priority(keyword: str) -> str:
    """Retorna a prioridade do prompt baseado na palavra-chave"""
    for keywords, data in prompts_com_aliases.items():
        if keyword.lower() in [k.lower() for k in keywords]:
            return data.get("priority", "low")
    return "low"

def should_use_premium_model(tweet_text: str, keyword: str) -> bool:
    """Decide se deve usar modelo premium baseado no contexto"""
    priority = get_prompt_priority(keyword)
    
    # Usa modelo premium para temas críticos
    if priority in ["critical", "high"]:
        return True
    
    # Usa modelo premium para tweets longos e complexos
    if len(tweet_text) > 200:
        return True
    
    # Usa modelo premium se menciona dados ou números
    if any(word in tweet_text.lower() for word in ["dados", "pesquisa", "estudo", "%", "milhão", "bilhão"]):
        return True
    
    return False

def is_blacklisted_content(tweet_text: str) -> bool:
    """Verifica se o tweet contém conteúdo que não devemos responder"""
    text_lower = tweet_text.lower()
    return any(word in text_lower for word in BOT_CONFIG["blacklist_keywords"])