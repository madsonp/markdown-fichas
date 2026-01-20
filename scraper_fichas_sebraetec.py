"""
Web Scraper para coletar PDFs das Fichas Técnicas Sebraetec
URL: https://datasebrae.com.br/fichas-tecnicas-sebraetec/
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re

class SebraetecScraper:
    def __init__(self, download_dir="entrada/pdfs"):
        self.base_url = "https://datasebrae.com.br/fichas-tecnicas-sebraetec/"
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def get_page_content(self, url):
        """Obtém o conteúdo HTML da página"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"❌ Erro ao acessar {url}: {e}")
            return None
    
    def extract_pdf_links(self, html_content):
        """Extrai todos os links de PDFs da página"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        pdf_links = []
        
        # Buscar todos os links que apontam para PDFs
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(self.base_url, href)
                pdf_links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True)
                })
        
        return pdf_links
    
    def download_pdf(self, pdf_url, filename=None):
        """Faz download de um PDF"""
        try:
            if not filename:
                # Extrair nome do arquivo da URL
                parsed = urlparse(pdf_url)
                filename = os.path.basename(parsed.path)
                
                # Limpar nome do arquivo
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            filepath = self.download_dir / filename
            
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
    
    def scrape_all_pdfs(self):
        """Extrai e baixa todos os PDFs da página"""
        print("="*60)
        print("🔍 SCRAPER DE FICHAS TÉCNICAS SEBRAETEC")
        print("="*60)
        print(f"📁 Diretório de download: {self.download_dir.absolute()}")
        print(f"🌐 URL: {self.base_url}")
        print()
        
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
            time.sleep(1)  # Pausa entre downloads
        
        print()
        print("="*60)
        print(f"✅ Download concluído: {len(downloaded)}/{len(pdf_links)} PDFs")
        print("="*60)
        
        return downloaded

def main():
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
