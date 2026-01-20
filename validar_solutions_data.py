"""
Script para validar solution-data-novo.ts
Verifica:
- Sintaxe JSON/TypeScript válida
- Campos obrigatórios preenchidos
- Tipos de dados corretos
- IDs únicos
"""

import json
import re
from pathlib import Path

def validar_arquivo():
    """Valida solution-data-novo.ts"""
    
    print("🔍 VALIDAÇÃO DE solutions-data-novo.ts\n")
    print("=" * 80)
    
    # Ler arquivo
    try:
        with open('solutions-data-novo.ts', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        print("✓ Arquivo lido com sucesso")
    except Exception as e:
        print(f"✗ Erro ao ler arquivo: {e}")
        return False
    
    # Extrair JSON
    try:
        match = re.search(r'export const solutionsData: Solution\[\] = \[(.*)\];', conteudo, re.DOTALL)
        if not match:
            print("✗ Não encontrou array solutionsData")
            return False
        
        json_str = '[' + match.group(1) + ']'
        solucoes = json.loads(json_str)
        print(f"✓ JSON parseado com sucesso ({len(solucoes)} soluções)")
    except json.JSONDecodeError as e:
        print(f"✗ Erro ao fazer parse JSON: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("VALIDAÇÃO DE CAMPOS")
    print("=" * 80)
    
    # Campos obrigatórios
    campos_obrigatorios = [
        'id', 'nomeSolucao', 'codigo', 'tema', 'subtema', 
        'tipoServico', 'modalidade', 'publicoAlvo',
        'descricao', 'beneficiosResultadosEsperados',
        'estruturaMateriais', 'responsabilidadeEmpresaDemandante',
        'responsabilidadePrestadora', 'perfilDesejadoPrestadora',
        'etapas', 'perguntasDiagnostico', 'observacoesGerais',
        'historicoAlteracoes', 'setorial', 'valorTeto'
    ]
    
    # Campos recomendados
    campos_recomendados = [
        'ods', 'estadosDisponiveis', 'editalPorEstado',
        'objetivo', 'versaoAtual', 'status'
    ]
    
    ids_vistos = set()
    erros = 0
    avisos = 0
    
    for i, sol in enumerate(solucoes, 1):
        print(f"\n📄 Solução {i}: {sol.get('id', '???')}")
        
        # Verificar ID único
        if sol.get('id') in ids_vistos:
            print(f"  ✗ ID duplicado: {sol.get('id')}")
            erros += 1
        else:
            ids_vistos.add(sol.get('id'))
            print(f"  ✓ ID único")
        
        # Verificar campos obrigatórios
        campos_faltando = []
        campos_vazios = []
        
        for campo in campos_obrigatorios:
            if campo not in sol:
                campos_faltando.append(campo)
            elif not sol[campo] and sol[campo] != 0:  # Permite 0 como valor válido
                campos_vazios.append(campo)
        
        if campos_faltando:
            print(f"  ✗ Campos faltando: {', '.join(campos_faltando)}")
            erros += len(campos_faltando)
        
        if campos_vazios:
            print(f"  ⚠️  Campos vazios: {', '.join(campos_vazios)}")
            avisos += len(campos_vazios)
        
        # Verificar tipos específicos
        if not isinstance(sol.get('publicoAlvo'), list):
            print(f"  ✗ 'publicoAlvo' deve ser array")
            erros += 1
        
        if not isinstance(sol.get('etapas'), list):
            print(f"  ✗ 'etapas' deve ser array")
            erros += 1
        
        if not isinstance(sol.get('perguntasDiagnostico'), list):
            print(f"  ✗ 'perguntasDiagnostico' deve ser array")
            erros += 1
        
        if not isinstance(sol.get('historicoAlteracoes'), list):
            print(f"  ✗ 'historicoAlteracoes' deve ser array")
            erros += 1
        
        # Verificar campos recomendados
        campos_rec_faltando = [c for c in campos_recomendados if c not in sol or not sol.get(c)]
        if campos_rec_faltando:
            print(f"  ⚠️  Campos recomendados faltando: {', '.join(campos_rec_faltando[:3])}")
            avisos += 1
        
        # Verificar `codigo`
        if not sol.get('codigo'):
            print(f"  🔴 CRÍTICO: 'codigo' está vazio!")
            erros += 1
        
        # Verificar `ods`
        if not sol.get('ods'):
            print(f"  🔴 CRÍTICO: 'ods' está vazio!")
            erros += 1
        
        # Verificar `estadosDisponiveis`
        if not sol.get('estadosDisponiveis'):
            print(f"  🔴 CRÍTICO: 'estadosDisponiveis' está vazio!")
            erros += 1
    
    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 80)
    print(f"\n✓ Soluções válidas: {len(solucoes)}")
    print(f"✓ IDs únicos: {len(ids_vistos)}")
    print(f"✗ Erros críticos: {erros}")
    print(f"⚠️  Avisos: {avisos}")
    
    status = "❌ FALHOU" if erros > 0 else "⚠️  COM AVISOS" if avisos > 0 else "✅ SUCESSO"
    print(f"\n{status}")
    
    if erros > 0:
        print("\nⓘ  Corrija os erros críticos antes de usar o arquivo")
    
    return erros == 0

# Executar
if __name__ == "__main__":
    sucesso = validar_arquivo()
    exit(0 if sucesso else 1)
