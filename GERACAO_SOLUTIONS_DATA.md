# Geração do Arquivo solutions-data.ts

## Visão Geral

O arquivo `solutions-data.ts` é gerado automaticamente a partir de todos os arquivos JSON na pasta `saida/json/`, consolidando as 317 fichas técnicas em um único arquivo TypeScript para consumo em aplicações frontend.

## Estrutura do Arquivo

```typescript
import { Solution } from './types/solution';

// Metadados da geração
// Data: 26/01/2026 [timestamp]
// Total de soluções: 317

export const solutionsData: Solution[] = [
  // Array com todas as soluções em formato JSON
];
```

## Processo de Geração

### Script Python

```python
import json
from pathlib import Path
from datetime import datetime

# Ler todos os JSONs
json_dir = Path('saida/json')
solutions = []

for json_file in sorted(json_dir.glob('*.json')):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            solutions.append(data)
    except Exception as e:
        print(f'Erro ao ler {json_file.name}: {e}')

# Gerar TypeScript
ts_content = f'''import {{ Solution }} from './types/solution';

// Dados de soluções - Gerado automaticamente a partir dos JSONs convertidos
// Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
// Total de soluções: {len(solutions)}
export const solutionsData: Solution[] = {json.dumps(solutions, ensure_ascii=False, indent=2)};
'''

# Salvar arquivo
with open('solutions-data.ts', 'w', encoding='utf-8') as f:
    f.write(ts_content)

print(f'✓ Arquivo solutions-data.ts gerado com {len(solutions)} soluções')
```

### Comando de Execução

```bash
python -c "
import json
from pathlib import Path
from datetime import datetime

json_dir = Path('saida/json')
solutions = []

for json_file in sorted(json_dir.glob('*.json')):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            solutions.append(data)
    except Exception as e:
        print(f'Erro ao ler {json_file.name}: {e}')

ts_content = f'''import {{ Solution }} from './types/solution';

// Dados de soluções - Gerado automaticamente a partir dos JSONs convertidos
// Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
// Total de soluções: {len(solutions)}
export const solutionsData: Solution[] = {json.dumps(solutions, ensure_ascii=False, indent=2)};
'''

with open('solutions-data.ts', 'w', encoding='utf-8') as f:
    f.write(ts_content)

print(f'✓ Arquivo solutions-data.ts gerado com {len(solutions)} soluções')
"
```

## Características

### Encoding UTF-8
- Todos os caracteres especiais preservados
- `ensure_ascii=False` no JSON para manter acentuação

### Ordenação
- Arquivos lidos em ordem alfabética (`sorted()`)
- Garante consistência entre gerações

### Tratamento de Erros
- Try/except individual para cada arquivo
- Continua processamento mesmo com erros
- Reporta arquivos problemáticos

## Estatísticas da Geração Atual

- **Data**: 26/01/2026
- **Total de soluções**: 317
- **Origem**: `saida/json/*.json`
- **Tamanho do arquivo**: ~34.000 linhas
- **Encoding**: UTF-8

## Correções Recentes

### Solução ESG (GS33017-1)
Corrigida manualmente antes da geração:

1. **nomeSolucao vazio** → Preenchido com título correto
2. **descricao vazia** → Adicionada descrição adequada do serviço
3. **Etapa 02 com título longo** → Removida descrição misturada no título

**Problema identificado**: O PDF original tinha erro estrutural (seção "9. Descrição" já começava com conteúdo de etapa ao invés de descrição geral).

## Uso no Frontend

```typescript
import { solutionsData } from './solutions-data';

// Filtrar soluções
const solucoesESG = solutionsData.filter(s => 
  s.tema === 'Sustentabilidade'
);

// Buscar por ID
const solucao = solutionsData.find(s => s.id === '33017-1');

// Total de soluções
console.log(`Total: ${solutionsData.length} soluções`);
```

## Quando Regenerar

Regenere o arquivo quando:

1. **Novos JSONs** adicionados em `saida/json/`
2. **Correções** aplicadas nos JSONs existentes
3. **Reprocessamento** completo das fichas
4. **Atualizações** de dados das soluções

## Integração com Git

O arquivo `solutions-data.ts` é **versionado** no repositório:
- ✅ Incluído no Git (não está no .gitignore)
- ✅ Permite rastreamento de mudanças
- ✅ Facilita deploy e distribuição

Os arquivos JSON individuais (`saida/json/`) são **ignorados** pelo Git:
- 🚫 Listados no .gitignore
- 🚫 Apenas o consolidado TypeScript é versionado
- 🚫 Reduz tamanho do repositório

## Histórico de Versões

### v6 - 26/01/2026
- 317 soluções
- Correção da solução ESG (GS33017-1)
- Todas as normalizações aplicadas:
  - Espaços duplos removidos
  - Quebras de linha removidas (título, etapas, histórico)
  - Detecção de duplicatas implementada

### v5 - 19/01/2026
- 314 soluções
- Primeira versão com todas as normalizações

---

**Nota**: Este arquivo é gerado automaticamente. Não edite manualmente. Use o script de geração para atualizar.
