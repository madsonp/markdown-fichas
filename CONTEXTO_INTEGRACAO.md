# Contexto do Projeto - Integração Pipeline e Sistema Principal

## 📅 Data: 19/01/2026

## 🗂️ Estrutura de Pastas

### Pasta 1: Pipeline de Processamento
**Localização**: `C:\Codes\MarkItDown`

**Função**: Extração, conversão e processamento de fichas técnicas Sebraetec
- Baixa PDFs do datasebrae.com.br
- Converte PDF → Markdown → JSON
- Extrai dados estruturados
- Gera arquivo TypeScript para frontend
- Valida qualidade e integridade

**Arquivos principais**:
- `scraper_fichas_sebraetec.py` - Coleta PDFs
- `processar_fichas_batch.py` - Pipeline completo
- `extrator_ficha.py` - Motor de extração
- `gerar_solutions_data.py` - Gera TypeScript
- `analisador_qualidade.py` - Análise de qualidade
- `validador_integridade.py` - Validação de campos

**Saídas**:
- `entrada/pdfs/` - PDFs originais
- `saida/` - Markdowns convertidos
- `saida/json/` - JSONs estruturados (314 fichas)
- `solutions-data.ts` - TypeScript final

### Pasta 2: Sistema Principal
**Nome**: "soluções sebraetec"
**Localização**: A definir
**Função**: Sistema principal onde os dados processados serão integrados

## ⚠️ Problema Identificado

### Fichas Técnicas com Qualidade Técnica Inadequada
As fichas não seguem completamente os padrões esperados, resultando em:
- Campos faltantes ou incompletos
- Estrutura inconsistente entre fichas
- Dados não normalizados
- Possível necessidade de reprocessamento

### Status Atual
- ✅ 314 fichas processadas
- ✅ 265 fichas com Código SAS (84.4%)
- ⚠️ Qualidade variável entre fichas
- ⚠️ Necessidade de ajustes no processamento

## 🎯 Próximas Ações Planejadas

### 1. Análise de Qualidade
- [ ] Executar `analisador_qualidade.py` para identificar fichas problemáticas
- [ ] Revisar `relatorio_qualidade.json` para métricas detalhadas
- [ ] Listar fichas com score abaixo do threshold aceitável

### 2. Correções Necessárias
- [ ] Identificar padrões específicos de problemas
- [ ] Ajustar extratores para casos especiais
- [ ] Implementar regras de normalização adicionais
- [ ] Validar campos obrigatórios

### 3. Reprocessamento
- [ ] Definir critérios para reprocessamento
- [ ] Criar script para reprocessar fichas específicas
- [ ] Validar melhorias após reprocessamento
- [ ] Regenerar `solutions-data.ts` final

### 4. Integração com Sistema Principal
- [ ] Definir caminho da pasta "soluções sebraetec"
- [ ] Mapear estrutura esperada pelo sistema principal
- [ ] Criar script de integração/migração
- [ ] Validar dados integrados

## 🔧 Scripts Disponíveis para Análise

### Identificar Problemas
```bash
# Análise de qualidade (threshold 70)
python analisador_qualidade.py 70

# Validação de integridade
python validador_integridade.py

# Listar códigos SAS
python listar_codigos_sas.py
```

### Verificar Encoding
```bash
# Verificar UTF-8 BOM
python verificar_encoding.py
```

### Reprocessamento
```bash
# Processar ficha individual
python processar_fichas_batch.py

# Regenerar TypeScript
python gerar_solutions_data.py
```

## 📊 Métricas Atuais

| Métrica | Valor | Status |
|---------|-------|--------|
| Total de fichas | 314 | ✅ |
| Com Código SAS | 265 (84.4%) | ✅ |
| Sem Código SAS | 49 (15.6%) | ⚠️ |
| Encoding | UTF-8 BOM | ✅ |
| Qualidade média | A definir | ⏳ |

## 🔍 Pontos de Atenção

1. **Variação de Formato**
   - Formato padrão (seções numeradas)
   - Formato alternativo (bullets • Campo: valor)
   - Necessidade de suporte a ambos

2. **Campos Problemáticos**
   - A identificar após análise de qualidade
   - Possíveis: etapas, perguntas diagnóstico, ODS

3. **Códigos SAS Faltantes**
   - 49 fichas sem Código SAS
   - Não encontradas na tabela de preços
   - Verificar se são fichas válidas ou obsoletas

## 📝 Observações

- Pipeline atual funcional para maioria das fichas
- Qualidade varia por não seguirem padrão estrito
- Necessário ajuste fino antes de integração final
- Encoding UTF-8 BOM resolvido para Windows

## 🚀 Quando Retomar

**Informações necessárias**:
1. Caminho da pasta "soluções sebraetec"
2. Estrutura/formato esperado pelo sistema principal
3. Critérios específicos de qualidade necessários
4. Quais ajustes priorizar no reprocessamento

**Aguardando estruturação pelo usuário para definir próximos passos.**
