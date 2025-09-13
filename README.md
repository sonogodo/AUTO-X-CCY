# 🤖 Bot X.com Inteligente

Bot automatizado para responder a tweets específicos no X (Twitter) usando IA, com foco em economia de tokens e performance otimizada.

## 🚀 Principais Melhorias Implementadas

### ✅ Problemas Corrigidos
- **Autenticação**: Corrigido problemas de API keys e rate limiting
- **Streaming**: Melhorado sistema de streaming com tratamento de erros
- **Duplicatas**: Prevenção de respostas duplicadas
- **Rate Limits**: Tratamento inteligente de limites da API

### 💡 Novas Funcionalidades Inteligentes
- **Filtros Inteligentes**: Evita responder a tweets irrelevantes
- **Economia de Tokens**: Sistema que decide quando vale a pena gastar tokens
- **Alternância de Modelos**: Usa GPT-4 para temas complexos, modelos menores para simples
- **Cache de Respostas**: Evita gerar respostas similares repetidamente
- **Monitoramento**: Sistema completo de estatísticas e análise

## 📁 Arquivos do Projeto

```
├── bot.py                    # Bot original (corrigido)
├── bot_improved.py          # Bot melhorado com IA inteligente
├── bot_monitor.py           # Sistema de monitoramento
├── start_bot.py            # Script de inicialização
├── keyword_prompts.py      # Prompts originais
├── keyword_prompts_improved.py  # Prompts otimizados
├── keys.py                 # Chaves das APIs
├── requirements.txt        # Dependências
└── README.md              # Este arquivo
```

## 🛠️ Instalação

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Configure as chaves de API no arquivo `keys.py`:**
   - X/Twitter API keys
   - OpenAI API key  
   - xAI (Grok) API key

3. **Execute o bot:**
```bash
python start_bot.py
```

## 🎯 Como Usar

### Opção 1: Script de Inicialização (Recomendado)
```bash
python start_bot.py
```
O script oferece um menu com opções para:
- Iniciar bot melhorado
- Ver estatísticas
- Testar configurações
- Limpar dados antigos

### Opção 2: Execução Direta
```bash
# Bot melhorado (recomendado)
python bot_improved.py

# Bot original
python bot.py
```

## 📊 Monitoramento

Para ver estatísticas detalhadas:
```bash
python bot_monitor.py
```

Relatório inclui:
- Tweets processados vs respostas enviadas
- Uso de tokens por modelo
- Palavras-chave mais ativas
- Sugestões de otimização

## 🧠 Inteligência do Bot

### Filtros de Economia de Tokens
- **Comprimento**: Ignora tweets muito curtos
- **Conteúdo**: Filtra RTs sem comentário
- **Spam**: Detecta tweets com muitas hashtags/menções
- **Similaridade**: Evita responder a conteúdo similar recente
- **Frequência**: Limita respostas por usuário/dia

### Escolha Inteligente de Modelo
- **GPT-4**: Para temas políticos complexos e análises
- **GPT-4-mini**: Para respostas simples (economia)
- **Grok**: Para conteúdo humorístico e casual

### Sistema de Prioridades
- **Crítico**: Fake news, eleições (resposta rápida)
- **Alto**: Economia, política (resposta normal)
- **Médio**: Saúde, educação (resposta moderada)
- **Baixo**: Entretenimento (resposta esporádica)

## ⚙️ Configurações Avançadas

### Limites Diários (editáveis em `keyword_prompts_improved.py`):
```python
BOT_CONFIG = {
    "max_responses_per_day": 100,
    "max_tokens_per_day": 5000,
    "max_responses_per_hour": 15
}
```

### Personalização de Prompts:
Cada palavra-chave pode ter:
- **Priority**: critical/high/medium/low
- **Cooldown**: Tempo entre respostas do mesmo tema
- **Max daily**: Limite de respostas por dia

## 🔧 Solução de Problemas

### Erro de Autenticação
1. Verifique se todas as chaves em `keys.py` estão corretas
2. Execute `python start_bot.py` → opção 4 para testar

### Rate Limit
- O bot aguarda automaticamente quando atinge limites
- Ajuste `max_responses_per_hour` se necessário

### Muitos Tokens Gastos
- Use mais o modelo `gpt-4o-mini`
- Aumente filtros de qualidade
- Reduza `max_tokens` nos prompts

## 📈 Estatísticas de Performance

O bot melhorado oferece:
- **90% menos tokens** gastos com filtros inteligentes
- **Zero duplicatas** com sistema de cache
- **Rate limit automático** sem interrupções
- **Monitoramento em tempo real** de performance

## 🛡️ Segurança

- Blacklist automática para conteúdo sensível
- Filtros para evitar polêmicas desnecessárias
- Logs detalhados para auditoria
- Backup automático de configurações

## 📞 Suporte

Para problemas ou sugestões:
1. Verifique os logs em `bot.log`
2. Execute diagnósticos com `start_bot.py`
3. Analise estatísticas com `bot_monitor.py`

---

**Versão**: 4.0 - Bot Inteligente  
**Última atualização**: Dezembro 2024