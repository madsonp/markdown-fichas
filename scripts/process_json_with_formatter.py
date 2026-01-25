"""
Script para processar arquivos JSON existentes com o Markdown Formatter Agent
Útil para re-processar JSONs já convertidos
"""
import json
import glob
from pathlib import Path
from datetime import datetime
from agents.markdown_formatter_agent import get_formatter_agent

def process_json_files(directory: str = 'saida/json', output_suffix: str = '-formatted') -> None:
    """
    Processa todos os arquivos JSON em um diretório com o Formatter Agent
    
    Args:
        directory: Diretório contendo os arquivos JSON
        output_suffix: Sufixo para arquivos processados
    """
    formatter_agent = get_formatter_agent()
    
    # Encontrar todos os arquivos JSON
    json_files = sorted(glob.glob(f'{directory}/*.json'))
    
    if not json_files:
        print(f"❌ Nenhum arquivo JSON encontrado em '{directory}'")
        return
    
    print(f"📁 Processando {len(json_files)} arquivos JSON\n")
    print("=" * 80)
    
    total_adjustments = 0
    files_with_adjustments = 0
    
    for idx, json_file in enumerate(json_files, 1):
        try:
            # Reset memória para cada arquivo
            formatter_agent.reset_memory()
            
            # Ler arquivo
            with open(json_file, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Processar com agent
            dados_processados = formatter_agent.process_solution_data(dados)
            
            # Obter relatório
            report = formatter_agent.get_report()
            adjustments = report['totalAdjustmentsMade']
            
            # Salvar arquivo processado
            if adjustments > 0:
                output_file = json_file.replace('.json', f'{output_suffix}.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(dados_processados, f, indent=2, ensure_ascii=False)
                
                files_with_adjustments += 1
                total_adjustments += adjustments
                
                # Exibir resultado
                file_name = Path(json_file).name
                print(f"\n✅ [{idx}/{len(json_files)}] {file_name}")
                print(f"   Ajustes realizados: {adjustments}")
                print(f"   Salvo em: {Path(output_file).name}")
                
                # Exibir detalhes dos ajustes
                if report['adjustmentsHistory']:
                    for adj in report['adjustmentsHistory'][:3]:  # Primeiros 3
                        print(f"   • {adj['fieldName']}: {', '.join(adj['changesApplied'])}")
                    if len(report['adjustmentsHistory']) > 3:
                        print(f"   • ... e mais {len(report['adjustmentsHistory']) - 3} campos")
            else:
                print(f"\n⭕ [{idx}/{len(json_files)}] {Path(json_file).name}")
                print(f"   Nenhum ajuste necessário")
                
        except Exception as e:
            print(f"\n❌ [{idx}/{len(json_files)}] {Path(json_file).name}")
            print(f"   Erro: {str(e)[:100]}")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DO PROCESSAMENTO")
    print("=" * 80)
    print(f"✅ Total de arquivos: {len(json_files)}")
    print(f"📝 Arquivos com ajustes: {files_with_adjustments}")
    print(f"🔧 Total de ajustes realizados: {total_adjustments}")
    
    if files_with_adjustments > 0:
        print(f"\n💾 Arquivos processados salvos com sufixo '{output_suffix}'")
        print(f"   Exemplo: solucao{output_suffix}.json")
    else:
        print("\n✨ Todos os arquivos já estão corretamente formatados!")


def process_single_file(file_path: str, output_path: str = None) -> None:
    """
    Processa um único arquivo JSON
    
    Args:
        file_path: Caminho do arquivo JSON
        output_path: Caminho de saída (padrão: adiciona -formatted)
    """
    formatter_agent = get_formatter_agent()
    formatter_agent.reset_memory()
    
    try:
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Processar
        dados_processados = formatter_agent.process_solution_data(dados)
        
        # Definir caminho de saída
        if output_path is None:
            output_path = file_path.replace('.json', '-formatted.json')
        
        # Salvar
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dados_processados, f, indent=2, ensure_ascii=False)
        
        # Exibir relatório
        print(f"\n✅ Arquivo processado: {Path(file_path).name}")
        print(f"📁 Salvo em: {Path(output_path).name}")
        formatter_agent.print_report()
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 80)
    print("🔧 MARKDOWN FORMATTER AGENT - PROCESSADOR DE ARQUIVOS JSON")
    print("=" * 80 + "\n")
    
    # Se passado argumento, processar arquivo específico
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        process_single_file(file_path, output_path)
    else:
        # Processar diretório completo
        process_json_files()
