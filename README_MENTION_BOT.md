# 🤖 Bot de Menções X.com - Resposta Inteligente

Bot especializado em responder automaticamente quando sua conta é mencionada no X (Twitter), com distribuição inteligente de tokens entre ChatGPT e xAI.

## 🎯 Funcionalidades Principais

### ✨ Resposta Automática a Menções
- **Monitoramento 24/7**: Verifica menções a cada 2 minutos
- **Resposta Contextual**: Considera o contexto da conversa e thread
- **Personalidade Consistente**: Mantém tom e estilo definidos por você
- **Anti-Spam**: Não responde a si mesmo ou menções duplicadas

### 🧠 Distribuição Inteligente de Tokens
- **Balanceamento Automático**: Alterna entre ChatGPT e xAI automaticamente
- **Economia de Tokens**: Usa o modelo menos utilizado para distribuir custos
- **Estatísticas Detalhadas**: Monitora uso de cada modelo em tempo real
- **Fallback**: Se um modelo falha, usa o outro automaticamente

### 🎨 Prompt Totalmente Customizável
- **Personalidade**: Define tom, estilo e emoção das respostas
- **Valores Fundamentais**: Lista suas crenças e princípios
- **Diretrizes**: Regras específicas de como responder
- **Contexto Histórico**: Considera histórico da conversa
- **Presets**: Configurações prontas (progressista, técnico, educador)

## 🚀 Como Usar

### 1. Instalação Rápida
```bash
# Instale dependências
pip install tweepy openai requests

# Configure suas chaves de API no arquivo keys.py
# Execute o bot
python start_mention_bot.py
```

### 2. Primeira Configuração
1. **Execute**: `python start_mention_bot.py`
2. **Digite seu username** do X (sem @)
3. **Personalize o prompt** (opção 2 do menu)
4. **Inicie o bot** (opção 1)

### 3. Personalização do Prompt
```bash
python customize_prompt.py
```

Interface amigável para configurar:
- **Tom**: Como o bot deve "falar"
- **Valores**: O que o bot defende
- **Diretrizes**: Como deve responder
- **Instruções**: Comportamento específico

## 📊 Exemplo de Configuração

### Personalidade Base
```json
{
  "tone": "inteligente, respeitoso mas firme",
  "style": "direto e factual",
  "emotion": "equilibrado, nem muito formal nem muito casual",
  "max_length": 280
}
```

### Valores Fundamentais
- Defende a democracia e o Estado de Direito
- Valoriza dados e evidências científicas
- Promove o diálogo respeitoso e construtivo
- Questiona desinformação de forma educativa
- Apoia transparência e accountability

### Diretrizes de Resposta
- Sempre peça fontes quando alguém faz afirmações sem evidência
- Use dados oficiais quando disponíveis (IBGE, TSE, etc.)
- Mantenha o foco no argumento, não na pessoa
- Seja educativo, não apenas crítico
- Evite linguagem ofensiva ou polarizante

## 🔧 Arquivos Importantes

```
├── mention_bot.py              # Bot principal
├── start_mention_bot.py        # Inicializador com menu
├── customize_prompt.py         # Personalizador de prompt
├── mention_prompt_config.json  # Sua configuração personalizada
├── model_usage_stats.json      # Estatísticas de uso
├── processed_mentions.json     # Menções já processadas
└── mention_bot.log            # Log de atividades
```

## 📈 Monitoramento

### Estatísticas em Tempo Real
- **Total de respostas** enviadas
- **Distribuição de tokens** entre modelos
- **Balanceamento** ChatGPT vs xAI
- **Menções processadas** recentemente

### Exemplo de Relatório
```
📊 ESTATÍSTICAS DE USO
Total de respostas: 47
Total de tokens: 3,240

ChatGPT:
  • Usos: 23 (48.9%)
  • Tokens: 1,610

xAI (Grok):
  • Usos: 24 (51.1%)
  • Tokens: 1,630

✅ Modelos bem balanceados!
```

## 🎨 Presets Disponíveis

### 1. Político Progressista
- **Tom**: Firme mas respeitoso, progressista
- **Foco**: Direitos humanos, igualdade social, sustentabilidade
- **Estilo**: Defende mudanças sociais positivas

### 2. Analista Técnico
- **Tom**: Técnico, analítico, baseado em dados
- **Foco**: Evidências científicas, metodologia, precisão
- **Estilo**: Sempre pede fontes e questiona dados

### 3. Educador Democrático
- **Tom**: Educativo, paciente, democrático
- **Foco**: Informação de qualidade, diálogo respeitoso
- **Estilo**: Didático e construtivo

## 🛡️ Segurança e Boas Práticas

### Proteções Integradas
- **Anti-Loop**: Nunca responde a si mesmo
- **Cache de Respostas**: Evita duplicatas
- **Rate Limiting**: Respeita limites da API
- **Logs Detalhados**: Auditoria completa

### Configurações Recomendadas
- **Máximo 280 caracteres** por resposta
- **Verificação a cada 2 minutos** (não sobrecarrega API)
- **Backup automático** de configurações
- **Rotação de logs** para não ocupar espaço

## 🔧 Solução de Problemas

### Bot não responde
1. Verifique se o username está correto
2. Confirme se as chaves de API estão válidas
3. Veja o arquivo `mention_bot.log` para erros

### Desbalanceamento de modelos
- Execute `start_mention_bot.py` → opção 3
- Se um modelo está sendo usado muito mais, o bot se auto-corrige

### Respostas inadequadas
- Use `customize_prompt.py` para ajustar diretrizes
- Adicione mais valores fundamentais
- Refine as instruções personalizadas

## 💡 Dicas Avançadas

### Otimização de Tokens
- Use frases mais curtas nas diretrizes
- Seja específico nos valores fundamentais
- Teste diferentes configurações de `max_length`

### Personalização Avançada
- Crie múltiplos presets para diferentes contextos
- Ajuste `context_awareness` para mais ou menos contexto
- Use `custom_instructions` para comportamentos específicos

### Monitoramento
- Verifique estatísticas regularmente
- Analise logs para identificar padrões
- Ajuste configurações baseado no feedback

## 📞 Suporte

### Logs e Diagnóstico
```bash
# Ver logs recentes
tail -f mention_bot.log

# Testar configurações
python start_mention_bot.py → opção 5

# Limpar dados corrompidos
python start_mention_bot.py → opção 6
```

### Arquivos de Configuração
- **mention_prompt_config.json**: Sua personalidade e diretrizes
- **model_usage_stats.json**: Estatísticas de uso dos modelos
- **mention_bot_config.json**: Configurações gerais

---

**Versão**: 1.0 - Bot de Menções Inteligente  
**Compatível com**: X API v2, OpenAI API, xAI API  
**Última atualização**: Dezembro 2024

## 🎉 Resultado Final

Com este bot você terá:
- ✅ **Respostas automáticas** a todas as menções
- ✅ **Distribuição inteligente** de tokens entre APIs
- ✅ **Personalidade consistente** definida por você
- ✅ **Monitoramento completo** de atividade
- ✅ **Configuração fácil** através de interface amigável

O bot mantém sua voz e valores enquanto economiza tokens e responde de forma inteligente a quem te menciona!