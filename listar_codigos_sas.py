"""
Script para listar as soluções que não têm Código SAS.
"""
import json
from pathlib import Path

def listar_solucoes_sem_codigo_sas():
    """Lista todas as soluções que não têm Código SAS."""
    
    pasta_json = Path('saida/json')
    arquivos_json = list(pasta_json.glob('*.json'))
    
    sem_codigo = []
    com_codigo = []
    
    print("="*80)
    print("📋 RELATÓRIO DE CÓDIGOS SAS")
    print("="*80)
    
    for json_file in sorted(arquivos_json):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            ficha_id = dados.get('id', '')
            nome = dados.get('nomeSolucao', '')
            codigo = dados.get('codigo', '')
            
            if codigo and codigo != '':
                com_codigo.append({
                    'id': ficha_id,
                    'nome': nome[:60] + '...' if len(nome) > 60 else nome,
                    'codigo': codigo
                })
            else:
                sem_codigo.append({
                    'id': ficha_id,
                    'nome': nome[:60] + '...' if len(nome) > 60 else nome
                })
        except Exception as e:
            print(f"❌ Erro ao processar {json_file.name}: {e}")
    
    total = len(arquivos_json)
    total_com_codigo = len(com_codigo)
    total_sem_codigo = len(sem_codigo)
    cobertura = (total_com_codigo / total * 100) if total > 0 else 0
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de soluções: {total}")
    print(f"   ✅ Com Código SAS: {total_com_codigo} ({cobertura:.1f}%)")
    print(f"   ⚠️  Sem Código SAS: {total_sem_codigo} ({100-cobertura:.1f}%)")
    
    if com_codigo:
        print(f"\n✅ PRIMEIROS 10 COM CÓDIGO SAS:")
        for i, item in enumerate(com_codigo[:10], 1):
            print(f"   {i:2d}. [{item['id']}] {item['nome']}")
            print(f"       → Código SAS: {item['codigo']}")
    
    if sem_codigo:
        print(f"\n⚠️  SOLUÇÕES SEM CÓDIGO SAS ({len(sem_codigo)} no total):")
        for i, item in enumerate(sem_codigo, 1):
            print(f"   {i:2d}. [{item['id']}] {item['nome']}")
    
    print(f"\n{'='*80}")
    
    # Salvar relatório em arquivo
    with open('relatorio_codigos_sas.txt', 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE CÓDIGOS SAS\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total de soluções: {total}\n")
        f.write(f"Com Código SAS: {total_com_codigo} ({cobertura:.1f}%)\n")
        f.write(f"Sem Código SAS: {total_sem_codigo} ({100-cobertura:.1f}%)\n\n")
        
        f.write("SOLUÇÕES SEM CÓDIGO SAS:\n")
        f.write("-"*80 + "\n")
        for i, item in enumerate(sem_codigo, 1):
            f.write(f"{i:3d}. [{item['id']}] {item['nome']}\n")
    
    print(f"📄 Relatório salvo em: relatorio_codigos_sas.txt")
    
    return {
        'total': total,
        'com_codigo': total_com_codigo,
        'sem_codigo': total_sem_codigo,
        'cobertura': cobertura
    }

if __name__ == "__main__":
    listar_solucoes_sem_codigo_sas()
