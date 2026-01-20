import pdfplumber

pdf = pdfplumber.open('Tabela-de-Precos-Fichas-Tecnicas-Sebraetec-4.0-08-12-2025-1.pdf')

print("Analisando primeiros 20 registros COM preço:")
count = 0
for page in pdf.pages:
    tables = page.extract_tables()
    if tables:
        for table in tables:
            for linha in table[2:]:  # Pular título e cabeçalhos
                if len(linha) >= 8 and linha[3]:
                    codigo = linha[3]
                    preco = linha[7] if len(linha) > 7 else None
                    if preco:
                        count += 1
                        print(f"{count}. Código: {codigo}, Preço raw: '{preco}', Tem R$: {'R$' in str(preco)}")
                        if count >= 20:
                            break
            if count >= 20:
                break
    if count >= 20:
        break
