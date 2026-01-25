"""
Markdown Formatter Agent para Python
Processa textos adicionando quebras de linha antes de bullets/numeração
"""
import re
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path


class MarkdownFormatterAgent:
    """Agent responsável por normalizar formatação de text com bullets/numeração"""
    
    def __init__(self):
        """Inicializa o agent com configurações padrão"""
        self.memory = {
            'adjustmentsHistory': [],
            'lastExecuted': None,
            'totalAdjustmentsMade': 0,
        }
        
        # Padrões regex para detectar problemas
        self.patterns = {
            # Bullet seguido de espaço e texto no mesmo parágrafo
            'bulletMixed': re.compile(r'([^\n])\s+•\s+'),
            # Numeração seguida de espaço e texto no mesmo parágrafo
            'numberMixed': re.compile(r'([^\n])\s+(\d+\.)\s+'),
            # Hífen como bullet seguido de espaço e texto no mesmo parágrafo
            'dashMixed': re.compile(r'([^\n])\s+-\s+(?!\s)'),
        }
        
        # Campos de texto que devem ser processados
        self.text_fields = [
            'descricao', 'objetivo', 'descricaoDetalhada', 'entrega',
            'beneficiosResultadosEsperados', 'estruturaMateriais',
            'responsabilidadeEmpresaDemandante', 'responsabilidadePrestadora',
            'perfilDesejadoPrestadora', 'observacoes', 'notas', 'conteudo',
            'texto', 'observacoesGerais', 'observacoesEspecificas'
        ]

    def format_markdown_text(self, text: str) -> str:
        """
        Processa texto para adicionar quebras de linha antes de bullets/numeração
        
        Args:
            text: Texto para processar
            
        Returns:
            Texto formatado com quebras de linha
        """
        if not text or not isinstance(text, str):
            return text

        formatted_text = text
        changes = []

        # Detecta e adiciona quebra de linha antes de bullets
        if self.patterns['bulletMixed'].search(formatted_text):
            formatted_text = self.patterns['bulletMixed'].sub(r'\1\n• ', formatted_text)
            changes.append('Quebra de linha adicionada antes de bullets (•)')

        # Detecta e adiciona quebra de linha antes de numeração
        if self.patterns['numberMixed'].search(formatted_text):
            formatted_text = self.patterns['numberMixed'].sub(r'\1\n\2 ', formatted_text)
            changes.append('Quebra de linha adicionada antes de numeração')

        # Detecta e adiciona quebra de linha antes de hífens
        if self.patterns['dashMixed'].search(formatted_text):
            formatted_text = self.patterns['dashMixed'].sub(r'\1\n- ', formatted_text)
            changes.append('Quebra de linha adicionada antes de hífens (-)')

        return formatted_text

    def process_json_object(self, obj: Any, field_name: str = 'root') -> Any:
        """
        Processa objeto recursivamente, formatando todos os campos de texto
        
        Args:
            obj: Objeto a processar (dict, list, string, etc)
            field_name: Nome do campo (para rastreamento)
            
        Returns:
            Objeto processado
        """
        if obj is None:
            return obj

        # Se é string, processar com o formatter
        if isinstance(obj, str):
            formatted = self.format_markdown_text(obj)
            if formatted != obj:
                self._record_adjustment(field_name, obj, formatted)
            return formatted

        # Se é lista, processar recursivamente
        if isinstance(obj, list):
            return [
                self.process_json_object(item, f'{field_name}[{idx}]')
                for idx, item in enumerate(obj)
            ]

        # Se é dict, processar recursivamente
        if isinstance(obj, dict):
            processed = {}
            for key, value in obj.items():
                processed[key] = self.process_json_object(
                    value,
                    f'{field_name}.{key}'
                )
            return processed

        return obj

    def process_solution_data(self, data: Any) -> Any:
        """
        Processa dados completos de uma solução
        
        Args:
            data: Dados da solução (dict)
            
        Returns:
            Dados processados
        """
        start_time = datetime.now()
        processed = self.process_json_object(data)
        self.memory['lastExecuted'] = start_time.strftime("%d/%m/%Y %H:%M:%S")
        
        return processed

    def _record_adjustment(self, field_name: str, original: str, adjusted: str) -> None:
        """Registra um ajuste no histórico"""
        changes = []

        if self.patterns['bulletMixed'].search(original):
            changes.append('Quebra de linha adicionada antes de bullets')
        if self.patterns['numberMixed'].search(original):
            changes.append('Quebra de linha adicionada antes de numeração')
        if self.patterns['dashMixed'].search(original):
            changes.append('Quebra de linha adicionada antes de hífens')

        adjustment = {
            'fieldName': field_name,
            'originalText': original[:100],
            'adjustedText': adjusted[:100],
            'changesApplied': changes,
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }

        self.memory['adjustmentsHistory'].append(adjustment)
        self.memory['totalAdjustmentsMade'] += 1

    def get_report(self) -> Dict[str, Any]:
        """Retorna relatório de ajustes realizados"""
        return self.memory.copy()

    def print_report(self) -> None:
        """Exibe resumo de ajustes no console"""
        report = self.get_report()
        
        print('\n' + '=' * 70)
        print('📋 MARKDOWN FORMATTER AGENT REPORT')
        print('=' * 70)
        print(f"✅ Total de ajustes realizados: {report['totalAdjustmentsMade']}")
        print(f"⏱️  Última execução: {report['lastExecuted']}")
        
        if report['adjustmentsHistory']:
            print('\n📝 Ajustes por campo:')
            print('-' * 70)
            
            for idx, adjustment in enumerate(report['adjustmentsHistory'], 1):
                print(f"\n{idx}. Campo: {adjustment['fieldName']}")
                print(f"   Alterações: {', '.join(adjustment['changesApplied'])}")
                print(f"   Original:  \"{adjustment['originalText']}...\"")
                print(f"   Ajustado:  \"{adjustment['adjustedText']}...\"")
        else:
            print('\n✨ Nenhum ajuste necessário')
        
        print('\n' + '=' * 70 + '\n')

    def export_report(self) -> str:
        """Exporta relatório em formato JSON"""
        import json
        return json.dumps(self.get_report(), indent=2, ensure_ascii=False)

    def reset_memory(self) -> None:
        """Reseta o histórico de memória"""
        self.memory = {
            'adjustmentsHistory': [],
            'lastExecuted': None,
            'totalAdjustmentsMade': 0,
        }


# Instância singleton
_formatter_agent = None

def get_formatter_agent() -> MarkdownFormatterAgent:
    """Retorna instância singleton do agent"""
    global _formatter_agent
    if _formatter_agent is None:
        _formatter_agent = MarkdownFormatterAgent()
    return _formatter_agent
