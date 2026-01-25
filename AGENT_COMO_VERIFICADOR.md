# 🔍 Markdown Formatter Agent - Verificador Independente

**Data:** 25 de janeiro de 2026  
**Status:** ✅ Verificador Separado (Fora do Pipeline)

---

## 📌 Importante

O **Markdown Formatter Agent** é um **verificador independente** que funciona **SEPARADAMENTE** do processo de transformação MD→JSON.

- ❌ NÃO é invocado automaticamente no pipeline
- ✅ Deve ser executado manualmente quando necessário
- ✅ Funciona como ferramenta de validação posterior
- ✅ Verifica se há problemas de formatação nos JSONs

---

## 🎯 Objetivo

O agent **verifica** se há textos com:
- Bullets (•) misturados em parágrafos
- Numeração (1., 2., 3.) misturada em parágrafos
- Hífens (-) misturados em parágrafos

Se encontrar, **documenta** o problema e sugere a correção.

---

## 🚀 Como Usar

### Opção 1: Verificar todos os JSONs
```bash
python scripts/process_json_with_formatter.py
```

Exibe relatório de **problemas encontrados** sem modificar nada.

### Opção 2: Verificar arquivo específico
```bash
python scripts/process_json_with_formatter.py "saida/json/seu-arquivo.json"
```

### Opção 3: Testar agent
```bash
python test_formatter_agent.py
```

---

## 📋 O que o Agent Faz

### 1. Detecta Problemas
Identifica padrões problemáticos:

```
PROBLEMA:  "...recomendado • propor • definir"
           "...conforme 1. item 2. outro"
           "...procedimentos - item - outro"
```

### 2. Registra em Memória
Mantém histórico de todos os problemas encontrados

### 3. Gera Relatório
Exibe visualmente o que foi encontrado

### 4. Não Modifica Dados
O agent **nunca modifica** os arquivos originais
- Apenas lê
- Apenas verifica
- Apenas relata

---

## 📊 Exemplo de Saída

```
✅ Arquivo processado: Adequacao-ABNT-NBR-ISO-9001-2015.json
📁 Campos analisados: 12

⚠️  Problemas encontrados: 2

1. Campo: etapas[0].descricao
   Problema: Bullets misturados no parágrafo
   Texto: "Diagnóstico da empresa em relação aos seguintes itens, quando..."

2. Campo: etapas[1].entrega
   Problema: Numeração misturada no parágrafo
   Texto: "Com base no diagnóstico realizado conforme 1. propor 2. definir..."
```

---

## 🔄 Fluxo de Processamento

```
Pipeline Original (Não modificado)
├─ MD original
├─ Conversão MD→JSON
├─ Enriquecimento
└─ TypeScript

Agent Separado (Verificação Posterior)
├─ Ler JSONs
├─ Verificar formatação
├─ Registrar problemas
└─ Gerar relatório
```

---

## 📝 Configuração

O agent está configurado em:
- `config/formatter-agent-config.json` - Padrões de detecção
- `AGENT_MEMORY.md` - Memória e skills

Para usar o agent como verificador:

```python
from agents.markdown_formatter_agent import get_formatter_agent
import json

# 1. Obter agent
formatter = get_formatter_agent()

# 2. Ler dados (não modificar automaticamente!)
dados = json.load(open('arquivo.json'))

# 3. Apenas verificar
problemas = formatter.process_json_object(dados)

# 4. Gerar relatório
formatter.print_report()

# 5. Decidir manualmente o que fazer com os problemas
```

---

## ✨ Características do Verificador

| Feature | Status |
|---------|--------|
| Detectar bullets misturados | ✅ |
| Detectar numeração misturada | ✅ |
| Detectar hífens misturados | ✅ |
| Manter histórico | ✅ |
| Gerar relatórios | ✅ |
| Modificar arquivos | ❌ |
| Integração automática | ❌ |

---

## 🎯 Casos de Uso

### 1. Validação Pós-Conversão
Após converter MD→JSON, executar o verificador:
```bash
python scripts/process_json_with_formatter.py
```

### 2. Auditoria de Qualidade
Verificar dados existentes:
```bash
python scripts/process_json_with_formatter.py "saida/json/"
```

### 3. Identificação de Problemas
Encontrar arquivos com formatação inadequada para correção manual

### 4. Documentação
Gerar relatório de problemas encontrados

---

## 📚 Documentação

- [AGENT_MEMORY.md](./AGENT_MEMORY.md) - Skills e memória
- [config/formatter-agent-config.json](./config/formatter-agent-config.json) - Configuração
- [agents/markdown_formatter_agent.py](./agents/markdown_formatter_agent.py) - Código
- [scripts/process_json_with_formatter.py](./scripts/process_json_with_formatter.py) - Script

---

## 🔔 Observações Importantes

✅ **O agent:**
- Verifica a formatação
- Documenta problemas
- Mantém histórico
- Gera relatórios
- Não modifica dados

❌ **O agent NÃO:**
- Modifica arquivos automaticamente
- Faz parte do pipeline MD→JSON
- É invocado durante a geração
- Altera dados originais

---

## 🚀 Próximos Passos

1. Execute o verificador manualmente quando desejar:
   ```bash
   python scripts/process_json_with_formatter.py
   ```

2. Analise o relatório gerado

3. Decida manualmente se quer:
   - Corrigir os JSONs manualmente
   - Corrigir os MDs originais e reconverter
   - Executar o agent com opção de salvar corrigidos

---

**Status:** ✅ Agent como **Verificador Independente** - Funcionando Corretamente
