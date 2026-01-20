# Atualização dos Códigos SAS nas Soluções

## 📅 Data: 19/01/2026

## 🎯 Objetivo
Atualizar o campo `codigo` das soluções com o **Código SAS** presente na tabela de preços.

## 📋 Processo Executado

### 1. Análise da Estrutura
- **Tabela de preços**: `Tabela-de-Precos-Fichas-Tecnicas-Sebraetec-4.0-08-12-2025-1.pdf`
- **Estrutura identificada**:
  - Coluna 3: CÓDIGO (ID da ficha, ex: 41002-3)
  - Coluna 5: CÓDIGO SAS (ex: 371440100441)
  - Coluna 7: PREÇO MÁXIMO

### 2. Script Criado
**`atualizar_codigo_sas.py`**
- Extrai Códigos SAS do PDF usando pdfplumber
- Mapeia ID da ficha → Código SAS
- Atualiza campo `codigo` nos arquivos JSON
- Gera relatório de atualização

### 3. Execução

#### Extração do PDF
```
✅ 297 Códigos SAS extraídos do PDF
```

#### Atualização dos JSONs
```
✅ 265 arquivos JSON atualizados
⚠️  48 IDs não encontrados na tabela
❌ 0 erros
```

#### Regeneração do TypeScript
```
✅ Arquivo solutions-data.ts gerado
✅ 265/314 soluções com Código SAS (84.4%)
```

## 📊 Resultados

### Estatísticas Finais
- **Total de soluções**: 314
- **Com Código SAS**: 265 (84.4%)
- **Sem Código SAS**: 49 (15.6%)

### Exemplos de Códigos Atualizados
1. [14085-1] ADEQUAÇÃO AO PRIMARY FARM ASSURANCE → **372000113104**
2. [14084-1] ADEQUAÇÃO AO PROGRAMA DE CERTIFICAÇÃO QUALIDADE ABSOLAR → **372000113102**
3. [13079-1] ADEQUAÇÃO À NORMA ABNT NBR COMPONENTES CERÂMICOS → **372000096916**
4. [35019-3] ADEQUAÇÃO À NR-12 - SEGURANÇA NO TRABALHO → **371440100511**
5. [13050-5] ADEQUAÇÃO ÀS NORMAS ABNT NBR ISO 21101:2014 → **371440100268**

## 📄 Arquivos Gerados

1. **`atualizar_codigo_sas.py`**
   - Script principal de atualização
   - Extrai Código SAS do PDF
   - Atualiza JSONs

2. **`listar_codigos_sas.py`**
   - Gera relatório de cobertura
   - Lista soluções sem Código SAS

3. **`relatorio_codigos_sas.txt`**
   - Relatório completo com todas as soluções sem Código SAS

4. **`solutions-data.ts`** (atualizado)
   - Arquivo TypeScript com códigos SAS preenchidos

## ⚠️ Observações

### Soluções Sem Código SAS (49 fichas)
As soluções listadas abaixo não foram encontradas na tabela de preços e permaneceram sem Código SAS:

- [13070-5] ADEQUAÇÃO À LEI GERAL DE PROTEÇÃO DE DADOS PESSOAIS (LGPD)
- [13007-7] ADEQUAÇÃO DE AGROINDÚSTRIAS AOS SERVIÇOS DE INSPEÇÃO
- [13006-5] ADEQUAÇÃO AO PROGRAMA BRASILEIRO DA QUALIDADE
- [32001-2] ADEQUAÇÃO PARA ETIQUETAGEM EM USO EFICIENTE DE ENERGIA
- [35018-2] ADEQUAÇÃO À NR 10 – INSTALAÇÕES ELÉTRICAS
- [45001-2] DEPÓSITO DE PATENTE DE INVENÇÃO
- [45002-3] ELABORAÇÃO DE RECURSO
- [45003-2] REGISTRO - TOPOGRAFIA DE CIRCUITOS INTEGRADOS
- [45004-2] REGISTRO DE DESENHO INDUSTRIAL
- [45005-3] REGISTRO DE PROGRAMA DE COMPUTADOR
- E mais 39 outras fichas...

**Relatório completo**: `relatorio_codigos_sas.txt`

## 🔄 Como Reatualizar no Futuro

Se uma nova tabela de preços for disponibilizada:

```bash
# 1. Atualizar JSONs com nova tabela
python atualizar_codigo_sas.py caminho/nova_tabela_precos.pdf

# 2. Regenerar arquivo TypeScript
python gerar_solutions_data.py

# 3. Verificar cobertura
python listar_codigos_sas.py
```

## ✅ Status
**Concluído com sucesso!** O campo `codigo` agora está preenchido com o Código SAS da tabela de preços em 84.4% das soluções.
