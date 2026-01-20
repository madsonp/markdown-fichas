import codecs

# Verificar BOM
with open('solutions-data.ts', 'rb') as f:
    raw = f.read(500)
    has_bom = raw[:3] == b'\xef\xbb\xbf'
    print(f'✅ BOM UTF-8 presente: {has_bom}')

# Ler conteúdo
with codecs.open('solutions-data.ts', 'r', 'utf-8-sig') as f:
    content = f.read(400)
    print('\n📄 Primeiros 400 caracteres:')
    print(content)
    print(f'\n✅ Caracteres especiais corretos: {"soluções" in content and "ADEQUAÇÃO" in content}')

# Verificar alguns exemplos
print('\n🔍 Verificando palavras-chave:')
print(f'   - "soluções": {"✅" if "soluções" in content else "❌"}')
print(f'   - "ADEQUAÇÃO": {"✅" if "ADEQUAÇÃO" in content else "❌"}')
print(f'   - "Produção": {"✅" if "Produção" in content else "❌"}')
print(f'   - "Gestão": {"✅" if "Gestão" in content else "❌"}')
