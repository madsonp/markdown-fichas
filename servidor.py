import os
import time
import json
from pathlib import Path
from markitdown import MarkItDown
from extrator_ficha import ExtractorFichaTecnica
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
PASTA_ENTRADA = Path("entrada")  # Pasta para colocar PDFs
PASTA_SAIDA = Path("saida")      # Pasta onde vão os Markdown
PASTA_JSON = Path("saida/json")  # Pasta onde vão os JSONs normalizados
EXTENSOES = [".pdf", ".docx", ".html", ".doc", ".xlsx", ".pptx", ".txt"]

# Criar pastas se não existirem
PASTA_ENTRADA.mkdir(exist_ok=True)
PASTA_SAIDA.mkdir(exist_ok=True)
PASTA_JSON.mkdir(exist_ok=True)

# Inicializar MarkItDown
md = MarkItDown()

# Template de normalização
TEMPLATE_FICHA = {
    "id": "",
    "nomeSolucao": "",
    "codigo": "",
    "valorTeto": 0,
    "dataAtualizacaoEscopo": "",
    "dataAtualizacaoValor": "",
    "tema": "",
    "subtema": "",
    "tipoServico": "",
    "modalidade": "",
    "setorial": [],
    "ods": [],
    "publicoAlvo": [],
    "estadosDisponiveis": [],
    "editalPorEstado": {},
    "objetivo": "",
    "descricao": "",
    "beneficiosResultadosEsperados": "",
    "estruturaMateriais": "",
    "responsabilidadeEmpresaDemandante": "",
    "responsabilidadePrestadora": "",
    "perfilDesejadoPrestadora": "",
    "etapas": [],
    "perguntasDiagnostico": [],
    "observacoesGerais": "",
    "observacoesEspecificas": "",
    "versaoAtual": 1,
    "historicoAlteracoes": []
}

def normalizar_ficha(dados_extraidos):
    """Normaliza dados extraídos conforme o template padrão"""
    ficha_normalizada = TEMPLATE_FICHA.copy()
    
    # Preencher com dados fornecidos
    for campo, valor in dados_extraidos.items():
        if campo in ficha_normalizada:
            ficha_normalizada[campo] = valor
    
    logger.info(f"✓ Ficha normalizada conforme template padrão")
    return ficha_normalizada

def converter_arquivo(caminho_arquivo):
    """Converte um arquivo para Markdown e normaliza os dados"""
    try:
        logger.info(f"Iniciando conversão de: {caminho_arquivo.name}")
        
        # Ler o arquivo
        with open(caminho_arquivo, "rb") as f:
            resultado = md.convert_stream(f, file_extension=caminho_arquivo.suffix)
        
        # Salvar como Markdown
        nome_saida = caminho_arquivo.stem + ".md"
        caminho_saida = PASTA_SAIDA / nome_saida
        
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(resultado.text_content)
        
        logger.info(f"✅ Convertido: {caminho_arquivo.name} → {nome_saida}")
        
        # Usar extrator_ficha para extrair dados inteligentemente
        logger.info(f"🔍 Extraindo dados com extrator_ficha...")
        extrator = ExtractorFichaTecnica(str(caminho_saida))
        dados_extraidos = extrator.extrair_todos_dados()
        
        logger.info(f"✅ Dados extraídos com sucesso")
        
        # Normalizar conforme template
        ficha_normalizada = normalizar_ficha(dados_extraidos)
        
        # Salvar como JSON
        nome_json = caminho_arquivo.stem + ".json"
        caminho_json = PASTA_JSON / nome_json
        
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(ficha_normalizada, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ JSON normalizado: {nome_json}")
        
        # Deletar arquivo de entrada após conversão bem-sucedida
        caminho_arquivo.unlink()
        logger.info(f"Arquivo original removido: {caminho_arquivo.name}\n")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao converter {caminho_arquivo.name}: {str(e)}")
        return False

def monitorar_pasta():
    """Monitora a pasta de entrada continuamente"""
    arquivos_processados = set()
    
    logger.info("🚀 Servidor iniciado!")
    logger.info(f"📁 Monitorando pasta: {PASTA_ENTRADA.absolute()}")
    logger.info(f"📤 Salvando em: {PASTA_SAIDA.absolute()}")
    logger.info(f"📄 Extensões suportadas: {', '.join(EXTENSOES)}")
    logger.info("Aguardando arquivos...\n")
    
    try:
        while True:
            # Listar arquivos na pasta de entrada
            if PASTA_ENTRADA.exists():
                arquivos = [f for f in PASTA_ENTRADA.iterdir() if f.is_file()]
                
                for arquivo in arquivos:
                    # Verificar se é uma extensão suportada
                    if arquivo.suffix.lower() in EXTENSOES:
                        # Evitar processar o mesmo arquivo múltiplas vezes
                        if arquivo.name not in arquivos_processados:
                            arquivos_processados.add(arquivo.name)
                            converter_arquivo(arquivo)
                            # Remover do conjunto após algum tempo
                            time.sleep(1)
            
            # Verificar a cada 2 segundos
            time.sleep(2)
    
    except KeyboardInterrupt:
        logger.info("\n\n⛔ Servidor parado pelo usuário")
        logger.info("Encerrando...")

if __name__ == "__main__":
    monitorar_pasta()
