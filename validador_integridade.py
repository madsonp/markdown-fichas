"""
Validador de Integridade dos JSONs das Fichas Técnicas
Verifica se todos os campos obrigatórios foram extraídos corretamente
"""

import json
from pathlib import Path
from collections import defaultdict

class ValidadorFichasTecnicas:
    """Valida a integridade dos dados extraídos das fichas técnicas"""
    
    # Campos obrigatórios que devem estar presentes
    CAMPOS_OBRIGATORIOS = [
        'id',
        'nomeSolucao',
        'tema',
        'subtema',
        'tipoServico',
        'modalidade',
        'publicoAlvo'
    ]
    
    # Campos importantes que devem ter conteúdo
    CAMPOS_IMPORTANTES = [
        'beneficiosResultadosEsperados',
        'responsabilidadeEmpresaDemandante',
        'responsabilidadePrestadora',
        'perfilDesejadoPrestadora',
        'etapas'
    ]
    
    def __init__(self, dir_json="saida/json"):
        self.dir_json = Path(dir_json)
        self.resultados = {
            'total': 0,
            'validos': 0,
            'com_problemas': 0,
            'problemas': defaultdict(list)
        }
    
    def validar_arquivo(self, arquivo_json):
        """Valida um arquivo JSON individual"""
        problemas = []
        
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Verificar campos obrigatórios
            for campo in self.CAMPOS_OBRIGATORIOS:
                if campo not in dados:
                    problemas.append(f"❌ Campo obrigatório ausente: {campo}")
                elif not dados[campo]:
                    problemas.append(f"⚠️  Campo obrigatório vazio: {campo}")
            
            # Verificar campos importantes
            for campo in self.CAMPOS_IMPORTANTES:
                if campo not in dados:
                    problemas.append(f"⚠️  Campo importante ausente: {campo}")
                elif campo == 'etapas':
                    if not isinstance(dados[campo], list) or len(dados[campo]) == 0:
                        problemas.append(f"⚠️  Campo 'etapas' vazio ou inválido")
                elif not dados[campo] or dados[campo] == "":
                    problemas.append(f"⚠️  Campo importante vazio: {campo}")
            
            # Verificar se beneficiosResultadosEsperados está vazio mas deveria ter conteúdo
            if 'beneficiosResultadosEsperados' in dados:
                conteudo = dados['beneficiosResultadosEsperados']
                if not conteudo or len(conteudo.strip()) < 10:
                    problemas.append(f"⚠️  Campo 'beneficiosResultadosEsperados' muito curto ou vazio")
            
            return problemas
            
        except json.JSONDecodeError as e:
            return [f"❌ Erro ao ler JSON: {str(e)[:100]}"]
        except Exception as e:
            return [f"❌ Erro inesperado: {str(e)[:100]}"]
    
    def validar_todos(self, mostrar_detalhes=False):
        """Valida todos os arquivos JSON do diretório"""
        print("="*80)
        print("🔍 VALIDADOR DE INTEGRIDADE - FICHAS TÉCNICAS SEBRAETEC")
        print("="*80)
        print(f"📂 Diretório: {self.dir_json.absolute()}")
        print()
        
        # Listar todos os JSONs
        arquivos_json = sorted(list(self.dir_json.glob("*.json")))
        
        if not arquivos_json:
            print("❌ Nenhum arquivo JSON encontrado!")
            return
        
        print(f"📋 Total de arquivos JSON: {len(arquivos_json)}")
        print()
        
        # Validar cada arquivo
        arquivos_com_problemas = []
        
        for i, arquivo in enumerate(arquivos_json, 1):
            self.resultados['total'] += 1
            problemas = self.validar_arquivo(arquivo)
            
            if problemas:
                self.resultados['com_problemas'] += 1
                arquivos_com_problemas.append({
                    'arquivo': arquivo.name,
                    'problemas': problemas
                })
                
                # Categorizar problemas
                for problema in problemas:
                    if 'beneficiosResultadosEsperados' in problema:
                        self.resultados['problemas']['beneficios_vazio'].append(arquivo.name)
                    elif 'Campo obrigatório ausente' in problema:
                        self.resultados['problemas']['campo_obrigatorio_ausente'].append(arquivo.name)
                    elif 'Campo obrigatório vazio' in problema:
                        self.resultados['problemas']['campo_obrigatorio_vazio'].append(arquivo.name)
                    elif 'Campo importante' in problema:
                        self.resultados['problemas']['campo_importante_vazio'].append(arquivo.name)
                
                if mostrar_detalhes:
                    print(f"[{i}/{len(arquivos_json)}] ⚠️  {arquivo.name}")
                    for problema in problemas:
                        print(f"    {problema}")
                    print()
            else:
                self.resultados['validos'] += 1
                if mostrar_detalhes and i % 50 == 0:
                    print(f"[{i}/{len(arquivos_json)}] ✅ Validados até aqui...")
        
        # Relatório final
        print()
        print("="*80)
        print("📊 RELATÓRIO DE VALIDAÇÃO")
        print("="*80)
        print(f"Total de arquivos analisados: {self.resultados['total']}")
        print(f"✅ Arquivos válidos: {self.resultados['validos']}")
        print(f"⚠️  Arquivos com problemas: {self.resultados['com_problemas']}")
        print()
        
        if self.resultados['com_problemas'] > 0:
            taxa_sucesso = (self.resultados['validos'] / self.resultados['total']) * 100
            print(f"Taxa de sucesso: {taxa_sucesso:.1f}%")
            print()
            print("📋 RESUMO DOS PROBLEMAS:")
            print()
            
            if self.resultados['problemas']['beneficios_vazio']:
                print(f"⚠️  {len(self.resultados['problemas']['beneficios_vazio'])} arquivos com 'beneficiosResultadosEsperados' vazio")
            
            if self.resultados['problemas']['campo_obrigatorio_ausente']:
                print(f"❌ {len(self.resultados['problemas']['campo_obrigatorio_ausente'])} arquivos com campos obrigatórios ausentes")
            
            if self.resultados['problemas']['campo_obrigatorio_vazio']:
                print(f"⚠️  {len(self.resultados['problemas']['campo_obrigatorio_vazio'])} arquivos com campos obrigatórios vazios")
            
            if self.resultados['problemas']['campo_importante_vazio']:
                print(f"⚠️  {len(self.resultados['problemas']['campo_importante_vazio'])} arquivos com campos importantes vazios")
            
            print()
            print("📝 DETALHES DOS ARQUIVOS COM PROBLEMAS:")
            print()
            
            for item in arquivos_com_problemas[:20]:  # Mostrar apenas os 20 primeiros
                print(f"📄 {item['arquivo']}")
                for problema in item['problemas']:
                    print(f"   {problema}")
                print()
            
            if len(arquivos_com_problemas) > 20:
                print(f"... e mais {len(arquivos_com_problemas) - 20} arquivos com problemas")
        else:
            print("✅ Todos os arquivos estão válidos!")
        
        print("="*80)
        
        return arquivos_com_problemas
    
    def exportar_relatorio(self, arquivo_saida="relatorio_validacao.txt", arquivos_com_problemas=None):
        """Exporta relatório detalhado para arquivo"""
        if not arquivos_com_problemas:
            return
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE VALIDAÇÃO DE FICHAS TÉCNICAS SEBRAETEC\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total de arquivos: {self.resultados['total']}\n")
            f.write(f"Válidos: {self.resultados['validos']}\n")
            f.write(f"Com problemas: {self.resultados['com_problemas']}\n\n")
            
            f.write("ARQUIVOS COM PROBLEMAS:\n")
            f.write("-"*80 + "\n\n")
            
            for item in arquivos_com_problemas:
                f.write(f"{item['arquivo']}\n")
                for problema in item['problemas']:
                    f.write(f"  {problema}\n")
                f.write("\n")
        
        print(f"📝 Relatório detalhado salvo em: {arquivo_saida}")

def main():
    import sys
    
    # Opção para mostrar detalhes durante validação
    mostrar_detalhes = '--detalhes' in sys.argv or '-d' in sys.argv
    
    validador = ValidadorFichasTecnicas()
    arquivos_com_problemas = validador.validar_todos(mostrar_detalhes=mostrar_detalhes)
    
    # Exportar relatório se houver problemas
    if arquivos_com_problemas:
        validador.exportar_relatorio(arquivos_com_problemas=arquivos_com_problemas)

if __name__ == "__main__":
    main()
