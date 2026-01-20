import re
import json
from pathlib import Path
from typing import Dict, Any, List

class ExtractorFichaTecnica:
    """Extrator inteligente de dados do MD da ficha técnica - Robusto para diferentes formatos"""
    
    SUJEIRAS = [
        r'^Uso Interno$',
        r'^Código da ficha técnica:',
        r'^HISTÓRICO DE ALTERAÇÕES',
        r'^Link$',
        r'^Responsável$',
        r'^Coordenação',
        r'^Sebraetec$',
        r'\d+\s+Ficha Técnica.*Sebraetec.*Código da ficha técnica:',  # Rodapé com número (1 Ficha Técnica..., 2 Ficha Técnica...)
        r'^Ficha Técnica\s*[\–\-]\s*Sebraetec',  # Rodapé sem número inicial
        r'^\d+\s*$',  # Número isolado (ex: "3" sozinho na linha)
        r'^Confidencial\s*$'  # Palavra "Confidencial" sozinha
    ]
    
    def __init__(self, caminho_md: str):
        self.caminho_md = Path(caminho_md)
        self.linhas = self._ler_arquivo()
        
    def _ler_arquivo(self) -> list:
        """Lê o arquivo MD e retorna lista de linhas"""
        with open(self.caminho_md, 'r', encoding='utf-8') as f:
            return f.readlines()
    
    def _eh_sujeira(self, linha: str) -> bool:
        """Verifica se uma linha é sujeira para ser ignorada"""
        linha_limpa = linha.strip()
        for padrao_sujeira in self.SUJEIRAS:
            if re.match(padrao_sujeira, linha_limpa):
                return True
        return False
    
    def _eh_inicio_secao(self, linha: str, numero_esperado: int = None) -> bool:
        """Detecta se é o início de uma seção numerada"""
        match = re.match(r'^(\d+)\.\s+', linha.strip())
        if match:
            numero = int(match.group(1))
            if numero_esperado is None or numero == numero_esperado:
                return True
        return False
    
    def _eh_lista_item(self, linha: str) -> bool:
        """Detecta se é um item de lista (bullet, número, letra)"""
        linha_limpa = linha.strip()
        # Deteta: ●, ○, •, números, letras maiúsculas
        return bool(re.match(r'^[●○•\d+\-A-Z]\.|^[●○•]\s+', linha_limpa))
    
    def _normalizar_modalidade(self, texto: str) -> str:
        """Normaliza modalidades para categorias padrão"""
        texto_lower = texto.lower()
        
        if "presencial" in texto_lower and ("distância" in texto_lower or "online" in texto_lower or "a distância" in texto_lower):
            return "Híbrido"
        elif "presencial" in texto_lower:
            return "Presencial"
        elif "distância" in texto_lower or "online" in texto_lower or "a distância" in texto_lower:
            return "Online"
        
        return texto
    
    def _normalizar_publico_alvo(self, texto: str) -> List[str]:
        """Normaliza público alvo para categorias padrão"""
        publico = []
        
        # Detectar empresa
        if any(termo in texto.upper() for termo in ["MEI", "ME", "EPP", "EMPRESA"]):
            publico.append("Empresa")
        
        # Detectar produtor rural
        if "produtor rural" in texto.lower():
            publico.append("Produtor Rural")
        
        # Detectar artesão
        if "artesão" in texto.lower():
            publico.append("Artesão")
        
        # Se não encontrou categorias, retorna o texto original
        if not publico:
            publico.append(texto)
        
        return publico
    
    def _limpar_quebras_em_frases(self, texto: str) -> str:
        """
        Remove quebras de linha (\n) que estão no meio de frases
        Mantém quebras após pontuação (. ! ? ; :)
        """
        if not texto:
            return texto
        
        # Substituir quebras que NÃO estão após pontuação
        # Primeiro, proteger quebras após pontuação
        texto = re.sub(r'([.!?;:])\n', '\x00QUEBRA_PROTEGIDA\x00', texto)
        
        # Remover todas as outras quebras (substituindo por espaço)
        texto = texto.replace('\n', ' ')
        
        # Restaurar quebras protegidas
        texto = texto.replace('\x00QUEBRA_PROTEGIDA\x00', '\n')
        
        # Limpar múltiplos espaços
        texto = re.sub(r' +', ' ', texto)
        
        # Limpar múltiplos \n
        texto = re.sub(r'\n+', '\n', texto)
        
        return texto.strip()
    
    def _normalizar_dados(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza todos os campos de string removendo quebras em frases e sujeira inline"""
        dados_normalizados = {}
        
        for chave, valor in dados.items():
            if isinstance(valor, str):
                # Limpar quebras em frases
                texto = self._limpar_quebras_em_frases(valor)
                # Remover sujeira inline (rodapé de página tipo "1 Ficha Técnica – Sebraetec 4.0 Código da ficha técnica: XXXXX")
                # Também remove versão reduzida como "3 Ficha Técnica – Sebraetec 4.0"
                texto = re.sub(r'\d+\s+Ficha Técnica\s*[\–\-]\s*Sebraetec\s+\d+\.\d+(\s+Código da ficha técnica:\s+\d+-\d+)?', '', texto)
                # Remover espaços duplos resultantes da remoção de sujeira
                texto = re.sub(r'  +', ' ', texto)
                # Remover bullets duplicados (• • → •, • • • → •, etc)
                texto = re.sub(r'•(\s*•)+', '•', texto)
                dados_normalizados[chave] = texto
            elif isinstance(valor, list):
                # Se é lista, normalizar cada item se for string
                dados_normalizados[chave] = [
                    self._normalizar_string_sujeira(item) if isinstance(item, str) else 
                    (self._normalizar_dados(item) if isinstance(item, dict) else item)
                    for item in valor
                ]
            elif isinstance(valor, dict):
                # Se é dict, normalizar recursivamente
                dados_normalizados[chave] = self._normalizar_dados(valor)
            else:
                dados_normalizados[chave] = valor
        
        return dados_normalizados
    
    def _normalizar_string_sujeira(self, texto: str) -> str:
        """Remove sujeira inline de um texto"""
        if not isinstance(texto, str):
            return texto
        texto = self._limpar_quebras_em_frases(texto)
        # Remover sujeira inline: "1 Ficha Técnica – Sebraetec 4.0 Código da ficha técnica: XXXXX" ou "3 Ficha Técnica – Sebraetec 4.0"
        # Usa [\s\–\-] para aceitar espaços, endash (–) ou hífen (-)
        # O "Código da ficha técnica: XXXXX" é opcional (\s+Código...)?
        texto = re.sub(r'\d+\s+Ficha Técnica\s*[\–\-]\s*Sebraetec\s+\d+\.\d+(\s+Código da ficha técnica:\s+\d+-\d+)?', '', texto)
        # Remover espaços duplos resultantes da remoção de sujeira
        texto = re.sub(r'  +', ' ', texto)
        # Remover bullets duplicados (• • → •, • • • → •, etc)
        # Padrão: bullet seguido por espaços/bullets repetidos
        texto = re.sub(r'•(\s*•)+', '•', texto)
        return texto
    
    def _formatar_descricao_estruturada(self, texto: str) -> str:
        """
        Formata descrições estruturadas em seções temáticas com bullets
        Detecta padrões como "Implementar... Alguns indicadores..." e reorganiza
        """
        if not isinstance(texto, str) or not texto:
            return texto
        
        # Padrão: títulos de seção que terminam em : ou são precedidos de bullets
        # Ex: "Implementar ou aprimorar os processos de compras e recebimento:"
        # Seguido por bullets
        
        # Dividir por títulos de seção (palavras chaves que iniciam seções)
        secao_keys = ['Implementar', 'Aprimorar', 'Alguns indicadores', 'Realização das']
        
        # Encontrar onde começam as seções
        secoes = []
        pos_atual = 0
        
        for key in secao_keys:
            matches = [(m.start(), m.end(), key) for m in re.finditer(rf'\b{re.escape(key)}\b', texto, re.IGNORECASE)]
            for inicio, fim, matched_key in matches:
                if inicio >= pos_atual:
                    secoes.append((inicio, fim, matched_key))
        
        # Ordenar por posição
        secoes.sort(key=lambda x: x[0])
        
        if not secoes:
            # Sem seções identificadas, apenas retornar com bullets organizados
            return self._organizar_bullets_estruturado(texto)
        
        # Reconstruir o texto com quebras duplas entre seções
        resultado = []
        ultimo_fim = 0
        
        for idx, (inicio, fim, key) in enumerate(secoes):
            # Se não é a primeira seção, adicionar quebra dupla
            if idx > 0 and resultado:
                resultado.append('\n')
            
            # Adicionar texto da seção até o próximo título ou fim
            if idx < len(secoes) - 1:
                proximo_inicio = secoes[idx + 1][0]
                texto_secao = texto[ultimo_fim:proximo_inicio].strip()
            else:
                texto_secao = texto[ultimo_fim:].strip()
            
            if texto_secao:
                # Organizar bullets dentro dessa seção
                texto_secao = self._organizar_bullets_estruturado(texto_secao)
                resultado.append(texto_secao)
            
            ultimo_fim = proximo_inicio if idx < len(secoes) - 1 else len(texto)
        
        return '\n'.join(resultado)
    
    def _organizar_bullets_estruturado(self, texto: str) -> str:
        """
        Organiza bullets em um texto para que cada um fique em sua própria linha
        Também preserva títulos de seções (linhas sem bullets)
        """
        if not texto or '•' not in texto:
            return texto.strip()
        
        linhas = texto.split('\n')
        resultado = []
        
        for linha in linhas:
            linha_limpa = linha.strip()
            
            if not linha_limpa:
                continue
            
            # Se tem bullet, precisa separar todos os bullets para linhas diferentes
            if '•' in linha_limpa:
                # Dividir por bullets e reconstruir
                partes = linha_limpa.split('•')
                
                # Primeira parte (antes do primeiro bullet) - pode ser título
                if partes[0].strip():
                    primeiro = partes[0].strip()
                    # Se parece ser um título (sem pontuação de fim de sentence), adicionar
                    if not primeiro.endswith('.') and not primeiro.endswith(';'):
                        resultado.append(primeiro)
                    else:
                        resultado.append(primeiro)
                
                # Cada parte após o bullet se torna um item
                for i, parte in enumerate(partes[1:]):
                    parte_limpa = parte.strip()
                    if parte_limpa:
                        # Limpar pontuação de fim que pode estar em bullet anterior
                        parte_limpa = re.sub(r'^[;:]\s*', '', parte_limpa)
                        # Remover ponto e vírgula do final se for último caractere
                        parte_limpa = re.sub(r';\s*$', '', parte_limpa)
                        resultado.append('• ' + parte_limpa)
            else:
                # Linha sem bullets - é um título ou descrição
                resultado.append(linha_limpa)
        
        return '\n'.join(resultado)
    
    def extrair_nome_solucao(self) -> str:
        """
        Extrai o nome da solução (título da ficha após o código)
        Coleta TODAS as linhas maiúsculas consecutivas que formam o título
        Exemplo: ADEQUAÇÃO / EXPORTAÇÃO / DE / PROCESSOS / LOGÍSTICOS / PARA
        """
        for i, linha in enumerate(self.linhas):
            # Procurar pela linha do código
            if re.match(r'^Código da ficha técnica:', linha.strip()):
                # Após o código, coletar todas as palavras maiúsculas consecutivas
                palavras_titulo = []
                j = i + 1
                
                while j < len(self.linhas):
                    linha_candidata = self.linhas[j].strip()
                    
                    # Pular linhas vazias
                    if not linha_candidata:
                        j += 1
                        continue
                    
                    # Pular linha de tipo de serviço (como "Consultoria tecnológica")
                    if linha_candidata in ["Consultoria tecnológica", "Consultoria", "Assessoria"]:
                        j += 1
                        continue
                    
                    # Se encontrou um número (tipo "1.  Tema"), parar
                    if re.match(r'^\d+\.|^-$', linha_candidata):
                        break
                    
                    # Pular palavras especiais que não fazem parte do título
                    if linha_candidata in ["ÍNDICE", "INDEX", "SUMÁRIO"]:
                        j += 1
                        continue
                    
                    # Se é uma palavra maiúscula, adicionar ao título
                    if linha_candidata.isupper() and len(linha_candidata) > 0:
                        palavras_titulo.append(linha_candidata)
                        j += 1
                    else:
                        # Se encontrou algo que não é maiúsculo/vazio/número, parar
                        break
                
                # Juntar todas as palavras com espaço
                if palavras_titulo:
                    return " ".join(palavras_titulo)
        
        return ""
    
    def extrair_codigo_ficha(self) -> str:
        """
        Extrai o código da ficha técnica (ID)
        Procura por "Código da ficha técnica: XXXXX"
        """
        for linha in self.linhas[:5]:
            match = re.search(r'Código da ficha técnica:\s*([\d\w-]+)', linha)
            if match:
                return match.group(1)
        return ""
    
    def _extrair_valor_bullet(self, campo: str) -> str:
        """
        Extrai valor de formato bullet: • Campo: Valor
        Exemplo: • Tema: Produção e qualidade
        """
        for linha in self.linhas:
            linha_limpa = linha.strip()
            # Procurar padrão: • Campo: Valor
            match = re.search(rf'•\s*{re.escape(campo)}\s*:\s*(.+)', linha_limpa, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
    
    def extrair_tema(self) -> str:
        """
        Extrai o tema - texto após "1. Tema" ou • Tema: xxx
        Procura pela linha com número e pega a próxima linha não vazia
        """
        # Tentar formato padrão primeiro
        for i, linha in enumerate(self.linhas):
            if re.search(r'^1\.\s+Tema', linha.strip()):
                # Procura a próxima linha que não seja vazia
                for j in range(i + 1, len(self.linhas)):
                    tema = self.linhas[j].strip()
                    if tema and not re.match(r'^\d+\.', tema):  # Se não é outra seção
                        return tema
        
        # Se não encontrou, tentar formato bullet
        return self._extrair_valor_bullet("Tema")
    
    def extrair_subtema(self) -> str:
        """
        Extrai o subtema - texto após "2. Subtema" ou • Subtema: xxx
        Procura pela linha com número e pega a próxima linha não vazia
        """
        # Tentar formato padrão primeiro
        for i, linha in enumerate(self.linhas):
            if re.search(r'^2\.\s+Subtema', linha.strip()):
                # Procura a próxima linha que não seja vazia
                for j in range(i + 1, len(self.linhas)):
                    subtema = self.linhas[j].strip()
                    if subtema and not re.match(r'^\d+\.', subtema):
                        return subtema
        
        # Se não encontrou, tentar formato bullet
        return self._extrair_valor_bullet("Subtema")
    
    def extrair_tipo_servico(self) -> str:
        """
        Extrai o tipo de serviço - texto após "4. Tipo de serviço" ou linha do código
        """
        # Tentar formato padrão primeiro
        for i, linha in enumerate(self.linhas):
            if re.search(r'^4\.\s+Tipo de serviço', linha.strip()):
                # Procura a próxima linha que não seja vazia
                for j in range(i + 1, len(self.linhas)):
                    tipo = self.linhas[j].strip()
                    if tipo and not re.match(r'^\d+\.', tipo):
                        # Pega apenas a primeira parte antes de "/"
                        tipo = tipo.split("/")[0].strip()
                        return tipo
        
        # Tentar na linha após o código (alguns arquivos têm "Consultoria tecnológica" ali)
        for i, linha in enumerate(self.linhas[:10]):
            if re.match(r'^Código da ficha técnica:', linha.strip()):
                # Verificar linha seguinte
                if i + 1 < len(self.linhas):
                    proxima = self.linhas[i + 1].strip()
                    # Se não está vazia e não é maiúscula (título), pode ser tipo de serviço
                    if proxima and not proxima.isupper() and not re.match(r'^\d+\.', proxima):
                        return proxima.split("/")[0].strip()
        
        return ""
    
    def extrair_modalidade(self) -> str:
        """Extrai e normaliza modalidade"""
        # Tentar formato padrão primeiro
        for i, linha in enumerate(self.linhas):
            if re.search(r'^5\.\s+Modalidade', linha.strip()):
                for j in range(i + 1, len(self.linhas)):
                    modalidade = self.linhas[j].strip()
                    if modalidade and not self._eh_inicio_secao(modalidade):
                        return self._normalizar_modalidade(modalidade)
        
        # Se não encontrou, tentar formato bullet
        valor = self._extrair_valor_bullet("Modalidade")
        if valor:
            return self._normalizar_modalidade(valor)
        return ""
    
    def extrair_publico_alvo(self) -> List[str]:
        """Extrai e normaliza público alvo"""
        # Tentar formato padrão primeiro
        for i, linha in enumerate(self.linhas):
            if re.search(r'^6\.\s+Público alvo', linha.strip()):
                for j in range(i + 1, len(self.linhas)):
                    texto = self.linhas[j].strip()
                    if texto and not self._eh_inicio_secao(texto):
                        return self._normalizar_publico_alvo(texto)
        
        # Se não encontrou, tentar formato bullet
        valor = self._extrair_valor_bullet("Público-alvo")
        if not valor:
            valor = self._extrair_valor_bullet("Público alvo")
        if valor:
            return self._normalizar_publico_alvo(valor)
        return []
    
    def extrair_setor(self) -> str:
        """Extrai o setor indicado (seção 7) ou • Setor indicado: xxx"""
        # Tentar formato padrão primeiro
        for i, linha in enumerate(self.linhas):
            if re.search(r'^7\.\s+Setor indicado', linha.strip()):
                # Procura a próxima linha que não seja vazia
                for j in range(i + 1, len(self.linhas)):
                    setor = self.linhas[j].strip()
                    if setor and not re.match(r'^\d+\.', setor):
                        return setor
        
        # Se não encontrou, tentar formato bullet
        return self._extrair_valor_bullet("Setor indicado")
        return ""
    
    def extrair_secao(self, titulo_secao: str, numero_secao: int) -> str:
        """
        Método robusto para extrair seção
        - Preserva estrutura (bullets, números, letras)
        - Remove sujeiras
        - Para na próxima seção numerada
        - Ignora variações de formatação
        """
        secao_completa = []
        coletando = False
        
        for i, linha in enumerate(self.linhas):
            linha_limpa = linha.strip()
            
            # Começar a coletar na seção desejada
            if self._eh_inicio_secao(linha_limpa, numero_secao):
                coletando = True
                continue
            
            if coletando:
                # Parar em próxima seção numerada (número diferente)
                if re.match(r'^\d+\.', linha_limpa):
                    match = re.match(r'^(\d+)\.', linha_limpa)
                    if match and int(match.group(1)) != numero_secao:
                        break
                
                # Parar em marcadores específicos
                if re.match(r'^ETAPA|^HISTÓRICO', linha_limpa):
                    break
                
                # Ignorar sujeiras
                if linha_limpa and not self._eh_sujeira(linha_limpa):
                    secao_completa.append(linha_limpa)
        
        # Juntar preservando estrutura
        if secao_completa:
            texto = "\n".join(secao_completa)
            # Limpar múltiplos espaços mas preservar quebras
            texto = re.sub(r'[ \t]+', ' ', texto)
            return texto.strip()
        
        return ""
    
    def extrair_beneficios_resultados(self) -> str:
        """
        Extrai Benefícios e resultados esperados
        Busca pelo título em todo o documento (não depende de numeração)
        """
        secao_completa = []
        coletando = False
        
        for i, linha in enumerate(self.linhas):
            linha_limpa = linha.strip()
            
            # Buscar pelo título (flexível com regex)
            if re.search(r'Benefícios\s+e\s+resultados\s+esperados', linha_limpa, re.IGNORECASE):
                coletando = True
                continue
            
            if coletando:
                # Parar ao encontrar próxima seção numerada (10., 11., etc.) seguida de título em maiúscula
                # Mas não parar em listas numeradas (1., 2., 3.) nem em "10. Item da lista"
                if re.match(r'^(\d{1,2})\.\s+([A-Z][a-záàâãéèêíïóôõöúçñ]+)', linha_limpa):
                    # Verificar se é uma nova seção ou apenas um item de lista
                    match = re.match(r'^(\d{1,2})\.\s+([A-Z][a-záàâãéèêíïóôõöúçñ]+)', linha_limpa)
                    numero = int(match.group(1))
                    primeira_palavra = match.group(2)
                    
                    # Se o número é >= 11 E a primeira palavra é um título de seção (não item de lista)
                    # Títulos de seção comuns: "Estrutura", "Responsabilidade", "Perfil", "Observações"
                    titulos_secao = ['Estrutura', 'Responsabilidade', 'Perfil', 'Observações', 'Histórico']
                    if numero >= 11 and any(primeira_palavra.startswith(t) for t in titulos_secao):
                        break
                
                # Parar em marcadores específicos de nova seção
                if re.match(r'^(ETAPA|HISTÓRICO|Pré-diagnóstico|Estrutura\s+e\s+materiais)', linha_limpa, re.IGNORECASE):
                    break
                
                # Ignorar sujeiras mas continuar coletando
                if linha_limpa and not self._eh_sujeira(linha_limpa):
                    secao_completa.append(linha_limpa)
        
        if secao_completa:
            texto = "\n".join(secao_completa)
            # Para este campo específico, remover TODAS as quebras de linha
            texto = texto.replace('\n', ' ')
            texto = re.sub(r'[ \t]+', ' ', texto)
            # Remover rodapés e palavras soltas como "Confidencial"
            texto = re.sub(r'\s*\d+\s*Ficha Técnica.*$', '', texto, flags=re.IGNORECASE)
            texto = re.sub(r'\s*Confidencial\s*$', '', texto, flags=re.IGNORECASE)
            return texto.strip()
        return ""
    
    def extrair_estrutura_materiais(self) -> str:
        """
        Extrai Estrutura e materiais necessários
        Busca pelo título em todo o documento
        """
        secao_completa = []
        coletando = False
        
        for i, linha in enumerate(self.linhas):
            linha_limpa = linha.strip()
            
            # Buscar pelo título
            if re.search(r'Estrutura\s+e\s+materiais\s+necessários', linha_limpa, re.IGNORECASE):
                coletando = True
                continue
            
            if coletando:
                # Parar ao encontrar próxima seção numerada
                if re.match(r'^\d{1,2}\.', linha_limpa):
                    break
                
                # Parar em marcadores específicos
                if re.match(r'^Responsabilidade|^ETAPA|^HISTÓRICO', linha_limpa, re.IGNORECASE):
                    break
                
                # Ignorar sujeiras
                if linha_limpa and not self._eh_sujeira(linha_limpa):
                    secao_completa.append(linha_limpa)
        
        if secao_completa:
            texto = "\n".join(secao_completa)
            texto = re.sub(r'[ \t]+', ' ', texto)
            return texto.strip()
        return ""
    
    def extrair_responsabilidade_empresa_demandante(self) -> str:
        """
        Extrai responsabilidade da empresa demandante
        Robusto para diferentes formatos (bullets, números, letras)
        """
        secao_completa = []
        coletando = False
        
        for i, linha in enumerate(self.linhas):
            if re.search(r'^12\.\s+Responsabilidade da empresa demandante', linha.strip()):
                coletando = True
                continue
            
            if coletando:
                linha_limpa = linha.strip()
                
                # Parar em próxima seção numerada
                if re.match(r'^13\.', linha_limpa):
                    break
                
                # Ignorar sujeiras
                if linha_limpa and not self._eh_sujeira(linha_limpa):
                    secao_completa.append(linha_limpa)
        
        if secao_completa:
            texto = "\n".join(secao_completa)
            texto = re.sub(r'[ \t]+', ' ', texto)
            return texto.strip()
        return ""
    
    def extrair_responsabilidade_prestadora(self) -> str:
        """
        Extrai responsabilidade da prestadora de serviço
        Robusto para diferentes formatos (bullets, números, letras)
        """
        secao_completa = []
        coletando = False
        
        for i, linha in enumerate(self.linhas):
            if re.search(r'^13\.\s+Responsabilidade da prestadora de serviço', linha.strip()):
                coletando = True
                continue
            
            if coletando:
                linha_limpa = linha.strip()
                
                # Parar em próxima seção numerada
                if re.match(r'^14\.', linha_limpa):
                    break
                
                # Ignorar sujeiras
                if linha_limpa and not self._eh_sujeira(linha_limpa):
                    secao_completa.append(linha_limpa)
        
        if secao_completa:
            texto = "\n".join(secao_completa)
            texto = re.sub(r'[ \t]+', ' ', texto)
            return texto.strip()
        return ""
    
    def extrair_perfil_desejado_prestadora(self) -> str:
        """
        Extrai Perfil desejado da prestadora de serviço
        Busca pelo título em todo o documento
        """
        secao_completa = []
        coletando = False
        
        for i, linha in enumerate(self.linhas):
            linha_limpa = linha.strip()
            
            # Buscar pelo título
            if re.search(r'Perfil\s+desejado\s+da\s+prestadora', linha_limpa, re.IGNORECASE):
                coletando = True
                continue
            
            if coletando:
                # Parar ao encontrar próxima seção numerada ou outro tópico
                if re.match(r'^\d{1,2}\.|^Pré-diagnóstico|^Observações', linha_limpa, re.IGNORECASE):
                    break
                
                # Parar em marcadores específicos
                if re.match(r'^ETAPA|^HISTÓRICO', linha_limpa, re.IGNORECASE):
                    break
                
                # Ignorar sujeiras
                if linha_limpa and not self._eh_sujeira(linha_limpa):
                    secao_completa.append(linha_limpa)
        
        if secao_completa:
            texto = "\n".join(secao_completa)
            texto = re.sub(r'[ \t]+', ' ', texto)
            return texto.strip()
        return ""
    
    def extrair_descricao(self) -> str:
        """
        Extrai a descrição completa
        Começa na seção "9. Descrição" e vai até antes de "ETAPA 01" ou similar
        Remove sujeiras como "Uso Interno" e "Código da ficha técnica"
        """
        descricao_completa = []
        coletando = False
        
        for i, linha in enumerate(self.linhas):
            # Começar a coletar na seção de descrição
            if re.search(r'^9\.\s+Descrição', linha.strip()):
                coletando = True
                continue
            
            if coletando:
                # Parar quando encontrar as etapas ou outras seções
                if re.search(r'^ETAPA\s+\d+|^10\.|^11\.|^12\.|^13\.|^14\.|^15\.', linha.strip()):
                    break
                
                # Adicionar linha se não for vazia e não for sujeira
                linha_limpa = linha.strip()
                
                # Ignorar linhas de "sujeira" (Uso Interno, Código da ficha técnica)
                if linha_limpa and not re.match(r'^Uso Interno$|^Código da ficha técnica:', linha_limpa):
                    descricao_completa.append(linha_limpa)
        
        # Juntar linhas e limpar espaços extras
        descricao = " ".join(descricao_completa)
        # Remover múltiplos espaços
        descricao = re.sub(r'\s+', ' ', descricao).strip()
        
        return descricao
    
    def extrair_etapas(self) -> List[Dict[str, Any]]:
        """
        Extrai as etapas conforme formato do solutions-data.ts
        Retorna lista de dicts com: id, titulo, ordem, percentual, tipo, descricao, entrega
        """
        etapas = []
        numero_etapa = 1
        i = 0
        
        while i < len(self.linhas):
            linha = self.linhas[i].strip()
            
            # Procurar por linhas que começam com "ETAPA"
            match = re.match(r'^ETAPA\s+(\d+)\s*[\|:]?\s*(.+)$', linha, re.IGNORECASE)
            if match:
                numero_str = match.group(1)
                titulo_base = match.group(2).strip()
                
                # Verificar se há continuação do título na próxima linha
                i += 1
                while i < len(self.linhas):
                    linha_seguinte = self.linhas[i].strip()
                    # Se não é linha vazia, não começa com item de lista, não é ENTREGA, nem é outra etapa
                    if (linha_seguinte and 
                        not re.match(r'^[●○•\d+\-A-Z]\.|^[●○•]\s+', linha_seguinte) and
                        not re.match(r'^ENTREGAS?\s+ETAPA', linha_seguinte, re.IGNORECASE) and
                        not re.match(r'^ETAPA\s+\d+|^\d+\.', linha_seguinte, re.IGNORECASE) and
                        not re.match(r'^Com\s+base|^Realizar', linha_seguinte)):  # Palavras-chave de início de descrição
                        # É continuação do título
                        titulo_base += " " + linha_seguinte
                        i += 1
                    else:
                        break
                
                # Título com formato: "ETAPA 01 | Alinhamento da Proposta"
                titulo = f"ETAPA {numero_str} | {titulo_base}"
                
                # Coletar descrição até encontrar "ENTREGA"
                descricao_linhas = []
                while i < len(self.linhas):
                    linha_atual = self.linhas[i].strip()
                    
                    # Parar quando encontrar a entrega
                    if re.match(r'^ENTREGAS?\s+ETAPA\s+\d+:', linha_atual, re.IGNORECASE):
                        break
                    
                    # Ignorar linhas vazias no início
                    if linha_atual or descricao_linhas:
                        descricao_linhas.append(linha_atual)
                    
                    i += 1
                
                # Remover linhas vazias do final
                while descricao_linhas and not descricao_linhas[-1]:
                    descricao_linhas.pop()
                
                # Juntar preservando quebras de linha para seções
                descricao = "\n".join(descricao_linhas).strip()
                # Não collapsar quebras - vamos manter a estrutura para formatar depois
                
                # Coletar entrega/deliverable
                entrega = ""
                if i < len(self.linhas):
                    linha_entrega = self.linhas[i].strip()
                    if re.match(r'^ENTREGAS?\s+ETAPA\s+\d+:', linha_entrega, re.IGNORECASE):
                        # Extrair o texto após o ":"
                        match_entrega = re.match(r'^ENTREGAS?\s+ETAPA\s+\d+:\s*(.+)', linha_entrega, re.IGNORECASE)
                        if match_entrega:
                            entrega = match_entrega.group(1).strip()
                        
                        # Coletar linhas seguintes até encontrar próxima etapa ou seção
                        i += 1
                        while i < len(self.linhas):
                            linha_proxima = self.linhas[i].strip()
                            
                            # Parar quando encontrar:
                            # - Próxima etapa
                            # - Próxima seção numerada (10., 11., etc)
                            if (re.match(r'^ETAPA\s+\d+', linha_proxima, re.IGNORECASE) or
                                re.match(r'^\d+\.\s+(?!Uso Interno|Código)', linha_proxima)):  # Seção numerada (mas não sujeira)
                                break
                            
                            # Ignorar linhas de sujeira mas continuar coletando
                            if linha_proxima and not self._eh_sujeira(linha_proxima):
                                if entrega:
                                    entrega += " " + linha_proxima
                                else:
                                    entrega = linha_proxima
                            
                            i += 1
                        
                        entrega = entrega.strip()
                
                # Criar estrutura da etapa conforme solutions-data.ts
                # Normalizar descricao com formatação estruturada
                descricao_normalizada = self._normalizar_string_sujeira(descricao)
                descricao_normalizada = self._formatar_descricao_estruturada(descricao_normalizada)
                
                etapa = {
                    "id": f"e{numero_etapa}",
                    "titulo": titulo,
                    "ordem": numero_etapa,
                    "percentual": 0,  # Será preenchido manualmente se houver % no documento
                    "tipo": "Consultoria",  # Será preenchido conforme tipo_servico
                    "descricao": descricao_normalizada,
                    "entrega": self._normalizar_string_sujeira(entrega)
                }
                
                etapas.append(etapa)
                numero_etapa += 1
            else:
                i += 1
        
        return etapas
    
    def extrair_perguntas_diagnostico(self) -> List[Dict[str, Any]]:
        """
        Extrai as perguntas de diagnóstico/pré-diagnóstico
        Retorna lista de dicts com: id, pergunta, tipo, obrigatoria, [opcoes]
        Tipos detectados automaticamente:
        - "sim_nao": Pergunta com palavras-chave que indicam sim/não
        - "texto": Pergunta aberta que necessita resposta em texto
        - "multipla_escolha": Pergunta com opções listadas
        """
        perguntas = []
        i = 0
        numero_pergunta = 1
        
        # Procurar pela seção "Pré-diagnóstico"
        while i < len(self.linhas):
            if re.match(r'^\d+\.\s+Pré-diagnóstico', self.linhas[i].strip(), re.IGNORECASE):
                i += 1
                break
            i += 1
        
        # Processar perguntas enquanto não encontrar próxima seção
        while i < len(self.linhas):
            linha = self.linhas[i].strip()
            
            # Parar quando encontrar "Observações" ou "HISTÓRICO"
            if re.match(r'^\d+\.\s+Observações|^HISTÓRICO', linha, re.IGNORECASE):
                break
            
            # Procurar por linha de pergunta numerada
            match = re.match(r'^(\d+)\.\s+(.+)$', linha)
            if match:
                numero_q = match.group(1)
                texto_pergunta = match.group(2).strip()
                
                # Coletar continuação da pergunta nas linhas seguintes (se houver quebra)
                i += 1
                while i < len(self.linhas):
                    linha_continua = self.linhas[i].strip()
                    
                    # Parar se encontrar próxima pergunta ou seção
                    if re.match(r'^\d+\.\s+', linha_continua):
                        break
                    
                    # Se não é linha vazia e não é sujeira, é continuação
                    if linha_continua and not self._eh_sujeira(linha_continua):
                        texto_pergunta += " " + linha_continua
                        i += 1
                    elif not linha_continua:
                        # Pular linhas vazias no meio da pergunta
                        i += 1
                        # Mas parar se há mais de uma linha vazia
                        if i < len(self.linhas) and not self.linhas[i].strip():
                            break
                    else:
                        i += 1
                        break
                
                texto_pergunta = texto_pergunta.strip()
                
                # Detectar tipo de pergunta
                tipo_pergunta = self._detectar_tipo_pergunta(texto_pergunta)
                
                # Detectar obrigatoriedade (por padrão obrigatória, salvo mencionado "opcional")
                obrigatoria = "opcional" not in texto_pergunta.lower()
                
                # Criar estrutura da pergunta
                pergunta = {
                    "id": str(numero_pergunta),
                    "pergunta": self._limpar_quebras_em_frases(texto_pergunta),
                    "tipo": tipo_pergunta,
                    "obrigatoria": obrigatoria
                }
                
                # Se houver opções, adicionar campo opcoes (apenas para multipla_escolha)
                if tipo_pergunta == "multipla_escolha":
                    opcoes = self._extrair_opcoes_pergunta(texto_pergunta)
                    if opcoes:
                        pergunta["opcoes"] = opcoes
                
                perguntas.append(pergunta)
                numero_pergunta += 1
                continue
            
            i += 1
        
        return perguntas
    
    def _detectar_tipo_pergunta(self, pergunta: str) -> str:
        """
        Detecta o tipo de pergunta baseado em palavras-chave
        Retorna: "sim_nao", "texto" ou "multipla_escolha"
        """
        pergunta_lower = pergunta.lower()
        
        # Detectar multipla_escolha se mencionar "escolha", "selecione", "opções", etc
        if any(palavra in pergunta_lower for palavra in ["escolha", "selecione", "opções", "alternativas"]):
            return "multipla_escolha"
        
        # Detectar perguntas com condições (se sim, se não, qual, como após a pergunta)
        # Exemplo: "Já possui? Se sim, quais as dificuldades?"
        if any(padrao in pergunta_lower for padrao in ["se sim", "se não", "se houver", "se tiver"]):
            return "texto"
        
        # Detectar perguntas abertas (como/qual/quais/onde/quando/por que)
        if any(palavra in pergunta_lower for palavra in ["qual", "como", "quem", "onde", "quando", "por que", "quais"]):
            return "texto"
        
        # Detectar sim/não por palavras-chave
        if any(palavra in pergunta_lower for palavra in ["já possui", "possui experiência", "tem", "possui", "existe", "há", "foi"]):
            if "?" in pergunta:
                return "sim_nao"
        
        # Por padrão, considerar texto
        return "texto"
    
    def _extrair_opcoes_pergunta(self, pergunta: str) -> List[str]:
        """
        Extrai opções de uma pergunta se estiverem entre parênteses ou listadas
        Exemplo: "...? (ERPs, sistemas de despacho, plataformas...)"
        """
        # Procurar por opções entre parênteses
        match = re.search(r'\(([^)]+)\)', pergunta)
        if match:
            opcoes_texto = match.group(1)
            # Dividir por vírgula e limpar
            opcoes = [opt.strip() for opt in opcoes_texto.split(',')]
            return opcoes
        
        return []
    
    def extrair_observacoes(self) -> str:
        """
        Extrai as observações (seção 15. Observações)
        Retorna como texto único concatenando todos os itens com quebra de linha
        """
        observacoes_completas = []
        i = 0
        encontrou_observacoes = False
        
        # Procurar pela seção "Observações"
        while i < len(self.linhas):
            linha = self.linhas[i].strip()
            if re.match(r'^\d+\.\s+Observações', linha, re.IGNORECASE):
                encontrou_observacoes = True
                i += 1
                break
            i += 1
        
        if not encontrou_observacoes:
            return ""
        
        # Coletar todas as observações (itens numerados)
        while i < len(self.linhas):
            linha = self.linhas[i].strip()
            
            # Parar quando encontrar "HISTÓRICO"
            if re.match(r'^HISTÓRICO', linha, re.IGNORECASE):
                break
            
            # Procurar por itens numerados (1., 2., 3., etc)
            match = re.match(r'^(\d+)\.\s+(.+)$', linha)
            if match:
                # Começar com o conteúdo após o número
                texto_obs = match.group(2).strip()
                
                # Coletar continuação nas linhas seguintes
                i += 1
                while i < len(self.linhas):
                    linha_raw = self.linhas[i]
                    linha_continua = linha_raw.strip()
                    
                    # Parar se encontrar próximo item numerado ou HISTÓRICO
                    if re.match(r'^\d+\.\s+', linha_continua) or re.match(r'^HISTÓRICO', linha_continua, re.IGNORECASE):
                        break
                    
                    # Se a linha está vazia, pular
                    if not linha_continua:
                        i += 1
                        continue
                    
                    # Ignorar sujeiras mas continuar coletando próximas linhas
                    if not self._eh_sujeira(linha_continua):
                        # Usar espaço para juntar linhas (não quebra)
                        texto_obs += " " + linha_continua
                    
                    i += 1
                
                observacoes_completas.append(texto_obs.strip())
                continue
            
            i += 1
        
        # Juntar todas as observações com quebra de linha entre elas
        if observacoes_completas:
            # Aplicar limpeza de quebras em frases a cada observação
            observacoes_limpas = [self._limpar_quebras_em_frases(obs) for obs in observacoes_completas]
            return "\n".join(observacoes_limpas)
        
        return ""
    
    def extrair_historico_alteracoes(self) -> List[Dict[str, Any]]:
        """
        Extrai o histórico de alterações em formato tabular
        Padrão da tabela:
        Versão | Data | Link | Responsável
        1 | 06/03/2019 | https://...CS11003-1.pdf | Coordenação Sebraetec
        2 | 14/04/2020 | https://...CS11003-2.pdf | Arthur Carneiro
        3 | 01/01/2021 | https://...CS11003-3.pdf | Flavio Germano Petry
        """
        historico = []
        i = 0
        encontrou_historico = False
        
        # Procurar pela seção "HISTÓRICO DE ALTERAÇÕES"
        while i < len(self.linhas):
            if re.match(r'^HISTÓRICO\s+DE\s+ALTERAÇÕES', self.linhas[i].strip(), re.IGNORECASE):
                encontrou_historico = True
                i += 1
                break
            i += 1
        
        if not encontrou_historico:
            return historico
        
        versoes = []
        datas = []
        responsaveis_bruto = []  # Todas as linhas que parecem ser responsáveis
        
        # Coletar todos os dados da tabela
        while i < len(self.linhas):
            linha = self.linhas[i].strip()
            
            if re.match(r'^Ficha Técnica', linha, re.IGNORECASE):
                break
            
            # Versão: número 1-99 único
            if re.match(r'^\d{1,2}$', linha):
                num = int(linha)
                if num < 100 and num not in versoes:
                    versoes.append(num)
            
            # Data: DD/MM/YYYY
            elif re.match(r'^\d{2}/\d{2}/\d{4}$', linha):
                if linha not in datas:
                    datas.append(linha)
            
            # Responsável: linha que começa com letra maiúscula, não é número/URL
            # Pode ter quebra de linha (e.g., "Flavio Germano" em uma linha, "Petry" em outra)
            elif (re.match(r'^[A-Z]', linha) and 
                  not re.match(r'^\d', linha) and 
                  not re.match(r'^https?://', linha) and
                  not linha.startswith('content') and
                  not linha.startswith('uploads') and
                  not re.match(r'^(Versão|Data|Link|Responsável)', linha, re.IGNORECASE)):
                responsaveis_bruto.append(linha)
            
            i += 1
        
        # Consolidar responsáveis (alguns têm quebra de linha)
        # Ex: ["Coordenação", "Sebraetec", "Arthur Carneiro", "Flavio Germano", "Petry"]
        # -> ["Coordenação Sebraetec", "Arthur Carneiro", "Flavio Germano Petry"]
        
        responsaveis = []
        i = 0
        while i < len(responsaveis_bruto):
            resp_linha = responsaveis_bruto[i]
            resp_componentes = [resp_linha]
            
            # Verificar se próxima linha é continuação (se é palavra pequena como "Sebraetec", "Petry")
            # Heurística: se próxima linha tem 1 palavra ou começa com minúscula no meio, é continuação
            while i + 1 < len(responsaveis_bruto):
                prox = responsaveis_bruto[i + 1]
                # Se próxima tem 1 palavra E é maiúscula, é continuação
                # Ou se responsável atual é "Coordenação" e próximo é "Sebraetec"
                if (len(prox.split()) == 1 and prox[0].isupper()):
                    resp_componentes.append(prox)
                    i += 1
                else:
                    break
            
            responsaveis.append(" ".join(resp_componentes))
            i += 1
        
        # Garantir que temos 3 responsáveis
        while len(responsaveis) < 3:
            responsaveis.append("Coordenação Sebraetec")
        
        # Construir histórico
        for j in range(min(len(versoes), len(datas), 3)):
            registro = {
                "versao": versoes[j],
                "dataAlteracao": datas[j],
                "alteradoPor": responsaveis[j] if j < len(responsaveis) else "Coordenação Sebraetec"
            }
            historico.append(registro)
        
        return historico
    
    def extrair_todos_dados(self) -> Dict[str, Any]:
        """Extrai todos os dados importantes"""
        return {
            "id": self.extrair_codigo_ficha(),
            "nomeSolucao": self.extrair_nome_solucao(),
            "tema": self.extrair_tema(),
            "subtema": self.extrair_subtema(),
            "tipoServico": self.extrair_tipo_servico(),
            "modalidade": self.extrair_modalidade(),
            "publicoAlvo": self.extrair_publico_alvo(),
            "setor": self.extrair_setor(),
            "descricao": self.extrair_descricao(),
            "etapas": self.extrair_etapas(),
            "perguntasDiagnostico": self.extrair_perguntas_diagnostico(),
            "beneficiosResultadosEsperados": self.extrair_beneficios_resultados(),
            "estruturaMateriais": self.extrair_estrutura_materiais(),
            "responsabilidadeEmpresaDemandante": self.extrair_responsabilidade_empresa_demandante(),
            "responsabilidadePrestadora": self.extrair_responsabilidade_prestadora(),
            "perfilDesejadoPrestadora": self.extrair_perfil_desejado_prestadora(),
            "observacoesGerais": self.extrair_observacoes(),
            "historicoAlteracoes": self.extrair_historico_alteracoes()
        }
    
    def salvar_dados_extraidos(self, caminho_saida: str):
        """Salva os dados extraídos em JSON"""
        dados = self.extrair_todos_dados()
        # Normalizar dados removendo quebras em frases
        dados = self._normalizar_dados(dados)
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        print(f"✅ Dados extraídos salvos em: {caminho_saida}")
        return dados

# Teste
if __name__ == "__main__":
    extrator = ExtractorFichaTecnica("saida/Adequacao-de-processos-logisticos-para-exportacao-CI11004-1.md")
    
    print("=" * 60)
    print("DADOS EXTRAÍDOS DA FICHA TÉCNICA")
    print("=" * 60)
    
    dados = extrator.extrair_todos_dados()
    for chave, valor in dados.items():
        print(f"{chave:20} : {valor}")
    
    print("\n" + "=" * 60)
    
    # Salvar também
    extrator.salvar_dados_extraidos("saida/dados_extraidos.json")
