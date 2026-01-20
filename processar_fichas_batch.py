"""
Pipeline completo: PDF → Markdown → JSON
Processa todas as fichas técnicas baixadas
"""

import os
import json
from pathlib import Path
from extrator_ficha import ExtractorFichaTecnica

# Importar markitdown
try:
    from markitdown import MarkItDown
    md_converter = MarkItDown()
except ImportError:
    print("❌ markitdown não está instalado. Instale com: pip install markitdown")
    md_converter = None

class ProcessadorFichasTecnicas:
    def __init__(self, dir_pdfs="entrada/pdfs", dir_markdown="saida", dir_json="saida/json"):
        self.dir_pdfs = Path(dir_pdfs)
        self.dir_markdown = Path(dir_markdown)
        self.dir_json = Path(dir_json)
        
        # Criar diretórios se não existem
        self.dir_json.mkdir(parents=True, exist_ok=True)
    
    def pdf_para_markdown(self, arquivo_pdf):
        """Converte PDF para Markdown usando markitdown"""
        try:
            if md_converter is None:
                print(f"   ❌ markitdown não disponível")
                return None
            
            nome_sem_ext = arquivo_pdf.stem
            arquivo_md = self.dir_markdown / f"{nome_sem_ext}.md"
            
            # Se já existe, pular
            if arquivo_md.exists():
                print(f"   ⏭️  MD já existe: {arquivo_md.name}")
                return arquivo_md
            
            print(f"   📄 Convertendo para MD...")
            
            # Converter usando markitdown
            result = md_converter.convert(str(arquivo_pdf))
            
            if result and result.text_content:
                # Salvar conteúdo
                with open(arquivo_md, 'w', encoding='utf-8') as f:
                    f.write(result.text_content)
                print(f"   ✅ MD criado: {arquivo_md.name}")
                return arquivo_md
            else:
                print(f"   ❌ Conversão retornou vazio")
                return None
                
        except Exception as e:
            print(f"   ❌ Exceção: {str(e)[:100]}")
            return None
    
    def markdown_para_json(self, arquivo_md):
        """Converte Markdown para JSON usando o extrator"""
        try:
            nome_sem_ext = arquivo_md.stem
            arquivo_json = self.dir_json / f"{nome_sem_ext}.json"
            
            # Se já existe, pular
            if arquivo_json.exists():
                print(f"   ⏭️  JSON já existe: {arquivo_json.name}")
                return arquivo_json
            
            print(f"   🔄 Extraindo dados para JSON...")
            
            # Extrair dados
            extrator = ExtractorFichaTecnica(str(arquivo_md))
            dados = extrator.extrair_todos_dados()
            dados_normalizados = extrator._normalizar_dados(dados)
            
            # Salvar JSON
            with open(arquivo_json, 'w', encoding='utf-8') as f:
                json.dump(dados_normalizados, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ JSON criado: {arquivo_json.name}")
            return arquivo_json
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair: {str(e)[:100]}")
            return None
    
    def processar_todos(self, limite=None):
        """Processa todos os PDFs do diretório"""
        print("="*70)
        print("🚀 PIPELINE DE PROCESSAMENTO DE FICHAS TÉCNICAS SEBRAETEC")
        print("="*70)
        print(f"📂 PDFs: {self.dir_pdfs}")
        print(f"📂 Markdown: {self.dir_markdown}")
        print(f"📂 JSON: {self.dir_json}")
        print()
        
        # Listar PDFs
        pdfs = sorted(list(self.dir_pdfs.glob("*.pdf")))
        
        if not pdfs:
            print("❌ Nenhum PDF encontrado!")
            return
        
        if limite:
            pdfs = pdfs[:limite]
            print(f"⚠️  Processando apenas {limite} primeiros arquivos")
        
        print(f"📋 Total de PDFs encontrados: {len(pdfs)}")
        print()
        
        # Estatísticas
        stats = {
            'total': len(pdfs),
            'md_sucesso': 0,
            'md_erro': 0,
            'json_sucesso': 0,
            'json_erro': 0
        }
        
        # Processar cada PDF
        for i, pdf in enumerate(pdfs, 1):
            print(f"[{i}/{len(pdfs)}] {pdf.name}")
            
            # PDF → MD
            arquivo_md = self.pdf_para_markdown(pdf)
            if arquivo_md:
                stats['md_sucesso'] += 1
                
                # MD → JSON
                arquivo_json = self.markdown_para_json(arquivo_md)
                if arquivo_json:
                    stats['json_sucesso'] += 1
                else:
                    stats['json_erro'] += 1
            else:
                stats['md_erro'] += 1
                stats['json_erro'] += 1
            
            print()
        
        # Relatório final
        print("="*70)
        print("📊 RELATÓRIO FINAL")
        print("="*70)
        print(f"Total de PDFs: {stats['total']}")
        print(f"MD criados:    {stats['md_sucesso']} ✅ / {stats['md_erro']} ❌")
        print(f"JSON criados:  {stats['json_sucesso']} ✅ / {stats['json_erro']} ❌")
        print(f"Taxa de sucesso: {stats['json_sucesso']/stats['total']*100:.1f}%")
        print("="*70)

def main():
    import sys
    
    # Verificar se deve processar apenas alguns arquivos (para teste)
    limite = None
    if len(sys.argv) > 1:
        try:
            limite = int(sys.argv[1])
            print(f"⚠️  Modo teste: processando apenas {limite} arquivos\n")
        except:
            pass
    
    processador = ProcessadorFichasTecnicas()
    processador.processar_todos(limite=limite)

if __name__ == "__main__":
    main()
