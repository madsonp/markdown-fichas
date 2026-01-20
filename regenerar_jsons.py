import json
from extrator_ficha import ExtractorFichaTecnica

# Processar documento com histórico corrigido
print("📄 Processando documento de 3 versões...")
extractor = ExtractorFichaTecnica('saida/Otimização-da-Cadeia-de-Suprimentos-CS11003-3.md')
ficha_completa = extractor.extrair_todos_dados()
ficha_normalizada = extractor._normalizar_dados(ficha_completa)

with open('saida/json/Otimização-da-Cadeia-de-Suprimentos-CS11003-3.json', 'w', encoding='utf-8') as f:
    json.dump(ficha_normalizada, f, ensure_ascii=False, indent=2)

print('✓ JSON gerado com histórico corrigido')
print('Histórico:')
for h in ficha_normalizada.get('historicoAlteracoes', []):
    print(f"  Versão {h.get('versao')}: {h.get('dataAlteracao')} - {h.get('alteradoPor')}")

# Reprocessar outros documentos
print("\n" + "="*60)
arquivos = [
    'saida/Adequacao-de-processos-logisticos-para-exportacao-CI11004-1.md',
    'saida/Organizacao-e-Controle-de-Estoque-CS11002-3.md'
]

for arquivo_md in arquivos:
    print(f"\n📄 Processando: {arquivo_md.split('/')[-1]}")
    try:
        extrator = ExtractorFichaTecnica(arquivo_md)
        dados = extrator.extrair_todos_dados()
        dados_normalizados = extrator._normalizar_dados(dados)
        
        nome_json = arquivo_md.replace('saida/', '').replace('.md', '.json')
        caminho_json = f'saida/json/{nome_json}'
        
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(dados_normalizados, f, ensure_ascii=False, indent=2)
        
        print(f'✓ Salvo em: {caminho_json}')
        print(f"  Histórico: {len(dados_normalizados.get('historicoAlteracoes', []))} registros")
    except Exception as e:
        print(f'✗ Erro: {str(e)[:80]}')
