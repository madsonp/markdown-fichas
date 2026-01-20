# Correção de Encoding UTF-8 no Windows

## 🐛 Problema Identificado

Ao visualizar o arquivo `solutions-data.ts` no PowerShell usando `Get-Content` sem especificar o encoding, caracteres especiais apareciam corrompidos:

```
❌ ANTES: "soluÃ§Ãµes" (corrompido)
✅ DEPOIS: "soluções" (correto)

❌ ANTES: "ADEQUAÃ‡ÃƒO" (corrompido)
✅ DEPOIS: "ADEQUAÇÃO" (correto)
```

## 🔍 Causa Raiz

O arquivo estava sendo salvo com **UTF-8 sem BOM** (Byte Order Mark). No Windows, quando o PowerShell lê um arquivo sem BOM, ele assume o encoding padrão do sistema (geralmente Windows-1252 ou similar), causando a corrupção de caracteres especiais.

### Detalhes Técnicos:
- **Python salvava**: UTF-8 sem BOM (`encoding='utf-8'`)
- **PowerShell lia**: Encoding padrão do Windows (não UTF-8)
- **Resultado**: Caracteres UTF-8 interpretados incorretamente

## ✅ Solução Implementada

### Mudança no Script `gerar_solutions_data.py`

**Linha 180 - ANTES:**
```python
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(typescript_code)
```

**Linha 180 - DEPOIS:**
```python
# Salvar arquivo com UTF-8 BOM para melhor compatibilidade no Windows
with open(output_file, 'w', encoding='utf-8-sig') as f:
    f.write(typescript_code)
```

### O que mudou?

- **`utf-8`**: UTF-8 sem BOM (não detectado automaticamente pelo Windows)
- **`utf-8-sig`**: UTF-8 com BOM (`0xEF 0xBB 0xBF`) - detectado automaticamente

## 🧪 Verificação

### Teste 1: Verificar presença do BOM
```bash
python -c "with open('solutions-data.ts', 'rb') as f: bom = f.read(3); print('BOM:', bom)"
```
**Resultado esperado:** `BOM: b'\xef\xbb\xbf'`

### Teste 2: Leitura no PowerShell sem especificar encoding
```powershell
Get-Content "solutions-data.ts" -Head 10
```
**Resultado esperado:** Caracteres especiais exibidos corretamente

### Teste 3: Leitura em editores
- Visual Studio Code ✅
- Notepad ✅
- Notepad++ ✅
- PowerShell ✅

## 📝 Por que UTF-8 BOM?

### Vantagens:
1. ✅ **Compatibilidade Windows**: Detectado automaticamente pelo PowerShell e editores Windows
2. ✅ **Transparente**: Não interfere na execução do código TypeScript/JavaScript
3. ✅ **Padrão**: Recomendado pela Microsoft para arquivos de texto no Windows

### Desvantagens:
- ⚠️ Adiciona 3 bytes no início do arquivo (desprezível)
- ⚠️ Alguns sistemas Unix podem exibir caracteres estranhos (raro)

## 🎯 Impacto

- ✅ **Arquivos TypeScript (.ts)**: Agora usam UTF-8 BOM
- ℹ️ **Arquivos JSON (.json)**: Mantêm UTF-8 sem BOM (JSON não aceita BOM)
- ℹ️ **Arquivos TXT (.txt)**: UTF-8 sem BOM (aceitável para logs)

## 🔄 Para Aplicar a Correção

1. **Regenerar o arquivo TypeScript:**
   ```bash
   python gerar_solutions_data.py
   ```

2. **Verificar encoding:**
   ```powershell
   Get-Content "solutions-data.ts" -Head 5
   ```

3. **Se ainda houver problemas:**
   ```bash
   # Forçar UTF-8 BOM manualmente
   python -c "content = open('solutions-data.ts', 'r', encoding='utf-8').read(); open('solutions-data.ts', 'w', encoding='utf-8-sig').write(content)"
   ```

## 📚 Referências

- [Python codecs - utf-8-sig](https://docs.python.org/3/library/codecs.html#module-encodings.utf_8_sig)
- [UTF-8 BOM (Byte Order Mark)](https://en.wikipedia.org/wiki/Byte_order_mark#UTF-8)
- [PowerShell encoding issues](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding)

## ✅ Status

**RESOLVIDO** - O arquivo `solutions-data.ts` agora é salvo com UTF-8 BOM e pode ser lido corretamente pelo PowerShell e todos os editores no Windows sem especificar encoding explícito.

**Data da correção**: 19/01/2026 17:41
