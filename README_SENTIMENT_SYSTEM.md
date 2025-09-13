# 😠 Sistema de Análise de Sentimento - Detector de Críticas

Sistema inteligente que monitora respostas aos seus tweets, detecta críticas negativas e ataques pessoais, e automaticamente adiciona os autores como "targets" para monitoramento futuro.

## 🎯 Como Funciona

### 🔍 **Monitoramento Automático**
1. **Verifica seus tweets** recentes a cada 5 minutos
2. **Analisa todas as respostas** usando IA (OpenAI GPT-4)
3. **Detecta sentimento negativo** e ataques pessoais
4. **Adiciona automaticamente** críticos como targets
5. **Integra com bot de palavras-chave** para monitoramento futuro

### 🧠 **Análise Inteligente de Sentimento**
- **Score de -1 a +1**: -1 = muito negativo, +1 = muito positivo
- **Detecta ataques pessoais** vs crítica construtiva
- **Identifica linguagem tóxica** e padrões hostis
- **Filtra spam e bots** automaticamente
- **Considera contexto** da conversa original

## 🚀 Instalação e Uso

### **Opção 1: Interface Completa (Recomendado)**
```bash
python start_sentiment_system.py
```

### **Opção 2: Gerenciador Central**
```bash
python bot_manager.py
# Escolha opção 6: Sistema de Análise de Sentimento
```

### **Opção 3: Execução Direta**
```bash
python sentiment_monitor.py
```

## ⚙️ Configuração

### **Parâmetros Principais**
```json
{
  "analysis_criteria": {
    "negative_threshold": -0.3,    // Limite para considerar negativo
    "criticism_keywords": [        // Palavras que indicam crítica
      "errado", "mentira", "falso", "ridículo"
    ]
  },
  "target_criteria": {
    "min_negativity_score": -0.4,      // Score mínimo para virar target
    "require_personal_attack": true,    // Exige ataque pessoal
    "exclude_constructive_criticism": true  // Exclui crítica construtiva
  },
  "monitoring_settings": {
    "check_interval_minutes": 5,       // Frequência de verificação
    "max_replies_per_check": 20,       // Máximo de respostas por vez
    "days_to_keep_targets": 30         // Dias para manter targets
  }
}
```

### **Personalização Fácil**
- **Threshold de Negatividade**: Ajuste a sensibilidade
- **Critérios de Target**: Define quando alguém vira target
- **Frequência**: Controla quantas vezes verifica por hora
- **Filtros**: Exclui bots, contas grandes, etc.

## 📊 Exemplo de Funcionamento

### **Cenário:**
Você posta: *"A nova política econômica vai ajudar as famílias"*

### **Respostas Analisadas:**
1. **@usuario1**: *"Discordo, mas respeito sua opinião"*
   - **Score**: -0.1 (levemente negativo)
   - **Resultado**: ❌ Não vira target (crítica respeitosa)

2. **@usuario2**: *"Você não entende nada de economia, que vergonha!"*
   - **Score**: -0.7 (muito negativo)
   - **Ataque pessoal**: ✅ Sim
   - **Resultado**: 🎯 **VIRA TARGET**

3. **@usuario3**: *"Adorei a proposta! Muito bem explicado"*
   - **Score**: +0.8 (muito positivo)
   - **Resultado**: ❌ Não vira target (positivo)

### **Target Adicionado:**
```json
{
  "user_id": "123456789",
  "username": "usuario2",
  "sentiment_score": -0.7,
  "reason": "Crítica negativa detectada",
  "is_personal_attack": true,
  "is_toxic": true,
  "negative_tweet_example": "Você não entende nada de economia, que vergonha!"
}
```

## 🎯 Gerenciamento de Targets

### **Visualização Completa**
```bash
python target_manager.py
```

### **Funcionalidades:**
- **📊 Resumo**: Estatísticas gerais dos targets
- **📋 Lista Detalhada**: Todos os targets com informações completas
- **💡 Sugestões**: Targets prontos para adicionar ao bot
- **➕ Adição Automática**: Integra com bot de palavras-chave
- **📤 Exportação**: Gera código para copiar e colar

### **Exemplo de Relatório:**
```
📊 RESUMO DOS TARGETS
Total de targets: 12
Tweets analisados: 156
Negativos detectados: 23
Taxa de negatividade: 14.7%

🎯 TARGETS MAIS RECENTES:
1. @critico_negativo (Score: -0.8) - 2024-12-15
   Razão: Crítica negativa detectada
   
2. @usuario_toxico (Score: -0.6) - 2024-12-14
   Razão: Ataque pessoal detectado
```

## 🔗 Integração com Bot de Palavras-Chave

### **Adição Automática**
O sistema gera automaticamente o código para adicionar targets ao bot:

