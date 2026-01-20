import pdfplumber
import pandas as pd

pdf = pdfplumber.open('Tabela-de-Precos-Fichas-Tecnicas-Sebraetec-4.0-08-12-2025-1.pdf')

todos_dados = []
erros = []

for page_num, page in enumerate(pdf.pages, 1):
    tables = page.extract_tables()
    if not tables:
        continue
    
    for tabela in tables:
        if len(tabela) > 2 and tabela[1][0] and 'CÓDIGO' in str(tabela[1][0]).upper():
            for idx, linha in enumerate(tabela[2:], start=2):
                if len(linha) >= 8 and linha[3]:
                    codigo = linha[3]
                    preco_str = linha[7] if len(linha) > 7 else None
                    
                    if preco_str and 'R$' in str(preco_str):
                        preco_limpo = preco_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
                        try:
                            preco = float(preco_limpo)
                            todos_dados.append({'id': codigo, 'valorTeto': preco})
                        except Exception as e:
                            erros.append({
                                'codigo': codigo,
                                'preco_original': preco_str,
                                'preco_limpo': preco_limpo,
                                'erro': str(e)
                            })

print(f"✅ Preços extraídos: {len(todos_dados)}")
print(f"❌ Erros: {len(erros)}")

if erros:
    print("\nPrimeiros 5 erros:")
    for i, erro in enumerate(erros[:5], 1):
        print(f"{i}. Código: {erro['codigo']}")
        print(f"   Original: '{erro['preco_original']}'")
        print(f"   Limpo: '{erro['preco_limpo']}'")
        print(f"   Erro: {erro['erro']}\n")

if todos_dados:
    print(f"\nPrimeiros 5 preços extraídos:")
    for i, dado in enumerate(todos_dados[:5], 1):
        print(f"{i}. {dado}")
