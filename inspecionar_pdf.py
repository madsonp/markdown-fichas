import pdfplumber

pdf = pdfplumber.open('Tabela-de-Precos-Fichas-Tecnicas-Sebraetec-4.0-08-12-2025-1.pdf')
print(f'Total de páginas: {len(pdf.pages)}')

total_linhas = 0
linhas_com_preco = 0
linhas_sem_preco = 0

for i, page in enumerate(pdf.pages, 1):
    tables = page.extract_tables()
    if tables:
        for table in tables:
            for j, linha in enumerate(table[2:], start=2):  # Pular título e cabeçalhos
                if len(linha) >= 8 and linha[3]:  # Tem código
                    total_linhas += 1
                    preco = linha[7] if len(linha) > 7 else None
                    if preco and 'R$' in str(preco):
                        linhas_com_preco += 1
                    else:
                        linhas_sem_preco += 1
                        if linhas_sem_preco <= 10:  # Mostrar primeiros 10 sem preço
                            print(f'Sem preço - Código: {linha[3]}, Nome: {linha[2][:50] if len(linha) > 2 else "N/A"}')

print(f'\n📊 Resumo:')
print(f'Total de fichas: {total_linhas}')
print(f'Com preço: {linhas_com_preco}')
print(f'Sem preço (None): {linhas_sem_preco}')
