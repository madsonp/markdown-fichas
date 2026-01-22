# 📚 Guia de Instalação e Uso

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional, para clonar o repositório)

### Instalação Automática

O jeito mais fácil é usar o script de setup automático:

```bash
# 1. Clonar ou navegar até o diretório
cd C:\Codes\MarkItDown

# 2. Executar setup automático
python setup.py
```

O script vai:
- ✅ Verificar versão do Python
- ✅ Instalar dependências
- ✅ Configurar ambiente
- ✅ Criar diretórios necessários
- ✅ Rodar testes (opcional)

### Instalação Manual

Se preferir fazer manualmente:

```bash
# 1. Criar ambiente virtual (recomendado)
python -m venv .venv

# 2. Ativar ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
copy .env.example .env
# Edite .env conforme necessário

# 5. Validar configuração
python config.py

# 6. Rodar testes (opcional)
pytest
```

## 📖 Uso Básico

### 1. Baixar Fichas (Scraping)

```bash
python scraper_fichas_sebraetec.py
```

Isso vai:
- Acessar o site do Sebraetec
- Baixar todos os PDFs para `entrada/pdfs/`
- Mostrar progresso em tempo real

### 2. Processar Fichas (PDF → JSON)

```bash
# Processar todos os PDFs
python processar_fichas_batch.py

# Processar apenas os 5 primeiros (teste)
python processar_fichas_batch.py 5
```

Isso vai:
- Converter PDFs para Markdown
- Extrair dados estruturados
- Salvar JSONs em `saida/json/`

### 3. Validar Qualidade

```bash
# Analisar qualidade (threshold 70%)
python analisador_qualidade.py 70

# Validar integridade dos dados
python validador_integridade.py
```

### 4. Gerar TypeScript

```bash
# Gerar arquivo solutions-data.ts
python gerar_solutions_data.py
```

## 🔧 Configuração

### Arquivo .env

Copie `.env.example` para `.env` e ajuste:

```ini
# Scraper
SCRAPER_TIMEOUT=30          # Timeout em segundos
SCRAPER_DELAY=1.0           # Delay entre downloads
SCRAPER_MAX_RETRIES=3       # Máximo de tentativas

# Processamento
PROCESSAMENTO_PARALELO=false # Habilitar paralelização
NUM_WORKERS=4               # Número de workers

# Validação
SCORE_MINIMO_QUALIDADE=70.0 # Score mínimo aceitável

# Logging
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
```

## 🧪 Testes

### Rodar Todos os Testes

```bash
pytest
```

### Rodar com Cobertura

```bash
pytest --cov
```

### Rodar Testes Específicos

```bash
# Teste específico
pytest tests/test_models.py -v

# Teste por padrão
pytest -k "test_ficha"
```

## 📂 Estrutura de Diretórios

```
MarkItDown/
├── entrada/
│   └── pdfs/              # PDFs baixados
├── saida/
│   ├── *.md              # Markdowns convertidos
│   └── json/             # JSONs estruturados
├── logs/                  # Logs de execução
├── tests/                 # Testes unitários
├── config.py              # Configuração
├── logger_config.py       # Sistema de logging
├── models.py              # Modelos Pydantic
└── utils.py               # Utilitários
```

## 🐛 Solução de Problemas

### Erro: "markitdown não instalado"

```bash
pip install markitdown
```

### Erro: "Module not found"

```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: "Permission denied"

Execute como administrador ou verifique permissões dos diretórios.

### Logs não aparecem

Verifique `LOG_LEVEL` no arquivo `.env`:

```ini
LOG_LEVEL=DEBUG  # Para ver tudo
```

### Testes falhando

```bash
# Ver detalhes
pytest -v

# Debugger interativo
pytest --pdb
```

## 📊 Monitoramento

### Ver Logs

```bash
# Últimas linhas
tail -n 50 logs/sebraetec_pipeline_*.log

# Seguir em tempo real
tail -f logs/sebraetec_pipeline_*.log

# Windows PowerShell
Get-Content logs\sebraetec_pipeline_*.log -Tail 50
```

### Verificar Status

```bash
# Validar configuração
python config.py

# Estatísticas
python resumo_precos.py
python listar_codigos_sas.py
```

## 🔄 Workflow Recomendado

1. **Setup inicial**
   ```bash
   python setup.py
   ```

2. **Baixar PDFs**
   ```bash
   python scraper_fichas_sebraetec.py
   ```

3. **Processar**
   ```bash
   python processar_fichas_batch.py
   ```

4. **Validar**
   ```bash
   python analisador_qualidade.py 70
   python validador_integridade.py
   ```

5. **Gerar output final**
   ```bash
   python gerar_solutions_data.py
   ```

## 🆘 Suporte

1. Verifique logs em `logs/`
2. Execute com `LOG_LEVEL=DEBUG`
3. Consulte [MELHORIAS.md](MELHORIAS.md)
4. Abra issue no repositório

## 📚 Documentação Adicional

- [README_PIPELINE.md](README_PIPELINE.md) - Pipeline detalhado
- [MELHORIAS.md](MELHORIAS.md) - Documentação das melhorias
- [CONTEXTO_INTEGRACAO.md](CONTEXTO_INTEGRACAO.md) - Contexto do projeto

## ⚡ Dicas de Performance

### Processar em Paralelo

Edite `.env`:
```ini
PROCESSAMENTO_PARALELO=true
NUM_WORKERS=4
```

### Processar Incremental

Use os flags de "skip if exists" nos scripts - eles já verificam se arquivos existem antes de processar.

### Limpar Cache

```bash
# Windows
rmdir /s /q __pycache__
del /s *.pyc

# Linux/Mac
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## 🔐 Boas Práticas

1. **Sempre use ambiente virtual**
2. **Mantenha .env fora do git** (já está no .gitignore)
3. **Rode testes antes de commitar**
4. **Verifique logs após processamento**
5. **Faça backup dos JSONs gerados**

---

**Versão:** 2.0.0  
**Última atualização:** 22/01/2026  
**Status:** ✅ Produção
