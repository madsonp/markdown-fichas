import json
import pandas as pd
from pathlib import Path

def extrair_tabela_pdf(caminho_pdf):
    """
    Extrai tabela de um PDF usando diferentes métodos.
    Tenta primeiro com tabula-py, depois com pdfplumber, e por último com camelot.
    """
    print(f"📄 Tentando extrair tabela do PDF...")
    
    # Método 1: Tentar com tabula-py
    try:
        import tabula
        print("   Método 1: Usando tabula-py...")
        dfs = tabula.read_pdf(caminho_pdf, pages='all', multiple_tables=False)
        if dfs and len(dfs) > 0:
            df = dfs[0] if isinstance(dfs, list) else dfs
            print(f"   ✅ Tabela extraída com tabula-py: {len(df)} linhas")
            return df
    except ImportError:
        print("   ⚠️  tabula-py não instalado")
    except Exception as e:
        print(f"   ⚠️  Erro com tabula-py: {str(e)[:100]}")
    
    # Método 2: Tentar com pdfplumber
    try:
        import pdfplumber
        print("   Método 2: Usando pdfplumber...")
        with pdfplumber.open(caminho_pdf) as pdf:
            todos_dados = []
            
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if not tables:
                    continue
                
                for tabela in tables:
                    # Verificar se primeira página tem cabeçalhos (linha 1 com "CÓDIGO")
                    tem_cabecalho = (page_num == 1 and len(tabela) > 2 and 
                                    tabela[1][0] and 'CÓDIGO' in str(tabela[1][0]).upper())
                    
                    # Linha inicial: 2 se tem cabeçalho (pula título e cabeçalhos), 0 caso contrário
                    linha_inicial = 2 if tem_cabecalho else 0
                    
                    for linha in tabela[linha_inicial:]:
                        if len(linha) >= 8 and linha[3]:  # Código está na coluna 3
                            codigo = linha[3]
                            preco_str = linha[7] if len(linha) > 7 else None
                            # Limpar preço: remover "R$", pontos e vírgulas
                            if preco_str and 'R$' in str(preco_str):
                                preco_str = preco_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
                                try:
                                    preco = float(preco_str)
                                    todos_dados.append({'id': codigo, 'valorTeto': preco})
                                except:
                                    pass
            
            if todos_dados:
                df = pd.DataFrame(todos_dados)
                print(f"   ✅ Tabela Sebraetec extraída com pdfplumber: {len(df)} linhas com preço de {len(pdf.pages)} páginas")
                return df
            
            # Se não encontrou dados no formato Sebraetec, tentar formato padrão
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)
            
            if all_tables:
                # Formato padrão
                tabela = all_tables[0]
                df = pd.DataFrame(tabela[1:], columns=tabela[0])
                print(f"   ✅ Tabela extraída com pdfplumber: {len(df)} linhas")
                return df
                
    except ImportError:
        print("   ⚠️  pdfplumber não instalado")
    except Exception as e:
        print(f"   ⚠️  Erro com pdfplumber: {str(e)[:100]}")
    
    # Método 3: Tentar com camelot
    try:
        import camelot
        print("   Método 3: Usando camelot...")
        tables = camelot.read_pdf(caminho_pdf, pages='all', flavor='lattice')
        if len(tables) > 0:
            df = tables[0].df
            print(f"   ✅ Tabela extraída com camelot: {len(df)} linhas")
            return df
    except ImportError:
        print("   ⚠️  camelot não instalado")
    except Exception as e:
        print(f"   ⚠️  Erro com camelot: {str(e)[:100]}")
    
    print("\n❌ Não foi possível extrair a tabela do PDF automaticamente.")
    print("\n💡 Soluções:")
    print("   1. Instale uma biblioteca de extração:")
    print("      pip install tabula-py")
    print("      pip install pdfplumber")
    print("   2. Ou converta o PDF para CSV/Excel manualmente")
    return None

