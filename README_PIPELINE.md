# Pipeline de Processamento de Fichas Técnicas Sebraetec

Este projeto automatiza a coleta e conversão de fichas técnicas do Sebraetec em formato estruturado JSON.

## 📋 Índice

- [Estrutura do Projeto](#estrutura-do-projeto)
- [Scripts Disponíveis](#scripts-disponíveis)
- [Pipeline Completo](#pipeline-completo)
- [Uso](#uso)

## 📂 Estrutura do Projeto

```
MarkItDown/
├── entrada/
│   └── pdfs/              # PDFs baixados (330 fichas)
├── saida/
│   ├── *.md              # Arquivos Markdown convertidos
│   └── json/             # Arquivos JSON finais estruturados
├── scraper_fichas_sebraetec.py      # Web scraper
├── processar_fichas_batch.py        # Pipeline batch PDF→MD→JSON
├── extrator_ficha.py                # Extrator de dados MD→JSON
└── README_PIPELINE.md               # Este arquivo
```

## 🛠️ Scripts Disponíveis

### 1. `scraper_fichas_sebraetec.py`

**Propósito**: Coleta todos os PDFs das fichas técnicas do site do Sebraetec

**URL**: https://datasebrae.com.br/fichas-tecnicas-sebraetec/

**Uso**:
```bash
python scraper_fichas_sebraetec.py
```

**Saída**: 
- 330 PDFs salvos em `entrada/pdfs/`
- Categorias incluídas: GQ (Qualidade), MMP (Produtividade), DA/DC/DP/DS (Design), AA/EE/GS/R/SST (Sustentabilidade), PI/PT/DP/GI/MG/TD (Inovação e Tecnologia)

### 2. `processar_fichas_batch.py`

**Propósito**: Processa em lote todos os PDFs através do pipeline completo

**Pipeline**:
1. PDF → Markdown (usando markitdown)
2. Markdown → JSON estruturado (usando extrator_ficha.py)

**Uso**:
```bash
# Processar todos os arquivos
python processar_fichas_batch.py

# Processar apenas os N primeiros (para teste)
python processar_fichas_batch.py 5
```

**Saída**: 
- Arquivos `.md` em `saida/`
- Arquivos `.json` em `saida/json/`

### 3. `extrator_ficha.py`

**Propósito**: Extrai dados estruturados de um arquivo Markdown de ficha técnica

**Funcionalidades**:
- Extração inteligente de campos (tema, subtema, etapas, etc.)
- Normalização de dados (modalidades, público-alvo)
- Tratamento de quebras de linha em textos contínuos
- Remoção de rodapés e textos residuais
- Limpeza de formatação inconsistente

**Campos extraídos**:
```json
{
  "id": "12035-1",
  "nomeSolucao": "...",
  "tema": "...",
  "subtema": "...",
  "tipoServico": "...",
  "modalidade": "Presencial | Online | Híbrido",
  "publicoAlvo": ["Empresa", "Produtor Rural", "Artesão"],
  "objetivo": "...",
  "descricao": "...",
  "beneficiosResultadosEsperados": "...",
  "etapas": [...],
  "perguntasDiagnostico": [...],
  "responsabilidadeEmpresaDemandante": "...",
  "responsabilidadePrestadora": "...",
  "perfilDesejadoPrestadora": "...",
  "observacoesGerais": "...",
  "historicoAlteracoes": [...]
}
```

## 🚀 Pipeline Completo

### Passo 1: Baixar PDFs

```bash
python scraper_fichas_sebraetec.py
```

Resultado: 330 PDFs baixados em `entrada/pdfs/`

### Passo 2: Processar Todos os PDFs

```bash
python processar_fichas_batch.py
```

O script:
1. ✅ Converte cada PDF para Markdown
2. ✅ Extrai dados estruturados para JSON
3. ⏭️ Pula arquivos já processados
4. 📊 Gera relatório final com estatísticas

### Passo 3: Validar Resultados

```bash
# Verificar quantidade de arquivos gerados
ls saida/json/*.json | wc -l

# Verificar estrutura de um JSON
python -c "import json; print(json.dumps(json.load(open('saida/json/Certificacao_Programa_Qualidade_ABSOLAR-CI12035-1.json')), indent=2)[:500])"
```

## 📊 Estatísticas

- **Total de fichas**: 330
- **Taxa de sucesso esperada**: ~98%
- **Tempo de processamento**: ~2-3 horas (depende do hardware)

## 🔧 Tratamentos Especiais

### 1. Quebras de Linha

O extrator remove quebras de linha (`\n`) no meio de frases, preservando apenas quebras após pontuação quando apropriado.

**Antes**:
```
"A certificação no programa cria um diferencial\npara as empresas do setor"
```

**Depois**:
```
"A certificação no programa cria um diferencial para as empresas do setor"
```

### 2. Rodapés e Sujeira

Remove automaticamente:
- Rodapés de página: "2 Ficha Técnica – Sebraetec 4.0"
- Códigos de ficha inline
- Texto "Confidencial" isolado
- Múltiplos espaços

### 3. Normalização

- **Modalidade**: Presencial, Online, Híbrido
- **Público-alvo**: Empresa, Produtor Rural, Artesão
- **Etapas**: Estrutura padronizada com id, título, ordem, tipo, descrição, entrega

## 🐛 Troubleshooting

### PDFs não foram baixados
- Verifique conexão com internet
- Verifique se o site está acessível
- O scraper já tentou baixar 330 PDFs com sucesso

### Erro ao converter PDF
- Instale markitdown: `pip install markitdown`
- Verifique dependências: `pip list | grep markitdown`

### JSON com dados incompletos
- Verifique o arquivo Markdown correspondente
- Alguns PDFs podem ter formatação inconsistente
- O extrator usa heurísticas robustas mas pode falhar em casos extremos

## 📝 Logs

Durante o processamento, o script gera logs detalhados:

```
[1/330] Nome-do-arquivo.pdf
   📄 Convertendo para MD...
   ✅ MD criado: Nome-do-arquivo.md
   🔄 Extraindo dados para JSON...
   ✅ JSON criado: Nome-do-arquivo.json
```

## ✅ Checklist de Validação

- [ ] 330 PDFs baixados em `entrada/pdfs/`
- [ ] ~330 arquivos MD em `saida/`
- [ ] ~330 arquivos JSON em `saida/json/`
- [ ] JSON válidos (testar com `json.load()`)
- [ ] Campos obrigatórios preenchidos (id, nomeSolucao, tema, etc.)
- [ ] Sem quebras de linha indesejadas em `beneficiosResultadosEsperados`

## 🎯 Próximos Passos

1. ✅ Validar consistência dos dados extraídos
2. ⏸️ Criar validador automático de schemas
3. ⏸️ Gerar estatísticas agregadas (temas mais comuns, etc.)
4. ⏸️ Integrar com sistema de busca/filtragem

---

**Autor**: Sistema de conversão automática  
**Data**: Janeiro 2026  
**Versão**: 1.0
