# Soluções Sebraetec - Fichas Técnicas em Markdown

Fichas técnicas das soluções Sebraetec convertidas para o formato Markdown.

## 📊 Sobre o Repositório

- **Total de soluções:** 314 fichas técnicas
- **Formato:** Markdown (.md)
- **Origem:** PDFs oficiais do Sebraetec datasebrae.com.br

## 🗂️ Estrutura

```
Sebraetec-Solutions-MD/
└── saida/          # Arquivos Markdown das soluções (314 arquivos)
```

## 📝 Conteúdo das Fichas

Cada arquivo Markdown contém informações sobre uma solução Sebraetec:
- Título e código SAS
- Descrição da solução
- Objetivos
- Atividades realizadas
- Entregas
- Informações de preço e categoria

## 💡 Como Usar

Estes arquivos estão prontos para:
- Visualização direta no GitHub
- Integração em sistemas de documentação
- Conversão para outros formatos
- Processamento automatizado

## 🔗 Links Úteis

- [Site oficial Sebraetec](https://datasebrae.com.br/)
- Fichas originais: datasebrae.com.br/sebraetec

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
