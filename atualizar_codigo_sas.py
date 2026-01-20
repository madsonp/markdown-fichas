"""
Script para atualizar o campo 'codigo' nos JSONs com o Código SAS da tabela de preços.
"""
import json
import pdfplumber
from pathlib import Path
from datetime import datetime

def extrair_codigos_sas_pdf(caminho_pdf):
    """
    Extrai os códigos SAS da tabela de preços em PDF.
    
    Estrutura da tabela:
    - Coluna 0: TEMA
    - Coluna 1: SUBTEMA  
    - Coluna 2: NOME DA FICHA
    - Coluna 3: CÓDIGO (ex: 41002-3)
    - Coluna 4: VERSÃO
    - Coluna 5: CÓDIGO SAS (ex: 371440100441)
    - Coluna 6: DATA DE PUBLICAÇÃO
    - Coluna 7: PREÇO MÁXIMO
    
    Returns:
        dict: Mapeamento {codigo_ficha: codigo_sas}
    """
    print(f"📄 Extraindo Códigos SAS do PDF: {caminho_pdf}")
    
    codigos_sas = {}
    
    with pdfplumber.open(caminho_pdf) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            if not tables:
                continue
            
            for tabela in tables:
                # Verificar se tem cabeçalho na primeira página
                tem_cabecalho = (page_num == 1 and len(tabela) > 2 and 
                                tabela[1] and tabela[1][0] and 
                                'CÓDIGO' in str(tabela[1][0]).upper())
                
                # Linha inicial: 2 se tem cabeçalho, 0 caso contrário
                linha_inicial = 2 if tem_cabecalho else 0
                
                for linha in tabela[linha_inicial:]:
                    if len(linha) >= 6 and linha[3]:  # Tem código na coluna 3
                        codigo_ficha = str(linha[3]).strip()
                        codigo_sas = str(linha[5]).strip() if len(linha) > 5 and linha[5] else None
                        
                        if codigo_sas and codigo_sas != 'None':
                            codigos_sas[codigo_ficha] = codigo_sas
    
    print(f"✅ {len(codigos_sas)} Códigos SAS extraídos")
    return codigos_sas

def atualizar_codigo_nos_jsons(codigos_sas, pasta_json='saida/json'):
    """
    Atualiza o campo 'codigo' nos JSONs com os Códigos SAS.
    
    Args:
        codigos_sas: dict com mapeamento {codigo_ficha: codigo_sas}
        pasta_json: caminho da pasta com os JSONs
    """
    pasta = Path(pasta_json)
    arquivos_json = list(pasta.glob('*.json'))
    
    print(f"\n🔄 Atualizando {len(arquivos_json)} arquivos JSON...")
    
    atualizados = 0
    nao_encontrados = []
    erros = []
    
    for json_file in arquivos_json:
        try:
            # Ler JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            ficha_id = dados.get('id', '')
            if not ficha_id:
                continue
            
            # Buscar Código SAS na tabela
            if ficha_id in codigos_sas:
                codigo_sas = codigos_sas[ficha_id]
                
                # Atualizar campo codigo
                dados['codigo'] = codigo_sas
                
                # Salvar JSON atualizado
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, indent=2, ensure_ascii=False)
                
                atualizados += 1
                if atualizados <= 5:  # Mostrar primeiros 5
                    print(f"   ✓ {ficha_id} → Código SAS: {codigo_sas}")
            else:
                nao_encontrados.append(ficha_id)
                
        except Exception as e:
            erro = f"{json_file.name}: {str(e)}"
            erros.append(erro)
    
    # Relatório final
    print(f"\n{'='*80}")
    print(f"📊 RELATÓRIO DE ATUALIZAÇÃO")
    print(f"{'='*80}")
    print(f"✅ Arquivos atualizados: {atualizados}")
    print(f"⚠️  IDs sem Código SAS na tabela: {len(nao_encontrados)}")
    print(f"❌ Erros: {len(erros)}")
    
    if nao_encontrados and len(nao_encontrados) <= 20:
        print(f"\n⚠️  IDs sem Código SAS:")
        for ficha_id in sorted(nao_encontrados):
            print(f"   - {ficha_id}")
    elif nao_encontrados:
        print(f"\n⚠️  {len(nao_encontrados)} IDs sem Código SAS (lista muito grande)")
    
    if erros and len(erros) <= 10:
        print(f"\n❌ Erros encontrados:")
        for erro in erros:
            print(f"   - {erro}")
    
    print(f"\n{'='*80}")
    print(f"✅ Atualização concluída!")
    
    return {
        'atualizados': atualizados,
        'nao_encontrados': len(nao_encontrados),
        'erros': len(erros)
    }

if __name__ == "__main__":
    import sys
    
    print("="*80)
    print("🔧 ATUALIZADOR DE CÓDIGO SAS - Fichas Técnicas Sebraetec")
    print("="*80)
    
    # Caminho padrão da tabela de preços
    caminho_pdf = 'Tabela-de-Precos-Fichas-Tecnicas-Sebraetec-4.0-08-12-2025-1.pdf'
    
    # Permitir passar caminho customizado
    if len(sys.argv) > 1:
        caminho_pdf = sys.argv[1]
    
    if not Path(caminho_pdf).exists():
        print(f"\n❌ Erro: Arquivo não encontrado: {caminho_pdf}")
        print("\nUso: python atualizar_codigo_sas.py [caminho_tabela_precos.pdf]")
        sys.exit(1)
    
    print(f"\n📂 Tabela de preços: {caminho_pdf}")
    
    # Extrair Códigos SAS do PDF
    codigos_sas = extrair_codigos_sas_pdf(caminho_pdf)
    
    if not codigos_sas:
        print("\n❌ Nenhum Código SAS foi extraído do PDF")
        sys.exit(1)
    
    # Mostrar alguns exemplos
    print(f"\n📋 Exemplos de Códigos SAS extraídos:")
    for i, (codigo, sas) in enumerate(list(codigos_sas.items())[:5], 1):
        print(f"   {i}. {codigo} → {sas}")
    
    # Atualizar JSONs
    resultado = atualizar_codigo_nos_jsons(codigos_sas)
    
    print(f"\n✨ Data da atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
