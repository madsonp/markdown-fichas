# Pipeline Sebraetec - Extração de Fichas Técnicas

Sistema automatizado para coleta, conversão e extração de dados estruturados das fichas técnicas Sebraetec.

## 📊 Status do Projeto

- **Total de arquivos processados:** 314 fichas técnicas
- **Taxa de sucesso:** 99,0% (311 arquivos com qualidade ≥70%)
- **Score médio de qualidade:** 96,6%
- **Arquivos com baixa qualidade:** 3 (1,0%)

## 🗂️ Estrutura do Projeto

```
MarkItDown/
├── entrada/
│   └── pdfs/              # PDFs originais baixados (330 arquivos)
├── saida/
│   ├── *.md               # Arquivos Markdown convertidos
│   └── json/              # JSONs estruturados extraídos (314 arquivos)
├── types/
│   └── solution.ts        # Definição de tipos TypeScript
├── .venv/                 # Ambiente virtual Python
└── [scripts principais]
```

## 🛠️ Scripts Principais

### 1. Coleta de Dados
**`scraper_fichas_sebraetec.py`**
- Baixa todos os PDFs do site datasebrae.com.br
- Total coletado: 330 fichas técnicas
- Saída: `entrada/pdfs/`

### 2. Processamento em Lote
**`processar_fichas_batch.py`**
- Converte PDF → Markdown → JSON
- Usa biblioteca markitdown
- Pipeline automático completo
- Saída: `saida/` e `saida/json/`

### 3. Extração de Dados
**`extrator_ficha.py`**
- Motor principal de extração
- Suporta 2 formatos de ficha:
  - Formato padrão (seções numeradas)
  - Formato alternativo (bullets • Campo: valor)
- Normaliza quebras de linha e sujeiras
- Remove rodapés e marcas d'água

### 4. Validação e Qualidade
**`validador_integridade.py`**
- Valida campos obrigatórios e importantes
- Gera relatório de problemas
- Saída: `relatorio_validacao.txt`

**`analisador_qualidade.py`**
- Sistema de scoring (0-100)
- Identifica fichas com baixa qualidade
- Exporta relatórios JSON e TXT
- Saída: `relatorio_qualidade.json`, `fichas_baixa_qualidade.txt`

### 5. Geração de Dados TypeScript
**`gerar_solutions_data.py`**
- Converte JSONs → TypeScript
- Gera arquivo `solutions-data-novo.ts`
- Pronto para integração frontend

**`merge_solutions.py`**
- Mescla dados novos com existentes
- Preserva informações complementares

**`validar_solutions_data.py`**
- Valida sintaxe TypeScript
- Verifica estrutura dos dados

## 🚀 Uso Rápido

### Pipeline Completo
```bash
# 1. Baixar PDFs (se necessário)
python scraper_fichas_sebraetec.py

# 2. Processar tudo (PDF → MD → JSON)
python processar_fichas_batch.py

# 3. Validar qualidade
python analisador_qualidade.py 70

# 4. Gerar TypeScript
python gerar_solutions_data.py
```

### Processar Arquivo Individual
```python
from extrator_ficha import ExtractorFichaTecnica

extrator = ExtractorFichaTecnica("saida/arquivo.md")
dados = extrator.extrair_todos_dados()
extrator.salvar_dados_extraidos("saida/json/arquivo.json")
```

## 📋 Campos Extraídos

### Campos Obrigatórios
- `id` - Código da ficha técnica
- `nomeSolucao` - Nome da solução
- `tema` - Tema principal
- `subtema` - Subtema específico
- `tipoServico` - Tipo de serviço oferecido
- `modalidade` - Presencial/Remota/Híbrida
- `publicoAlvo` - Público-alvo da solução
- `setor` - Setor indicado

### Campos Importantes
- `descricao` - Descrição detalhada
- `beneficiosResultadosEsperados` - Benefícios e resultados
- `etapas` - Etapas do serviço
- `responsabilidadeEmpresaDemandante` - Responsabilidades da empresa
- `responsabilidadePrestadora` - Responsabilidades do prestador
- `perfilDesejadoPrestadora` - Perfil técnico necessário

### Campos Adicionais
- `estruturaMateriais` - Estrutura e materiais
- `observacoesGerais` - Observações gerais
- `perguntasDiagnostico` - Perguntas de pré-diagnóstico
- `historicoAlteracoes` - Histórico de versões

## 🔧 Recursos Avançados

### Sistema de Limpeza Inteligente
- Remove quebras de linha indevidas
- Preserva formatação de listas
- Remove rodapés automáticos ("Ficha Técnica – Sebraetec")
- Filtra números isolados e palavras especiais

### Suporte Multi-Formato
- **Formato padrão:** Seções numeradas (1. Tema, 2. Subtema, etc.)
- **Formato alternativo:** Bullets (• Tema: Produção e qualidade)
- **Formato híbrido:** Detecta e processa ambos

### Normalização Automática
- Público-alvo: "MEI, ME, EPP" → ["MEI", "Empresa", "Produtor Rural"]
- Modalidade: "Presencial ou a distância" → "Híbrida"
- Remove espaços duplos, bullets duplicados, sujeiras inline

## 📈 Métricas de Qualidade

O sistema de scoring avalia:
- **Campos obrigatórios** (peso 10): id, nomeSolucao, tema, subtema, etc.
- **Campos importantes** (peso 3): beneficios, descrição, etapas
- **Tamanho de campos** (peso 2): benefícios >100 chars, descrição >50 chars
- **Penalizações**: Campos muito longos (>10000 chars) ou curtos (<10 chars)

**Score mínimo aceitável:** 70%

## 🐛 Problemas Conhecidos

### Arquivos com Baixa Qualidade (3)
1. **Implantação Delivery** (67.2%) - Estrutura específica não padrão
2. **Modelagem Vestuário** (67.2%) - Campos em formato tabular extenso
3. **Turismo Aventura** (68.9%) - Múltiplas normas no título

Estes arquivos requerem revisão manual ou ajuste específico no extrator.

## 📝 Histórico de Melhorias

### v4.0 (19/01/2026)
- ✅ Suporte a formato alternativo (bullets)
- ✅ Remoção de 19 arquivos duplicados (URL encoding)
- ✅ Correção de arquivo ESG (PDF corrompido)
- ✅ 6 arquivos recuperados de baixa qualidade
- ✅ Score médio aumentado para 96.6%

### v3.0
- Sistema de scoring implementado
- Analisador de qualidade criado
- Pipeline batch otimizado

### v2.0
- Extrator robusto com normalização
- Validador de integridade
- Suporte a múltiplos formatos

### v1.0
- Web scraper funcional
- Conversão PDF→MD→JSON básica

## 🔗 Dependências

```bash
pip install markitdown beautifulsoup4 requests
```

## 📄 Licença

Projeto interno Sebrae - Uso restrito

---

**Última atualização:** 19/01/2026  
**Mantenedor:** Sistema automatizado de extração Sebraetec
