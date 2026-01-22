"""
Gera arquivo TypeScript com dados das soluções
Inclui validação Pydantic e enriquecimento de dados
"""
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

try:
    from config import SAIDA_JSON_DIR, OUTPUT_ENCODING, OUTPUT_INDENT
    from logger_config import setup_logger, LogContext
    from models import FichaTecnica
    logger = setup_logger(__name__)
    USE_PYDANTIC = True
except ImportError:
    SAIDA_JSON_DIR = Path("saida/json")
    OUTPUT_ENCODING = "utf-8-sig"
    OUTPUT_INDENT = 2
    USE_PYDANTIC = False

def converter_setor_para_setorial(setor_str):
    """Converte 'setor' string para 'setorial' array"""
    if not setor_str:
        return ["transversal"]
    
    # Dividir por vírgula e limpar espaços
    setores = [s.strip().lower() for s in setor_str.split(',')]
    
    # Mapear nomes comuns
    mapeamento = {
        'agronegócios': 'agronegócios',
        'comércio': 'comercio',
        'indústria': 'industria',
        'serviços': 'servicos',
        'tecnologia': 'tecnologia',
        'transversal': 'transversal',
    }
    
    resultado = []
    for setor in setores:
        # Se tem mapeamento, usar; senão, usar como está
        resultado.append(mapeamento.get(setor, setor))
    
    return resultado if resultado else ["transversal"]

def enriquecer_solucao(dados_json: Dict[str, Any], indice: int) -> Dict[str, Any]:
    """
    Adiciona campos faltantes ao JSON da solução
    Agora com validação Pydantic opcional
    """
    try:
        # Se temos Pydantic, validar primeiro
        if USE_PYDANTIC:
            try:
                ficha = FichaTecnica(**dados_json)
                # Retornar dados validados e normalizados
                return ficha.to_dict()
            except Exception as e:
                if USE_PYDANTIC:
                    logger.warning(f"Validação Pydantic falhou, usando fallback: {e}")
                # Continua com método antigo se validação falhar
        
        # Método antigo (fallback)
        return enriquecer_solucao_legacy(dados_json, indice)
    
    except Exception as e:
        if USE_PYDANTIC:
            logger.error(f"Erro ao enriquecer solução: {e}")
        return dados_json


