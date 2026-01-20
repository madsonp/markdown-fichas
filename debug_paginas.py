import pdfplumber

pdf = pdfplumber.open('Tabela-de-Precos-Fichas-Tecnicas-Sebraetec-4.0-08-12-2025-1.pdf')

for page_num, page in enumerate(pdf.pages, 1):
    tables = page.extract_tables()
    if tables:
        for table in tables:
            print(f"\nPágina {page_num}:")
            print(f"  Linha 0: {table[0]}")
            print(f"  Linha 1: {table[1][:2] if len(table) > 1 else 'N/A'}")
            print(f"  Tem 'CÓDIGO' na linha 1? {('CÓDIGO' in str(table[1][0]).upper()) if len(table) > 1 and table[1][0] else False}")
            
            # Contar linhas com preço
            com_preco = 0
            for linha in table[2:]:
                if len(linha) >= 8 and linha[3]:
                    preco = linha[7] if len(linha) > 7 else None
                    if preco and 'R$' in str(preco):
                        com_preco += 1
            print(f"  Linhas com preço: {com_preco}")
