"""
Script para mesclar JSONs novos com solutions-data.ts existente
Permite adicionar novas soluções sem sobrescrever as existentes
"""

import json
import glob
import re
from pathlib import Path
from datetime import datetime

def extrair_solucoes_do_ts(arquivo_ts):
    """Extrai array de soluções do arquivo TypeScript"""
    with open(arquivo_ts, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Encontrar o array solutionsData
    match = re.search(r'export const solutionsData: Solution\[\] = \[(.*)\];', conteudo, re.DOTALL)
    if not match:
        return []
    
    # Extrair JSON do conteúdo
    json_str = '[' + match.group(1) + ']'
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print("⚠️  Erro ao fazer parse do TypeScript existente")
        return []

def comparar_solucoes(existentes, novas):
    """Compara soluções e identifica duplicatas e novas"""
    ids_existentes = {s['id'] for s in existentes}
    
    duplicatas = []
    novas_somas = []
    
    for solucao_nova in novas:
        if solucao_nova['id'] in ids_existentes:
            duplicatas.append(solucao_nova['id'])
        else:
            novas_somas.append(solucao_nova)
    
    return duplicatas, novas_somas

# Carregar soluções existentes
print("📂 Carregando solutions-data.ts existente...")
try:
    solucoes_existentes = extrair_solucoes_do_ts('solutions-data.ts')
    print(f"✓ Encontradas {len(solucoes_existentes)} soluções existentes")
except Exception as e:
    print(f"⚠️  Erro ao carregar existentes: {e}")
    solucoes_existentes = []

# Carregar novas soluções do novo arquivo
print("\n📂 Carregando solutions-data-novo.ts...")
try:
    with open('solutions-data-novo.ts', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    match = re.search(r'export const solutionsData: Solution\[\] = \[(.*)\];', conteudo, re.DOTALL)
    if match:
        json_str = '[' + match.group(1) + ']'
        solucoes_novas = json.loads(json_str)
        print(f"✓ Encontradas {len(solucoes_novas)} soluções novas")
    else:
        print("✗ Não foi possível extrair soluções do novo arquivo")
        solucoes_novas = []
except Exception as e:
    print(f"✗ Erro ao carregar novo: {e}")
    solucoes_novas = []

# Comparar
if solucoes_existentes and solucoes_novas:
    duplicatas, novas = comparar_solucoes(solucoes_existentes, solucoes_novas)
    
    print("\n" + "=" * 80)
    print("ANÁLISE DE MESCLAGEM")
    print("=" * 80)
    
    print(f"\n🔄 Duplicatas (atualizadas em novo): {len(duplicatas)}")
    for id_dup in duplicatas:
        print(f"   - {id_dup}")
    
    print(f"\n✨ Novas soluções: {len(novas)}")
    for sol in novas:
        print(f"   - {sol['id']}: {sol['nomeSolucao'][:50]}")
    
    # Estratégias de mesclagem
    print("\n" + "=" * 80)
    print("OPÇÕES DE MESCLAGEM")
    print("=" * 80)
    print("""
1. SUBSTITUIR TUDO
   - Usa todas as soluções do novo arquivo
   - Comando: copy solutions-data-novo.ts solutions-data.ts
   
2. MESCLAR (manter existentes + adicionar novas)
   - Mantém soluções existentes
   - Adiciona soluções que não existem
   - Usa este script com flag --merge
   
3. ATUALIZAR APENAS NOVAS
   - Ignora duplicatas
   - Adiciona apenas novas soluções
   - Comando: python merge_solutions.py --new-only
""")
    
    # Opção padrão: apenas informar
    print("=" * 80)
    print("PRÓXIMOS PASSOS")
    print("=" * 80)
    print("""
a) Revisar solutions-data-novo.ts
b) Preencherá campos manual (codigo, ods, estados, etc)
c) Executar: python merge_solutions.py --merge
d) Validar: npm run lint (ou similar)
e) Commit: git commit -m "chore: atualizar solutions-data com novas fichas"
""")