def enriquecer_solucao_legacy(dados_json: Dict[str, Any], indice: int) -> Dict[str, Any]:
    """Método legado de enriquecimento sem Pydantic"""
    dados = dados_json.copy()
    
    # Mapear 'setor' para 'setorial' se existir
    if 'setor' in dados and 'setorial' not in dados:
        dados['setorial'] = converter_setor_para_setorial(dados.pop('setor'))
    elif 'setor' in dados:
        del dados['setor']
    
    # Campos com valores padrão
    if 'valorTeto' not in dados:
        dados['valorTeto'] = 0  # Será preenchido com tabela de preços
    
    if 'dataAtualizacaoEscopo' not in dados:
        dados['dataAtualizacaoEscopo'] = datetime.now().strftime("%d/%m/%Y")
    
    if 'dataAtualizacaoValor' not in dados:
        dados['dataAtualizacaoValor'] = datetime.now().strftime("%d/%m/%Y")
    
    if 'ods' not in dados:
        dados['ods'] = []  # Array vazio
    
    if 'estadosDisponiveis' not in dados:
        dados['estadosDisponiveis'] = []
    
    if 'editalPorEstado' not in dados:
        dados['editalPorEstado'] = {}
    
    if 'objetivo' not in dados:
        # Gerar objetivo a partir da descrição ou usando valor padrão
        dados['objetivo'] = dados.get('descricao', '')[:100] + "..."
    
    if 'observacoesEspecificas' not in dados:
        dados['observacoesEspecificas'] = ""
    
    if 'versaoAtual' not in dados:
        dados['versaoAtual'] = 1
    
    # Campos meta (preenchimento posterior)
    if 'status' not in dados:
        dados['status'] = 'ativa'
    
    if 'criadoEm' not in dados:
        dados['criadoEm'] = datetime.now().strftime("%d/%m/%Y")
    
    if 'criadoPor' not in dados:
        dados['criadoPor'] = 'Sistema'
    
    if 'atualizadoEm' not in dados:
        dados['atualizadoEm'] = datetime.now().strftime("%d/%m/%Y")
    
    if 'codigoCdt' not in dados:
        dados['codigoCdt'] = ""  # Será preenchido manualmente
    
    if 'unidade' not in dados:
        dados['unidade'] = ""  # Será preenchido manualmente
    
    if 'numeroOferta' not in dados:
        dados['numeroOferta'] = ""  # Será preenchido manualmente
    
    # Enriquecer historicoAlteracoes com campos faltantes
    if 'historicoAlteracoes' in dados and isinstance(dados['historicoAlteracoes'], list):
        for alteracao in dados['historicoAlteracoes']:
            if 'camposAlterados' not in alteracao:
                alteracao['camposAlterados'] = []
            if 'descricao' not in alteracao:
                alteracao['descricao'] = f"Versão {alteracao.get('versao', '?')}"
    
    # Ordenar campos para consistência
    campos_ordenados = {
        'id': dados.get('id'),
        'nomeSolucao': dados.get('nomeSolucao'),
        'codigo': dados.get('codigo'),
        'valorTeto': dados.get('valorTeto'),
        'dataAtualizacaoEscopo': dados.get('dataAtualizacaoEscopo'),
        'dataAtualizacaoValor': dados.get('dataAtualizacaoValor'),
        'tema': dados.get('tema'),
        'subtema': dados.get('subtema'),
        'tipoServico': dados.get('tipoServico'),
        'modalidade': dados.get('modalidade'),
        'setorial': dados.get('setorial'),
        'ods': dados.get('ods'),
        'publicoAlvo': dados.get('publicoAlvo'),
        'estadosDisponiveis': dados.get('estadosDisponiveis'),
        'editalPorEstado': dados.get('editalPorEstado'),
        'objetivo': dados.get('objetivo'),
        'descricao': dados.get('descricao'),
        'beneficiosResultadosEsperados': dados.get('beneficiosResultadosEsperados'),
        'estruturaMateriais': dados.get('estruturaMateriais'),
        'responsabilidadeEmpresaDemandante': dados.get('responsabilidadeEmpresaDemandante'),
        'responsabilidadePrestadora': dados.get('responsabilidadePrestadora'),
        'perfilDesejadoPrestadora': dados.get('perfilDesejadoPrestadora'),
        'etapas': dados.get('etapas'),
        'perguntasDiagnostico': dados.get('perguntasDiagnostico'),
        'observacoesGerais': dados.get('observacoesGerais'),
        'observacoesEspecificas': dados.get('observacoesEspecificas'),
        'versaoAtual': dados.get('versaoAtual'),
        'historicoAlteracoes': dados.get('historicoAlteracoes'),
        'status': dados.get('status'),
        'criadoEm': dados.get('criadoEm'),
        'atualizadoEm': dados.get('atualizadoEm'),
        'criadoPor': dados.get('criadoPor'),
        'codigoCdt': dados.get('codigoCdt'),
        'unidade': dados.get('unidade'),
        'numeroOferta': dados.get('numeroOferta'),
    }
    
    return campos_ordenados

# Carregar todos os JSONs
json_files = sorted(glob.glob('saida/json/*.json'))
print(f"Processando {len(json_files)} arquivos JSON...\n")

solucoes = []
for i, json_file in enumerate(json_files, 1):
    with open(json_file, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Enriquecer com campos faltantes
    solucao_enriquecida = enriquecer_solucao(dados, i)
    solucoes.append(solucao_enriquecida)
    
    # Mostrar progresso sem caracteres especiais problemáticos
    if i % 50 == 0 or i <= 5:
        print(f"[{i}/{len(json_files)}] Processando...")




# Gerar TypeScript
typescript_code = 'import { Solution } from \'./types/solution\';\n\n'
typescript_code += '// Dados de soluções - Gerado automaticamente a partir dos JSONs convertidos\n'
typescript_code += f'// Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n'
typescript_code += f'// Total de soluções: {len(solucoes)}\n'
typescript_code += 'export const solutionsData: Solution[] = [\n'

for i, solucao in enumerate(solucoes):
    typescript_code += '  ' + json.dumps(solucao, ensure_ascii=False, indent=2).replace('\n', '\n  ')
    # Adicionar vírgula apenas se não for a última
    if i < len(solucoes) - 1:
        typescript_code += ',\n'
    else:
        typescript_code += '\n'

typescript_code += '];\n'

# Salvar arquivo com UTF-8 BOM para melhor compatibilidade no Windows
output_file = 'solutions-data-novo.ts'
with open(output_file, 'w', encoding='utf-8-sig') as f:
    f.write(typescript_code)

print("=" * 80)
print(f"✅ Arquivo gerado: {output_file}")
print(f"   Total de soluções: {len(solucoes)}")
print("\nⓘ  Campos com valores padrão (verifique e ajuste conforme necessário):")
print("   - valorTeto: 15000")
print("   - ods: [] (vazio)")
print("   - estadosDisponiveis: [] (vazio)")
print("   - editalPorEstado: {} (vazio)")
print("   - codigoCdt, unidade, numeroOferta: vazios")
print("   - status: 'ativa'")
print("   - criadoPor: 'Sistema'")
