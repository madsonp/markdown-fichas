/**
 * Markdown Formatter Agent
 * 
 * Agent Skills:
 * - Detecta bullets e numeração misturados em parágrafos
 * - Adiciona quebras de linha antes de bullets/numeração
 * - Padroniza formatação MD antes de conversão para JSON
 * - Mantém histórico de ajustes realizados
 * - Valida formatação de saída
 */

export interface FormattingAdjustment {
  fieldName: string;
  originalText: string;
  adjustedText: string;
  changesApplied: string[];
  timestamp: Date;
}

export interface AgentMemory {
  adjustmentsHistory: FormattingAdjustment[];
  lastExecuted: Date;
  totalAdjustmentsMade: number;
}

export class MarkdownFormatterAgent {
  private memory: AgentMemory = {
    adjustmentsHistory: [],
    lastExecuted: new Date(),
    totalAdjustmentsMade: 0,
  };

  /**
   * Padrões a detectar em texto
   */
  private patterns = {
    // Bullet seguido de espaço e texto no mesmo parágrafo
    bulletMixed: /([^\n])\s+•\s+/g,
    // Numeração seguida de espaço e texto no mesmo parágrafo
    numberMixed: /([^\n])\s+(\d+\.)\s+/g,
    // Hífen como bullet seguido de espaço e texto no mesmo parágrafo
    dashMixed: /([^\n])\s+-\s+/g,
  };

  /**
   * Processa texto para adicionar quebras de linha antes de bullets/numeração
   */
  formatMarkdownText(text: string): string {
    if (!text) return text;

    let formattedText = text;
    const changes: string[] = [];

    // Detecta e adiciona quebra de linha antes de bullets
    if (this.patterns.bulletMixed.test(formattedText)) {
      formattedText = formattedText.replace(
        this.patterns.bulletMixed,
        '$1\n• '
      );
      changes.push('Adicionada quebra de linha antes de bullets (•)');
    }

    // Detecta e adiciona quebra de linha antes de numeração
    if (this.patterns.numberMixed.test(formattedText)) {
      formattedText = formattedText.replace(
        this.patterns.numberMixed,
        '$1\n$2 '
      );
      changes.push('Adicionada quebra de linha antes de numeração');
    }

    // Detecta e adiciona quebra de linha antes de hífens (quando usado como bullet)
    if (this.patterns.dashMixed.test(formattedText)) {
      // Mais conservador para não quebrar sentenças normais
      const dashLines = formattedText.split('\n');
      const processedLines = dashLines.map(line => {
        // Só aplica se o hífen aparecer no meio de um parágrafo já com bullets/numeração
        if (line.includes('•') || line.match(/\d+\./)) {
          return line.replace(/ - /g, '\n- ');
        }
        return line;
      });
      formattedText = processedLines.join('\n');
      if (changes[changes.length - 1] !== 'Adicionada quebra de linha antes de hífens') {
        changes.push('Adicionada quebra de linha antes de hífens (-)');
      }
    }

    return formattedText;
  }

  /**
   * Processa objeto JSON recursivamente, formatando todos os campos de texto
   */
  processJsonObject(obj: any, fieldName: string = 'root'): any {
    if (obj === null || obj === undefined) return obj;

    if (typeof obj === 'string') {
      const formatted = this.formatMarkdownText(obj);
      if (formatted !== obj) {
        this.recordAdjustment(fieldName, obj, formatted);
      }
      return formatted;
    }

    if (Array.isArray(obj)) {
      return obj.map((item, index) => 
        this.processJsonObject(item, `${fieldName}[${index}]`)
      );
    }

    if (typeof obj === 'object') {
      const processed: any = {};
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          processed[key] = this.processJsonObject(
            obj[key],
            `${fieldName}.${key}`
          );
        }
      }
      return processed;
    }

    return obj;
  }

  /**
   * Processa arquivo JSON completo
   */
  processSolutionData(data: any): any {
    const startTime = new Date();
    const processed = this.processJsonObject(data);
    this.memory.lastExecuted = startTime;
    
    return processed;
  }

  /**
   * Registra um ajuste no histórico
   */
  private recordAdjustment(
    fieldName: string,
    originalText: string,
    adjustedText: string
  ): void {
    const changes: string[] = [];

    if (originalText.match(this.patterns.bulletMixed)) {
      changes.push('Quebra de linha adicionada antes de bullets');
    }
    if (originalText.match(this.patterns.numberMixed)) {
      changes.push('Quebra de linha adicionada antes de numeração');
    }
    if (originalText.match(this.patterns.dashMixed)) {
      changes.push('Quebra de linha adicionada antes de hífens');
    }

    this.memory.adjustmentsHistory.push({
      fieldName,
      originalText: originalText.substring(0, 100),
      adjustedText: adjustedText.substring(0, 100),
      changesApplied: changes,
      timestamp: new Date(),
    });

    this.memory.totalAdjustmentsMade++;
  }

  /**
   * Retorna relatório de ajustes realizados
   */
  getReport(): AgentMemory {
    return {
      ...this.memory,
      lastExecuted: new Date(this.memory.lastExecuted),
    };
  }

  /**
   * Exibe resumo de ajustes no console
   */
  printReport(): void {
    console.log('\n=== MARKDOWN FORMATTER AGENT REPORT ===');
    console.log(`Total de ajustes realizados: ${this.memory.totalAdjustmentsMade}`);
    console.log(`Última execução: ${this.memory.lastExecuted}`);
    console.log('\nAjustes por campo:');
    
    this.memory.adjustmentsHistory.forEach((adjustment, index) => {
      console.log(`\n${index + 1}. Campo: ${adjustment.fieldName}`);
      console.log(`   Alterações: ${adjustment.changesApplied.join(', ')}`);
      console.log(`   Original: "${adjustment.originalText}..."`);
      console.log(`   Ajustado: "${adjustment.adjustedText}..."`);
    });
    
    console.log('\n=====================================\n');
  }

  /**
   * Exporta relatório em formato JSON
   */
  exportReport(): string {
    return JSON.stringify(this.getReport(), null, 2);
  }

  /**
   * Reseta o histórico de memória
   */
  resetMemory(): void {
    this.memory = {
      adjustmentsHistory: [],
      lastExecuted: new Date(),
      totalAdjustmentsMade: 0,
    };
  }
}

// Exporta singleton instance
export const markdownFormatterAgent = new MarkdownFormatterAgent();