```python
# Para TARGET_USER_IDS:
"123456789",            # @critico_negativo - Crítica negativa (Score: -0.8)
"987654321",            # @usuario_toxico - Ataque pessoal (Score: -0.6)

# Para USER_ID_TO_NAME_MAP:
"123456789": "@critico_negativo",
"987654321": "@usuario_toxico",
```

### **Processo:**
1. **Sistema detecta** crítica negativa
2. **Adiciona como target** automaticamente
3. **Gera sugestão** para o bot de palavras-chave
4. **Você aprova** e adiciona ao bot
5. **Bot monitora** tweets futuros dessa pessoa

## 📈 Estatísticas e Monitoramento

### **Métricas Disponíveis:**
- **Total de tweets analisados**
- **Percentual de negatividade detectada**
- **Targets adicionados por período**
- **Score médio de negatividade**
- **Tipos de problemas** (ataques pessoais, linguagem tóxica)

### **Análise Temporal:**
- **Últimas 24 horas**: Atividade recente
- **Últimos 7 dias**: Tendências semanais
- **Histórico completo**: Padrões de longo prazo

## 🛡️ Proteções e Filtros

### **Anti-Falsos Positivos:**
- **Crítica construtiva** não vira target
- **Debates respeitosos** são ignorados
- **Contexto da conversa** é considerado
- **Confiança da IA** é avaliada

### **Filtros de Qualidade:**
- **Contas com poucos seguidores** (possíveis bots)
- **Contas com muitos seguidores** (evita polêmicas grandes)
- **Spam e bots** são filtrados automaticamente
- **Linguagem ambígua** é analisada com cuidado

## 📁 Arquivos do Sistema

```
├── sentiment_monitor.py        # Monitor principal
├── target_manager.py          # Gerenciador de targets
├── start_sentiment_system.py  # Inicializador
├── negative_targets.json      # Base de dados dos targets
├── sentiment_config.json      # Configurações do sistema
├── target_suggestions.json    # Sugestões para o bot
├── analyzed_replies.json      # Cache de respostas analisadas
└── sentiment_monitor.log      # Log de atividades
```

## 🔧 Configurações Avançadas

### **Ajuste de Sensibilidade:**
```python
# Mais sensível (detecta mais críticas)
"negative_threshold": -0.2

# Menos sensível (só críticas muito negativas)
"negative_threshold": -0.5
```

### **Critérios de Target:**
```python
# Só ataques pessoais viram targets
"require_personal_attack": true

# Qualquer crítica negativa vira target
"require_personal_attack": false
```

### **Filtros de Conta:**
```python
# Ignora contas com menos de 50 seguidores
"min_follower_count": 50

# Ignora contas com mais de 100k seguidores
"max_follower_count": 100000
```

## 💡 Casos de Uso

### **1. Político/Influencer**
- **Detecta ataques coordenados**
- **Identifica trolls persistentes**
- **Monitora críticas sistemáticas**

### **2. Empresa/Marca**
- **Detecta clientes insatisfeitos**
- **Identifica detratores da marca**
- **Monitora crises de reputação**

### **3. Pessoa Pública**
- **Detecta cyberbullying**
- **Identifica haters sistemáticos**
- **Protege saúde mental**

## 🚨 Considerações Éticas

### **Uso Responsável:**
- **Não para perseguição** ou assédio
- **Respeite liberdade de expressão**
- **Use para proteção**, não ataque
- **Revise targets** antes de adicionar ao bot

### **Transparência:**
- **Logs detalhados** de todas as ações
- **Critérios claros** de classificação
- **Possibilidade de revisão** manual
- **Remoção fácil** de falsos positivos

## 📞 Suporte e Solução de Problemas

### **Problemas Comuns:**

**Muitos falsos positivos:**
- Aumente `negative_threshold` (ex: -0.5)
- Ative `exclude_constructive_criticism`
- Ajuste `criticism_keywords`

**Poucos targets detectados:**
- Diminua `negative_threshold` (ex: -0.2)
- Desative `require_personal_attack`
- Aumente `max_replies_per_check`

**Sistema lento:**
- Aumente `check_interval_minutes`
- Diminua `max_replies_per_check`
- Use modelo mais rápido

### **Logs e Diagnóstico:**
```bash
# Ver logs recentes
tail -f sentiment_monitor.log

# Testar configurações
python start_sentiment_system.py → opção 5

# Limpar dados corrompidos
python start_sentiment_system.py → opção 7
```

---

**Versão**: 1.0 - Sistema de Análise de Sentimento  
**Compatível com**: X API v2, OpenAI API  
**Última atualização**: Dezembro 2024

## 🎉 Resultado Final

Com este sistema você terá:
- ✅ **Detecção automática** de críticas negativas
- ✅ **Análise inteligente** de sentimento com IA
- ✅ **Adição automática** de targets
- ✅ **Integração perfeita** com bot de palavras-chave
- ✅ **Monitoramento completo** de atividade
- ✅ **Proteção contra** falsos positivos

O sistema trabalha 24/7 protegendo sua reputação e identificando quem realmente merece ser monitorado!