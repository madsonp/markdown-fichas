"""
Teste rápido do Markdown Formatter Agent
Demonstra o funcionamento com exemplos práticos
"""
from agents.markdown_formatter_agent import get_formatter_agent

def test_formatter():
    """Testa o formatter com exemplos práticos"""
    formatter = get_formatter_agent()
    formatter.reset_memory()
    
    print("\n" + "=" * 80)
    print("🧪 TESTE RÁPIDO - MARKDOWN FORMATTER AGENT")
    print("=" * 80 + "\n")
    
    # Exemplo 1: Bullets misturados
    print("TESTE 1: Bullets Misturados")
    print("-" * 80)
    
    texto1 = "Com base no diagnóstico realizado, deve-se orientar a empresa para implantação conforme recomendado • propor estratégias e indicadores • definir e organizar processos • criar procedimentos • capacitar empregados"
    
    print("ANTES:")
    print(f'"{texto1}"\n')
    
    formatado1 = formatter.format_markdown_text(texto1)
    
    print("DEPOIS:")
    print(f'"{formatado1}"\n')
    
    # Reset para próximo teste
    formatter.reset_memory()
    
    # Exemplo 2: Numeração misturada
    print("\nTESTE 2: Numeração Misturada")
    print("-" * 80)
    
    texto2 = "Orientar para o processo de implantação conforme recomendado 1. propor estratégias 2. definir processos 3. criar procedimentos 4. capacitar empregados 5. avaliar resultados"
    
    print("ANTES:")
    print(f'"{texto2}"\n')
    
    formatado2 = formatter.format_markdown_text(texto2)
    
    print("DEPOIS:")
    print(f'"{formatado2}"\n')
    
    # Reset para próximo teste
    formatter.reset_memory()
    
    # Exemplo 3: Processamento de dicionário
    print("\nTESTE 3: Processamento de Dicionário")
    print("-" * 80)
    
    dados = {
        "id": "13004-4",
        "nomeSolucao": "ADEQUAÇÃO À NORMA ABNT NBR ISO 9001:2015",
        "etapas": [
            {
                "id": "e2",
                "titulo": "DIAGNÓSTICO",
                "descricao": "Diagnóstico da empresa em relação aos seguintes itens, quando aplicáveis • processos de planejamento • processos de suporte • processos de operação"
            }
        ],
        "responsabilidades": "As responsabilidades incluem 1. Aprovação da proposta 2. Disponibilização de agenda 3. Fornecimento de informações 4. Acompanhamento da prestadora"
    }
    
    print("ANTES:")
    print(f"descricao: \"{dados['etapas'][0]['descricao'][:80]}...\"")
    print(f"responsabilidades: \"{dados['responsabilidades'][:80]}...\"")
    
    dados_formatados = formatter.process_solution_data(dados)
    
    print("\nDEPOIS:")
    print(f"descricao: \"{dados_formatados['etapas'][0]['descricao'][:80]}...\"")
    print(f"responsabilidades: \"{dados_formatados['responsabilidades'][:80]}...\"")
    
    # Exibir relatório
    print("\n" + "=" * 80)
    formatter.print_report()
    
    # Resumo final
    print("\n" + "=" * 80)
    print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_formatter()
