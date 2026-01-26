# Critério de Qualidade: Entregas Duplicadas

## Data: 26/01/2026

## Objetivo
Adicionar validação para identificar soluções com entregas repetidas nas etapas, reduzindo a qualidade quando há duplicações.

## Análise Inicial

### Estatísticas
- **Total de arquivos analisados**: 317
- **Soluções COM duplicatas**: 6 (1.9%)
- **Soluções SEM duplicatas**: 311 (98.1%)
- **Total de duplicatas encontradas**: 12

### Casos Mais Críticos

1. **Cultivo-protegido-em-propriedades-rurais-MMP14043-2.json** (ID: 14043-2)
   - Total etapas: 8 | Únicas: 3 | Duplicatas: 5
   - Entrega repetida 6x: "Relatório assinado pelo produtor e pelo consultor, contendo..."

2. **Manejo-para-Aumento-da-Produtividade-na-Producao-de-Mel-e-Derivados-MMP14023-3.json** (ID: 14023-3)
   - Total etapas: 6 | Únicas: 3 | Duplicatas: 3
   - Entrega repetida 4x: "Relatório assinado pelo produtor e pelo consultor contendo a..."

3. **Implantacao-do-Sis.-de-Geren.-da-Integridade-Est.-das-Inst.-Terrestres-de-Producao-de-Petroleo-e-Gas-Natural-RTSGI-SST35020-3.json** (ID: 35020-3)
   - Total etapas: 3 | Únicas: 2 | Duplicatas: 1
   - Entrega repetida 2x: "Relatório com o resumo das atividades definidas nessa etapa...."

## Implementação

### 1. Script de Análise
Criado [scripts/analisar_entregas_duplicadas.py](scripts/analisar_entregas_duplicadas.py) para:
- Analisar todos os JSONs
- Identificar entregas duplicadas usando `Counter`
- Gerar relatório detalhado em JSON
- Exibir top 20 soluções com mais duplicatas

### 2. Atualização do Analisador de Qualidade

#### Arquivo: [analisador_qualidade.py](analisador_qualidade.py)

**Alterações:**
1. Adicionado peso `entregas_sem_duplicatas: 5` em PESOS_QUALIDADE
2. Nova lógica de validação:
   ```python
   from collections import Counter
   entregas = [etapa.get('entrega', '').strip() for etapa in etapas if etapa.get('entrega', '').strip()]
   
   if len(entregas) > 0:
       contador = Counter(entregas)
       duplicadas = {entrega: count for entrega, count in contador.items() if count > 1}
       
       if not duplicadas:
           # Sem duplicatas = pontuação completa
           score += self.PESOS.get('entregas_sem_duplicatas', 5)
       else:
           # Com duplicatas = penalização proporcional
           num_duplicatas = sum(count - 1 for count in duplicadas.values())
           problemas.append(f"Entregas duplicadas: {num_duplicatas} repetição(ões) em {len(duplicadas)} entrega(s)")
           
           penalidade = min(num_duplicatas / len(entregas), 1.0)
           score += self.PESOS.get('entregas_sem_duplicatas', 5) * (1 - penalidade)
   ```

#### Arquivo: [config.py](config.py)

**Alterações:**
```python
PESOS_QUALIDADE: Dict[str, int] = {
    "campo_obrigatorio_presente": 10,
    "campo_obrigatorio_preenchido": 5,
    "campo_importante_preenchido": 3,
    "beneficios_tamanho": 2,
    "etapas_quantidade": 2,
    "descricao_presente": 3,
    "responsabilidades_presentes": 2,
    "entregas_sem_duplicatas": 5  # Novo critério
}
```

## Testes

### Teste 1: Solução COM Duplicatas
**Arquivo:** Cultivo-protegido-em-propriedades-rurais-MMP14043-2.json

**Resultado:**
- Score: **97.5%**
- Problemas: "Entregas duplicadas: 5 repetição(ões) em 1 entrega(s)"
- Penalização: Redução proporcional de até 5 pontos

### Teste 2: Solução SEM Duplicatas
**Arquivo:** Adequacao-a-Lei-Geral-de-Protecao-de-Dados-LGPD-GQ13070-5.json

**Resultado:**
- Score: **96.0%**
- Problemas: Outros (descrição curta, responsabilidades)
- Sem penalização por duplicatas

## Cálculo da Penalização

A penalização é calculada proporcionalmente:

```python
penalidade = min(num_duplicatas / len(entregas), 1.0)
score += peso * (1 - penalidade)
```

**Exemplos:**
- 5 duplicatas em 8 entregas: penalidade = 0.625 → score reduzido em ~62.5% do peso (3.125 pontos)
- 1 duplicata em 3 entregas: penalidade = 0.333 → score reduzido em ~33.3% do peso (1.67 pontos)
- 0 duplicatas: penalidade = 0 → pontuação completa (5 pontos)

## Impacto

### Benefícios
1. **Detecção automática** de problemas de qualidade na extração
2. **Penalização proporcional** ao número de duplicatas
3. **Relatório detalhado** das entregas repetidas
4. **Visibilidade** de soluções que precisam revisão manual

### Melhorias Futuras
1. Normalizar entregas antes de comparar (remover pontuação, maiúsculas)
2. Detectar entregas "similares" (não apenas duplicatas exatas)
3. Sugerir consolidação automática de etapas duplicadas
4. Adicionar critério de "densidade de informação" nas entregas

## Arquivos Criados/Modificados

### Criados
1. [scripts/analisar_entregas_duplicadas.py](scripts/analisar_entregas_duplicadas.py) - Script de análise
2. [scripts/testar_criterio_duplicatas.py](scripts/testar_criterio_duplicatas.py) - Script de teste
3. [relatorio_entregas_duplicadas.json](relatorio_entregas_duplicadas.json) - Relatório gerado
4. Este documento de documentação

### Modificados
1. [analisador_qualidade.py](analisador_qualidade.py) - Adicionada validação de duplicatas
2. [config.py](config.py) - Adicionado peso `entregas_sem_duplicatas`

## Execução

### Análise Completa de Duplicatas
```bash
python scripts/analisar_entregas_duplicadas.py
```

### Teste do Novo Critério
```bash
python scripts/testar_criterio_duplicatas.py
```

### Análise de Qualidade Geral
```bash
python analisador_qualidade.py
```

## Conclusão

O novo critério de **entregas duplicadas** foi implementado com sucesso, detectando 6 soluções (1.9%) com problemas de duplicação. A penalização é proporcional e justa, permitindo identificar fichas que necessitam revisão manual para melhorar a qualidade dos dados extraídos.
