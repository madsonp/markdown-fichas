"""
Analisador de Qualidade do Scrapping de Fichas Técnicas
Identifica e rankeia fichas com baixa qualidade de extração
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any, Optional

try:
    from config import SAIDA_JSON_DIR, PESOS_QUALIDADE, CAMPOS_OBRIGATORIOS, SCORE_MINIMO_QUALIDADE
    from logger_config import setup_logger, log_exception
    logger = setup_logger(__name__)
    USE_NEW_INFRA = True
except ImportError:
    # Fallback para compatibilidade
    SAIDA_JSON_DIR = Path("saida/json")
    PESOS_QUALIDADE = {
        'campo_obrigatorio_presente': 10,
        'campo_obrigatorio_preenchido': 5,
        'campo_importante_preenchido': 3,
        'beneficios_tamanho': 2,
        'etapas_quantidade': 2,
        'descricao_presente': 3,
        'responsabilidades_presentes': 2,
        'entregas_sem_duplicatas': 5  # Penalidade por entregas duplicadas
    }
    CAMPOS_OBRIGATORIOS = ['id', 'nomeSolucao', 'tema', 'subtema', 'tipoServico', 'modalidade', 'publicoAlvo']
    SCORE_MINIMO_QUALIDADE = 70
    USE_NEW_INFRA = False


class AnalisadorQualidade:
    """Analisa a qualidade da extração de dados das fichas técnicas"""
    
    # Pesos para cálculo de score de qualidade
    PESOS = PESOS_QUALIDADE
    
    def __init__(self, dir_json: Optional[str] = None):
        self.dir_json = Path(dir_json) if dir_json else SAIDA_JSON_DIR
        self.resultados: List[Dict[str, Any]] = []
        if USE_NEW_INFRA:
            logger.info(f"Analisador inicializado - Diretório: {self.dir_json}")
    
    def calcular_score_qualidade(self, dados: Dict[str, Any], nome_arquivo: str) -> Dict[str, Any]:
        """Calcula um score de qualidade (0-100) para um arquivo JSON"""
        score = 0
        max_score = 0
        problemas = []
        
        # Campos obrigatórios
        for campo in CAMPOS_OBRIGATORIOS:
            max_score += self.PESOS['campo_obrigatorio_presente']
            if campo in dados:
                score += self.PESOS['campo_obrigatorio_presente']
                if dados[campo] and str(dados[campo]).strip():
                    score += self.PESOS['campo_obrigatorio_preenchido']
                    max_score += self.PESOS['campo_obrigatorio_preenchido']
                else:
                    problemas.append(f"Campo obrigatório vazio: {campo}")
                    max_score += self.PESOS['campo_obrigatorio_preenchido']
            else:
                problemas.append(f"Campo obrigatório ausente: {campo}")
                max_score += self.PESOS['campo_obrigatorio_preenchido']
        
        # beneficiosResultadosEsperados
        max_score += self.PESOS['campo_importante_preenchido']
        beneficios = dados.get('beneficiosResultadosEsperados', '')
        if beneficios and len(beneficios.strip()) > 50:
            score += self.PESOS['campo_importante_preenchido']
            # Bonus por tamanho adequado
            if len(beneficios) > 200:
                score += self.PESOS['beneficios_tamanho']
                max_score += self.PESOS['beneficios_tamanho']
            else:
                max_score += self.PESOS['beneficios_tamanho']
        else:
            problemas.append("beneficiosResultadosEsperados ausente ou muito curto")
            max_score += self.PESOS['beneficios_tamanho']
        
        # Etapas
        max_score += self.PESOS['etapas_quantidade']
        etapas = dados.get('etapas', [])
        if isinstance(etapas, list) and len(etapas) >= 2:
            score += self.PESOS['etapas_quantidade']
        else:
            problemas.append(f"Poucas etapas: {len(etapas) if isinstance(etapas, list) else 0}")
        
        # Descrição
        max_score += self.PESOS['descricao_presente']
        descricao = dados.get('descricao', '')
        if descricao and len(descricao.strip()) > 50:
            score += self.PESOS['descricao_presente']
        else:
            problemas.append("Descrição ausente ou muito curta")
        
        # Responsabilidades
        max_score += self.PESOS['responsabilidades_presentes'] * 2
        resp_empresa = dados.get('responsabilidadeEmpresaDemandante', '')
        resp_prestadora = dados.get('responsabilidadePrestadora', '')
        
        if resp_empresa and len(resp_empresa.strip()) > 50:
            score += self.PESOS['responsabilidades_presentes']
        else:
            problemas.append("responsabilidadeEmpresaDemandante ausente ou muito curta")
        
        if resp_prestadora and len(resp_prestadora.strip()) > 50:
            score += self.PESOS['responsabilidades_presentes']
        else:
            problemas.append("responsabilidadePrestadora ausente ou muito curta")
        
        # Verificar entregas duplicadas nas etapas
        max_score += self.PESOS.get('entregas_sem_duplicatas', 5)
        if isinstance(etapas, list) and len(etapas) > 0:
            from collections import Counter
            entregas = [etapa.get('entrega', '').strip() for etapa in etapas if etapa.get('entrega', '').strip()]
            
            if len(entregas) > 0:
                contador = Counter(entregas)
                duplicadas = {entrega: count for entrega, count in contador.items() if count > 1}
                
                if not duplicadas:
                    # Sem duplicatas = pontuação completa
                    score += self.PESOS.get('entregas_sem_duplicatas', 5)
                else:
                    # Com duplicatas = penalização
                    num_duplicatas = sum(count - 1 for count in duplicadas.values())
                    problemas.append(f"Entregas duplicadas: {num_duplicatas} repetição(ões) em {len(duplicadas)} entrega(s)")
                    
                    # Reduzir pontuação proporcionalmente ao número de duplicatas
                    penalidade = min(num_duplicatas / len(entregas), 1.0)  # 0 a 1
                    score += self.PESOS.get('entregas_sem_duplicatas', 5) * (1 - penalidade)
        
        # Calcular percentual
        score_percentual = (score / max_score * 100) if max_score > 0 else 0
        
        return {
            'arquivo': nome_arquivo,
            'score': round(score_percentual, 1),
            'problemas': problemas,
            'detalhes': {
                'id': dados.get('id', ''),
                'nomeSolucao': dados.get('nomeSolucao', ''),
                'tema': dados.get('tema', ''),
                'tamanho_beneficios': len(beneficios),
                'num_etapas': len(etapas) if isinstance(etapas, list) else 0,
                'tem_descricao': bool(descricao and len(descricao.strip()) > 50)
            }
        }
    
    def analisar_todos(self, limite_baixa_qualidade: Optional[float] = None) -> List[Dict[str, Any]]:
        """Analisa todos os arquivos JSON e identifica os de baixa qualidade"""
        limite = limite_baixa_qualidade or SCORE_MINIMO_QUALIDADE
        
        print("="*80)
        print("🔍 ANALISADOR DE QUALIDADE DO SCRAPPING")
        print("="*80)
        print(f"📂 Diretório: {self.dir_json.absolute()}")
        print(f"⚠️  Considerando baixa qualidade: score < {limite}%")
        print()
        
        # Listar todos os JSONs
        try:
            arquivos_json = sorted(list(self.dir_json.glob("*.json")))
        except Exception as e:
            if USE_NEW_INFRA:
                log_exception(logger, e, "listar arquivos JSON")
            print(f"❌ Erro ao listar arquivos: {e}")
            return []
        
        if not arquivos_json:
            print("❌ Nenhum arquivo JSON encontrado!")
            return []
        
        print(f"📋 Analisando {len(arquivos_json)} arquivos...")
        print()
        
        # Analisar cada arquivo
        for arquivo in arquivos_json:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                resultado = self.calcular_score_qualidade(dados, arquivo.name)
                self.resultados.append(resultado)
                
            except json.JSONDecodeError as e:
                if USE_NEW_INFRA:
                    log_exception(logger, e, f"decodificar JSON {arquivo.name}")
                self.resultados.append({
                    'arquivo': arquivo.name,
                    'score': 0,
                    'problemas': [f"Erro JSON: {str(e)[:100]}"],
                    'detalhes': {}
                })
            except Exception as e:
                if USE_NEW_INFRA:
                    log_exception(logger, e, f"processar {arquivo.name}")
                self.resultados.append({
                    'arquivo': arquivo.name,
                    'score': 0,
                    'problemas': [f"Erro ao processar: {str(e)[:100]}"],
                    'detalhes': {}
                })
        
        # Ordenar por score (pior primeiro)
        self.resultados.sort(key=lambda x: x['score'])
        
        # Filtrar baixa qualidade
        baixa_qualidade = [r for r in self.resultados if r['score'] < limite]
        
        # Estatísticas
        print("="*80)
        print("📊 ESTATÍSTICAS GERAIS")
        print("="*80)
        print(f"Total de arquivos: {len(self.resultados)}")
        print(f"Arquivos com baixa qualidade (< {limite}%): {len(baixa_qualidade)}")
        
        if self.resultados:
            scores = [r['score'] for r in self.resultados]
            print(f"Score médio: {sum(scores)/len(scores):.1f}%")
            print(f"Score mínimo: {min(scores):.1f}%")
            print(f"Score máximo: {max(scores):.1f}%")
        
        print()
        print("="*80)
        print(f"🚨 TOP {min(20, len(baixa_qualidade))} FICHAS COM PIOR QUALIDADE")
        print("="*80)
        print()
        
        for i, resultado in enumerate(baixa_qualidade[:20], 1):
            score_icon = "🔴" if resultado['score'] < 30 else "🟡" if resultado['score'] < 50 else "🟠"
            print(f"{i}. {score_icon} Score: {resultado['score']}% - {resultado['arquivo']}")
            
            # Mostrar detalhes
            detalhes = resultado['detalhes']
            if detalhes.get('id'):
                print(f"   ID: {detalhes['id']}")
            if detalhes.get('nomeSolucao'):
                print(f"   Nome: {detalhes['nomeSolucao'][:70]}...")
            if detalhes.get('tema'):
                print(f"   Tema: {detalhes['tema']}")
            
            print(f"   Problemas ({len(resultado['problemas'])}):")
            for problema in resultado['problemas'][:5]:
                print(f"      • {problema}")
            if len(resultado['problemas']) > 5:
                print(f"      ... e mais {len(resultado['problemas']) - 5} problemas")
            print()
        
        if len(baixa_qualidade) > 20:
            print(f"... e mais {len(baixa_qualidade) - 20} arquivos com baixa qualidade")
        
        print("="*80)
        
        return baixa_qualidade
    
    def exportar_relatorio_detalhado(self, arquivo_saida="relatorio_qualidade.json"):
        """Exporta relatório completo em JSON"""
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump({
                'total_arquivos': len(self.resultados),
                'estatisticas': {
                    'score_medio': sum(r['score'] for r in self.resultados) / len(self.resultados) if self.resultados else 0,
                    'score_minimo': min(r['score'] for r in self.resultados) if self.resultados else 0,
                    'score_maximo': max(r['score'] for r in self.resultados) if self.resultados else 0
                },
                'arquivos': self.resultados
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Relatório detalhado exportado: {arquivo_saida}")
    
    def exportar_lista_baixa_qualidade(self, limite=70, arquivo_saida="fichas_baixa_qualidade.txt"):
        """Exporta lista simples de arquivos com baixa qualidade"""
        baixa_qualidade = [r for r in self.resultados if r['score'] < limite]
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(f"FICHAS COM BAIXA QUALIDADE (Score < {limite}%)\n")
            f.write("="*80 + "\n\n")
            
            for i, resultado in enumerate(baixa_qualidade, 1):
                f.write(f"{i}. Score: {resultado['score']}% - {resultado['arquivo']}\n")
                f.write(f"   Problemas:\n")
                for problema in resultado['problemas']:
                    f.write(f"      • {problema}\n")
                f.write("\n")
        
        print(f"📝 Lista de baixa qualidade exportada: {arquivo_saida}")
        print(f"   Total: {len(baixa_qualidade)} arquivos")

def main():
    import sys
    
    # Definir limite de qualidade (padrão: 70%)
    limite = 70
    if len(sys.argv) > 1:
        try:
            limite = int(sys.argv[1])
        except:
            print(f"⚠️  Limite inválido, usando padrão: {limite}%")
    
    analisador = AnalisadorQualidade()
    baixa_qualidade = analisador.analisar_todos(limite_baixa_qualidade=limite)
    
    # Perguntar se quer exportar relatórios
    print()
    print("💾 Exportar relatórios?")
    print("   1 - Relatório JSON completo")
    print("   2 - Lista simples TXT")
    print("   3 - Ambos")
    print("   0 - Não exportar")
    
    try:
        opcao = input("\nEscolha (0-3): ").strip()
        
        if opcao == "1" or opcao == "3":
            analisador.exportar_relatorio_detalhado()
        
        if opcao == "2" or opcao == "3":
            analisador.exportar_lista_baixa_qualidade(limite=limite)
    except:
        print("\n⏭️  Pulando exportação")

if __name__ == "__main__":
    main()