def atualizar_precos_jsons(caminho_tabela_precos: str, formato='csv'):
    """
    Atualiza os valores de valorTeto nos JSONs com base em uma tabela de preços.
    
    Formato esperado da tabela:
    - Coluna 'id' ou 'codigo': código da ficha técnica (ex: 13008-4)
    - Coluna 'valorTeto' ou 'preco' ou 'valor': valor teto em reais
    
    Args:
        caminho_tabela_precos: Caminho para arquivo CSV, Excel, JSON ou PDF com preços
        formato: 'csv', 'excel', 'json' ou 'pdf'
    """
    
    # Ler tabela de preços
    print(f"📊 Lendo tabela de preços: {caminho_tabela_precos}")
    
    if formato == 'csv':
        df = pd.read_csv(caminho_tabela_precos)
    elif formato == 'excel':
        df = pd.read_excel(caminho_tabela_precos)
    elif formato == 'json':
        df = pd.read_json(caminho_tabela_precos)
    elif formato == 'pdf':
        df = extrair_tabela_pdf(caminho_tabela_precos)
        if df is None:
            return
    else:
        raise ValueError(f"Formato não suportado: {formato}")
    
    print(f"   Total de registros na tabela: {len(df)}")
    print(f"   Colunas: {list(df.columns)}")
    
    # Identificar colunas relevantes
    col_id = None
    col_valor = None
    
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ['id', 'codigo', 'código', 'ficha']:
            col_id = col
        if col_lower in ['valorteto', 'valor_teto', 'preco', 'preço', 'valor']:
            col_valor = col
    
    if not col_id or not col_valor:
        print(f"❌ Erro: Não foi possível identificar colunas de ID e Valor")
        print(f"   Colunas encontradas: {list(df.columns)}")
        print(f"   Esperado: coluna com 'id'/'codigo' e coluna com 'valorTeto'/'preco'")
        return
    
    print(f"✅ Colunas identificadas: ID='{col_id}', Valor='{col_valor}'")
    
    # Criar dicionário de preços
    precos = {}
    for _, row in df.iterrows():
        ficha_id = str(row[col_id]).strip()
        valor = float(row[col_valor]) if pd.notna(row[col_valor]) else 0
        precos[ficha_id] = valor
    
    print(f"   Dicionário de preços criado: {len(precos)} entradas")
    
    # Atualizar JSONs
    pasta_json = Path('saida/json')
    arquivos_json = list(pasta_json.glob('*.json'))
    
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
            
            # Buscar preço na tabela
            if ficha_id in precos:
                dados['valorTeto'] = precos[ficha_id]
                
                # Salvar JSON atualizado
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, indent=2, ensure_ascii=False)
                
                atualizados += 1
                if atualizados <= 5:  # Mostrar primeiros 5
                    print(f"   ✅ {json_file.name[:50]:50} | ID: {ficha_id:10} | Valor: R$ {precos[ficha_id]:,.2f}")
            else:
                nao_encontrados.append(ficha_id)
        
        except Exception as e:
            erros.append(f"{json_file.name}: {str(e)}")
    
    # Relatório final
    print(f"\n{'='*80}")
    print(f"📊 RELATÓRIO DE ATUALIZAÇÃO DE PREÇOS")
    print(f"{'='*80}")
    print(f"✅ Arquivos atualizados: {atualizados}")
    print(f"⚠️  IDs não encontrados na tabela: {len(nao_encontrados)}")
    print(f"❌ Erros: {len(erros)}")
    
    if nao_encontrados and len(nao_encontrados) <= 20:
        print(f"\n⚠️  IDs sem preço na tabela:")
        for ficha_id in sorted(nao_encontrados):
            print(f"   - {ficha_id}")
    
    if erros and len(erros) <= 10:
        print(f"\n❌ Erros encontrados:")
        for erro in erros:
            print(f"   - {erro}")
    
    print(f"\n{'='*80}")
    print(f"✅ Atualização concluída!")

if __name__ == "__main__":
    import sys
    
    print("="*80)
    print("💰 ATUALIZADOR DE PREÇOS - Fichas Técnicas Sebraetec")
    print("="*80)
    print("\nFormatos suportados:")
    print("  - CSV: python atualizar_precos.py precos.csv csv")
    print("  - Excel: python atualizar_precos.py precos.xlsx excel")
    print("  - JSON: python atualizar_precos.py precos.json json")
    print("  - PDF: python atualizar_precos.py precos.pdf pdf")
    print("\nA tabela deve conter:")
    print("  - Coluna 'id' ou 'codigo': código da ficha (ex: 13008-4)")
    print("  - Coluna 'valorTeto' ou 'preco': valor em reais")
    print("="*80)
    
    if len(sys.argv) < 2:
        print("\n❌ Erro: Informe o caminho da tabela de preços")
        print("\nUso: python atualizar_precos.py <arquivo> [formato]")
        print("Exemplo: python atualizar_precos.py tabela_precos.csv csv")
        sys.exit(1)
    
    caminho = sys.argv[1]
    formato = sys.argv[2] if len(sys.argv) > 2 else 'csv'
    
    if not Path(caminho).exists():
        print(f"\n❌ Erro: Arquivo não encontrado: {caminho}")
        sys.exit(1)
    
    print(f"\n📂 Arquivo: {caminho}")
    print(f"📋 Formato: {formato}\n")
    
    atualizar_precos_jsons(caminho, formato)
