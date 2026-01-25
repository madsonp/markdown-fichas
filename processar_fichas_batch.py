"""
Pipeline completo: PDF → Markdown → JSON
Processa todas as fichas técnicas baixadas
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, List
from extrator_ficha import ExtractorFichaTecnica

# Adicionar diretório pai ao path para importar agents
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import ENTRADA_PDFS_DIR, SAIDA_DIR, SAIDA_JSON_DIR
    from logger_config import setup_logger, LogContext, log_exception, log_progress
    logger = setup_logger(__name__)
    USE_NEW_INFRA = True
except ImportError:
    ENTRADA_PDFS_DIR = Path("entrada/pdfs")
    SAIDA_DIR = Path("saida")
    SAIDA_JSON_DIR = Path("saida/json")
    USE_NEW_INFRA = False

# Importar markitdown
try:
    from markitdown import MarkItDown
    md_converter = MarkItDown()
except ImportError:
    print("❌ markitdown não está instalado. Instale com: pip install markitdown")
    md_converter = None

# Importar Markdown Formatter Agent
try:
    from agents.markdown_formatter_agent import get_formatter_agent
    FORMATTER_AGENT = get_formatter_agent()
    USE_FORMATTER = True
except ImportError:
    FORMATTER_AGENT = None
    USE_FORMATTER = False


class ProcessadorFichasTecnicas:
    """Processador de fichas técnicas: PDF → MD → JSON"""
    
    def __init__(
        self, 
        dir_pdfs: Optional[Path] = None,
        dir_markdown: Optional[Path] = None,
        dir_json: Optional[Path] = None
    ):
        self.dir_pdfs = dir_pdfs or ENTRADA_PDFS_DIR
        self.dir_markdown = dir_markdown or SAIDA_DIR
        self.dir_json = dir_json or SAIDA_JSON_DIR
        
        # Criar diretórios se não existem
        self.dir_json.mkdir(parents=True, exist_ok=True)
        
        if USE_NEW_INFRA:
            logger.info(f"Processador inicializado")
            logger.info(f"  PDFs: {self.dir_pdfs}")
            logger.info(f"  Markdown: {self.dir_markdown}")
            logger.info(f"  JSON: {self.dir_json}")
    
    def pdf_para_markdown(self, arquivo_pdf: Path) -> Optional[Path]:
        """
        Converte PDF para Markdown usando markitdown
        
        Args:
            arquivo_pdf: Path do arquivo PDF
            
        Returns:
            Path do arquivo Markdown criado ou None em caso de erro
        """
        try:
            if md_converter is None:
                if USE_NEW_INFRA:
                    logger.error("markitdown não disponível")
                else:
                    print(f"   ❌ markitdown não disponível")
                return None
            
            nome_sem_ext = arquivo_pdf.stem
            arquivo_md = self.dir_markdown / f"{nome_sem_ext}.md"
            
            # Se já existe, pular
            if arquivo_md.exists():
                if USE_NEW_INFRA:
                    logger.debug(f"MD já existe: {arquivo_md.name}")
                else:
                    print(f"   ⏭️  MD já existe: {arquivo_md.name}")
                return arquivo_md
            
            if USE_NEW_INFRA:
                logger.info(f"Convertendo para MD: {arquivo_pdf.name}")
            else:
                print(f"   📄 Convertendo para MD...")
            
            # Converter usando markitdown
            result = md_converter.convert(str(arquivo_pdf))
            
            if result and result.text_content:
                # Salvar conteúdo
                with open(arquivo_md, 'w', encoding='utf-8') as f:
                    f.write(result.text_content)
                
                if USE_NEW_INFRA:
                    logger.info(f"✅ MD criado: {arquivo_md.name}")
                else:
                    print(f"   ✅ MD criado: {arquivo_md.name}")
                return arquivo_md
            else:
                if USE_NEW_INFRA:
                    logger.warning("Conversão retornou vazio")
                else:
                    print(f"   ❌ Conversão retornou vazio")
                return None
                
        except Exception as e:
            if USE_NEW_INFRA:
                log_exception(logger, e, f"converter {arquivo_pdf.name}")
            else:
                print(f"   ❌ Exceção: {str(e)[:100]}")
            return None
    
    def markdown_para_json(self, arquivo_md: Path) -> Optional[Path]:
        """
        Converte Markdown para JSON usando o extrator
        Aplica Markdown Formatter Agent para normalizar formatação
        
        Args:
            arquivo_md: Path do arquivo Markdown
            
        Returns:
            Path do arquivo JSON criado ou None em caso de erro
        """
        try:
            nome_sem_ext = arquivo_md.stem
            arquivo_json = self.dir_json / f"{nome_sem_ext}.json"
            
            # Se já existe, pular
            if arquivo_json.exists():
                if USE_NEW_INFRA:
                    logger.debug(f"JSON já existe: {arquivo_json.name}")
                else:
                    print(f"   ⏭️  JSON já existe: {arquivo_json.name}")
                return arquivo_json
            
            if USE_NEW_INFRA:
                logger.info(f"Extraindo dados: {arquivo_md.name}")
            else:
                print(f"   🔄 Extraindo dados para JSON...")
            
            # Extrair dados
            extrator = ExtractorFichaTecnica(str(arquivo_md))
            dados = extrator.extrair_todos_dados()
            dados_normalizados = extrator._normalizar_dados(dados)
            
            # Aplicar Markdown Formatter Agent se disponível
            if USE_FORMATTER and FORMATTER_AGENT:
                try:
                    FORMATTER_AGENT.reset_memory()
                    dados_normalizados = FORMATTER_AGENT.process_solution_data(dados_normalizados)
                    if USE_NEW_INFRA:
                        logger.debug(f"Formatter Agent aplicado: {arquivo_md.name}")
                except Exception as e:
                    if USE_NEW_INFRA:
                        logger.warning(f"Erro ao aplicar Formatter Agent: {str(e)[:100]}")
            
            # Salvar JSON
            with open(arquivo_json, 'w', encoding='utf-8') as f:
                json.dump(dados_normalizados, f, ensure_ascii=False, indent=2)
            
            if USE_NEW_INFRA:
                logger.info(f"✅ JSON criado: {arquivo_json.name}")
            else:
                print(f"   ✅ JSON criado: {arquivo_json.name}")
            
            return arquivo_json
            
        except Exception as e:
            if USE_NEW_INFRA:
                log_exception(logger, e, f"extrair dados de {arquivo_md.name}")
            else:
                print(f"   ❌ Erro ao extrair: {str(e)[:100]}")
            return None
    
    def processar_todos(self, limite: Optional[int] = None) -> Dict[str, int]:
        """
        Processa todos os PDFs do diretório
        
        Args:
            limite: Número máximo de arquivos a processar (None = todos)
            
        Returns:
            Dicionário com estatísticas de processamento
        """
        print("="*70)
        print("🚀 PIPELINE DE PROCESSAMENTO DE FICHAS TÉCNICAS SEBRAETEC")
        print("="*70)
        print(f"📂 PDFs: {self.dir_pdfs}")
        print(f"📂 Markdown: {self.dir_markdown}")
        print(f"📂 JSON: {self.dir_json}")
        print()
        
        # Listar PDFs
        try:
            pdfs = sorted(list(self.dir_pdfs.glob("*.pdf")))
        except Exception as e:
            if USE_NEW_INFRA:
                log_exception(logger, e, "listar PDFs")
            print(f"❌ Erro ao listar PDFs: {e}")
            return {'total': 0, 'md_sucesso': 0, 'md_erro': 0, 'json_sucesso': 0, 'json_erro': 0}
        
        if not pdfs:
            print("❌ Nenhum PDF encontrado!")
            return {'total': 0, 'md_sucesso': 0, 'md_erro': 0, 'json_sucesso': 0, 'json_erro': 0}
        
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
        if USE_NEW_INFRA:
            with LogContext(logger, f"Processamento de {len(pdfs)} PDFs"):
                self._processar_lote(pdfs, stats)
        else:
            self._processar_lote(pdfs, stats)
        
        # Relatório final
        self._imprimir_relatorio(stats)
        
        return stats
    
    def _processar_lote(self, pdfs: List[Path], stats: Dict[str, int]):
        """Processa um lote de PDFs"""
        for i, pdf in enumerate(pdfs, 1):
            print(f"[{i}/{len(pdfs)}] {pdf.name}")
            
            if USE_NEW_INFRA:
                log_progress(logger, i, len(pdfs), pdf.name)
            
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
    
    def _imprimir_relatorio(self, stats: Dict[str, int]):
        """Imprime relatório final de processamento"""
        print("="*70)
        print("📊 RELATÓRIO FINAL")
        print("="*70)
        print(f"Total de PDFs: {stats['total']}")
        print(f"MD criados:    {stats['md_sucesso']} ✅ / {stats['md_erro']} ❌")
        print(f"JSON criados:  {stats['json_sucesso']} ✅ / {stats['json_erro']} ❌")
        
        if stats['total'] > 0:
            taxa = stats['json_sucesso'] / stats['total'] * 100
            print(f"Taxa de sucesso: {taxa:.1f}%")
        
        print("="*70)
        
        if USE_NEW_INFRA:
            logger.info(f"Processamento concluído: {stats['json_sucesso']}/{stats['total']} fichas")

def main():
    """Função principal"""
    import sys
    
    # Verificar se deve usar processamento paralelo
    try:
        from config import PROCESSAMENTO_PARALELO
        if PROCESSAMENTO_PARALELO:
            print("🚀 Usando processamento PARALELO")
            print("   Para forçar sequencial, use: processar_fichas_batch.py")
            print()
            from processar_fichas_paralelo import ProcessadorParalelo
            
            limite = None
            if len(sys.argv) > 1:
                try:
                    limite = int(sys.argv[1])
                except ValueError:
                    pass
            
            processador = ProcessadorParalelo()
            processador.processar_todos_paralelo(limite=limite)
            return
    except ImportError:
        pass
    
    # Processamento sequencial (padrão)
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
