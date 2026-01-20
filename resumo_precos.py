import json
import os

dados = []
for f in os.listdir('saida/json'):
    try:
        with open(os.path.join('saida', 'json', f), 'r', encoding='utf-8') as file:
            data = json.load(file)
            dados.append((f, data.get('valorTeto', 0), data.get('id', 'N/A')))
    except Exception as e:
        print(f'❌ Erro ao ler {f}: {e}')

print(f'📊 RESUMO FINAL DA ATUALIZAÇÃO DE PREÇOS')
print(f'=' * 70)
print(f'Total de arquivos JSON: {len(dados)}')

com_preco = [d for d in dados if d[1] > 0]
sem_preco = [d for d in dados if d[1] == 0]

print(f'\n✅ Com preço (valorTeto > 0): {len(com_preco)} fichas')
print(f'⚠️  Sem preço (valorTeto = 0): {len(sem_preco)} fichas')

if com_preco:
    valores = [d[1] for d in com_preco]
    print(f'\n💰 Estatísticas de preços:')
    print(f'   Preço mínimo: R$ {min(valores):,.2f}')
    print(f'   Preço médio:  R$ {sum(valores)/len(valores):,.2f}')
    print(f'   Preço máximo: R$ {max(valores):,.2f}')
    print(f'   Total:        R$ {sum(valores):,.2f}')

# Distribuição de preços
faixas = [
    (0, 5000, '0-5k'),
    (5000, 10000, '5k-10k'),
    (10000, 20000, '10k-20k'),
    (20000, 30000, '20k-30k'),
    (30000, 100000, '30k-100k'),
    (100000, float('inf'), '100k+')
]

print(f'\n📊 Distribuição de preços:')
for min_val, max_val, label in faixas:
    count = len([d for d in com_preco if min_val <= d[1] < max_val])
    if count > 0:
        print(f'   {label:>10}: {count:>3} fichas')
