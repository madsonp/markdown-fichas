import json
import os

dados = []
for f in os.listdir('saida/json')[:50]:
    try:
        with open(os.path.join('saida', 'json', f), 'r', encoding='utf-8') as file:
            data = json.load(file)
            dados.append((f, data.get('valorTeto', 0)))
    except:
        pass

print('Top 20 fichas com maior valorTeto:')
for i, (nome, valor) in enumerate(sorted(dados, key=lambda x: x[1], reverse=True)[:20], 1):
    print(f'{i}. {nome[:55]:<55} R$ {valor:>12,.2f}')

print(f'\n📊 Resumo:')
com_preco = [v for _, v in dados if v > 0]
sem_preco = [v for _, v in dados if v == 0]
print(f'Com preço (>0): {len(com_preco)} fichas')
print(f'Sem preço (=0): {len(sem_preco)} fichas')
if com_preco:
    print(f'Preço médio: R$ {sum(com_preco)/len(com_preco):,.2f}')
