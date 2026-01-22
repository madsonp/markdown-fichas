"""
Web Scraper para coletar PDFs das Fichas Técnicas Sebraetec
URL: https://datasebrae.com.br/fichas-tecnicas-sebraetec/
"""

import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional

try:
    from config import SEBRAETEC_BASE_URL, SCRAPER_USER_AGENT, SCRAPER_TIMEOUT, SCRAPER_DELAY, SCRAPER_MAX_RETRIES, ENTRADA_PDFS_DIR
    from logger_config import setup_logger, LogContext, log_exception
    logger = setup_logger(__name__)
    USE_NEW_INFRA = True
except ImportError:
    SEBRAETEC_BASE_URL = "https://datasebrae.com.br/fichas-tecnicas-sebraetec/"
    SCRAPER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_TIMEOUT = 30
    SCRAPER_DELAY = 1.0
    SCRAPER_MAX_RETRIES = 3
    ENTRADA_PDFS_DIR = Path("entrada/pdfs")
    USE_NEW_INFRA = False


class SebraetecScraper:
    """Scraper para coletar PDFs das fichas técnicas do Sebraetec"""
    
    def __init__(self, download_dir: Optional[Path] = None):
        self.base_url = SEBRAETEC_BASE_URL
        self.download_dir = download_dir or ENTRADA_PDFS_DIR
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = SCRAPER_TIMEOUT
        self.delay = SCRAPER_DELAY
        self.max_retries = SCRAPER_MAX_RETRIES
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPER_USER_AGENT
        })
        
        if USE_NEW_INFRA:
            logger.info(f"Scraper inicializado - URL: {self.base_url}")
        
    def get_page_content(self, url: str, retries: int = 0) -> Optional[str]:
        """
        Obtém o conteúdo HTML da página com retry logic
        
        Args:
            url: URL para acessar
            retries: Número de tentativas já realizadas
            
        Returns:
            Conteúdo HTML ou None em caso de erro
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            if USE_NEW_INFRA:
                logger.info(f"Página carregada com sucesso: {url}")
            
            return response.text
            
        except requests.Timeout as e:
            if retries < self.max_retries:
                if USE_NEW_INFRA:
                    logger.warning(f"Timeout - Tentativa {retries + 1}/{self.max_retries}")
                time.sleep(self.delay * 2)
                return self.get_page_content(url, retries + 1)
            else:
                if USE_NEW_INFRA:
                    log_exception(logger, e, f"acessar {url} após {self.max_retries} tentativas")
                else:
                    print(f"❌ Timeout após {self.max_retries} tentativas: {url}")
                return None
                
        except requests.RequestException as e:
            if USE_NEW_INFRA:
                log_exception(logger, e, f"acessar {url}")
            else:
                print(f"❌ Erro ao acessar {url}: {e}")
            return None
    
    def extract_pdf_links(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extrai todos os links de PDFs da página
        
        Args:
            html_content: Conteúdo HTML da página
            
        Returns:
            Lista de dicionários com url e texto dos links
        """
        if not html_content:
            return []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            pdf_links = []
            
            # Buscar todos os links que apontam para PDFs
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().en: str, filename: Optional[str] = None) -> Optional[Path]:
        """
        Faz download de um PDF com retry logic
        
        Args:
            pdf_url: URL do PDF
            filename: Nome do arquivo (opcional, será extraído da URL)
            
        Returns:
            Path do arquivo baixado ou None em caso de erro
        """
        try:
            if not filename:
                # Extrair nome do arquivo da URL
                parsed = urlparse(pdf_url)
                filename = Path(parsed.path).name
                
                # Limpar nome do arquivo
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            filepath = self.download_dir / filename
            
            # Verificar se já existe
            if filepath.exists():
                if USE_NEW_INFRA:
                    logger.debug(f"Arquivo já existe: {filename}")
                else:
                    print(f"⏭️  Já existe: {filename}")
                return filepath
            
            if USE_NEW_INFRA:
                logger.info(f"Baixando: {filename}")
            else:
                print(f"⬇️  Baixando: {filename}")
            
            response = self.session.get(pdf_url, stream=True, timeout=self.timeout * 2)
            response.raise_for_status()
            
            # Salvar arquivo
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if USE_NEW_INFRA:
                logger.info(f"✅ Salvo: {filepath.name}")
            else:
                print(f"✅ Salvo: {filepath}")
            
            return filepath
            
        except requests.RequestException as e:
            if USE_NEW_INFRA:
                log_exception(logger, e, f"baixar {pdf_url}")
            else:
                print(f"❌ Erro ao baixar {pdf_url}: {e}")
            return None
        except IOError as e:
            if USE_NEW_INFRA:
                log_exception(logger, e, f"salvar arquivo {filename}")
            else:
                print(f"❌ Erro ao salvar {filename
            # Verificar se já existe
            if filepath.exists():
                print(f"⏭️  Já existe: {filename}")
                return filepath
            
            print(f"⬇️  Baixando: {filename}")
            response = self.session.get(pdf_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Salvar arquivo
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Salvo: {filepath}")
            return filepath
            
        except requests.RequestException as e:
            print(f"❌ Erro ao baixar {pdf_url}: {e}")
            return None
    
    def scrape_all_pdfs(self) -> List[Path]:
        """
        Extrai e baixa todos os PDFs da página
        
        Returns:
            Lista de Paths dos arquivos baixados
        """
        print("="*60)
        print("🔍 SCRAPER DE FICHAS TÉCNICAS SEBRAETEC")
        print("="*60)
        print(f"📁 Diretório de download: {self.download_dir.absolute()}")
        print(f"🌐 URL: {self.base_url}")
        print()
        
        if USE_NEW_INFRA:
            with LogContext(logger, "Scraping de PDFs"):
                return self._scrape_implementation()
        else:
            return self._scrape_implementation()
    
    def _scrape_implementation(self) -> List[Path]:
        """Implementação interna do scraping"""
        # Obter conteúdo da página
        print("📄 Carregando página principal...")
        html = self.get_page_content(self.base_url)
        
        if not html:
            print("❌ Não foi possível carregar a página")
            return []
        
        # Extrair links de PDFs
        print("🔎 Procurando PDFs na página...")
        pdf_links = self.extract_pdf_links(html)
        
        if not pdf_links:
            print("⚠️  Nenhum link de PDF encontrado diretamente na página")
            print("💡 A página pode usar JavaScript para carregar os PDFs")
            print("💡 Vou procurar por links em elementos específicos...")
            
            # Tentar abordagens alternativas
            soup = BeautifulSoup(html, 'html.parser')
            
            # Procurar por iframes, botões de download, etc
            print("\n🔍 Analisando estrutura da página...")
            print(f"   - Total de links encontrados: {len(soup.find_all('a'))}")
            print(f"   - Scripts JavaScript: {len(soup.find_all('script'))}")
            print(f"   - Iframes: {len(soup.find_all('iframe'))}")
            
            return []
        
        print(f"✨ Encontrados {len(pdf_links)} PDFs")
        print()
        
        # Baixar cada PDF
        downloaded = []
        for i, pdf_info in enumerate(pdf_links, 1):
            print(f"[{i}/{len(pdf_links)}] {pdf_info['text']}")
            filepath = self.download_pdf(pdf_info['url'])
            if filepath:
                downloaded.append(filepath)
            time.sleep(self.delay)  # Pausa entre downloads
        
        print()
        print("="*60)
        print(f"✅ Download concluído: {len(downloaded)}/{len(pdf_links)} PDFs")
        print("="*60)
        
        if USE_NEW_INFRA:
            logger.info(f"Scraping concluído: {len(downloaded)} PDFs baixados")
        
        return downloaded


def main():
    """Função principal do scraper"""
    scraper = SebraetecScraper()
    pdfs = scraper.scrape_all_pdfs()
    
    if pdfs:
        print("\n📋 PDFs baixados:")
        for pdf in pdfs:
            print(f"   - {pdf.name}")
    else:
        print("\n⚠️  Nenhum PDF foi baixado")
        print("\n💡 Sugestões:")
        print("   1. A página pode usar JavaScript dinâmico - considere usar Selenium")
        print("   2. Pode haver um seletor de estado/filtro que precisa ser acionado")
        print("   3. Verifique manualmente a página para identificar a estrutura")

if __name__ == "__main__":
    main()
