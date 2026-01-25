/**
 * Script de integração do Markdown Formatter Agent
 * 
 * Este script demonstra como usar o agent no pipeline MD→JSON
 * para garantir que bullets/numeração sejam separados com quebras de linha
 */

import { markdownFormatterAgent } from './agents/markdown-formatter-agent';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Processa arquivo JSON adicionando quebras de linha antes de bullets/numeração
 */
function processJsonFile(filePath: string): void {
  try {
    console.log(`📋 Processando arquivo: ${filePath}`);
    
    // Lê arquivo JSON
    const rawData = fs.readFileSync(filePath, 'utf-8');
    const jsonData = JSON.parse(rawData);

    // Processa com o agent
    const processedData = markdownFormatterAgent.processSolutionData(jsonData);

    // Salva arquivo processado
    const outputPath = filePath.replace(/\.json$/, '-formatted.json');
    fs.writeFileSync(outputPath, JSON.stringify(processedData, null, 2), 'utf-8');

    console.log(`✅ Arquivo processado e salvo em: ${outputPath}`);

    // Exibe relatório
    markdownFormatterAgent.printReport();

  } catch (error) {
    console.error(`❌ Erro ao processar arquivo: ${error}`);
  }
}

/**
 * Processa todos os arquivos JSON em um diretório
 */
function processDirectory(dirPath: string): void {
  try {
    console.log(`📁 Processando diretório: ${dirPath}`);
    
    const files = fs.readdirSync(dirPath);
    const jsonFiles = files.filter(f => f.endsWith('.json'));

    if (jsonFiles.length === 0) {
      console.warn('⚠️  Nenhum arquivo JSON encontrado no diretório');
      return;
    }

    console.log(`Encontrados ${jsonFiles.length} arquivos JSON\n`);

    jsonFiles.forEach(file => {
      markdownFormatterAgent.resetMemory(); // Reset para cada arquivo
      processJsonFile(path.join(dirPath, file));
      console.log('---\n');
    });

    console.log('✨ Processamento em lote concluído!');

  } catch (error) {
    console.error(`❌ Erro ao processar diretório: ${error}`);
  }
}

/**
 * Exemplo de uso direto com string
 */
function exampleDirectUsage(): void {
  console.log('=== EXEMPLO DE USO DIRETO ===\n');

  const sampleText = `Com base no(s) diagnóstico(s) realizado(s) na etapa anterior, deve-se organizar as informações e orientar a empresa para o processo de implantação do Sistema de Gestão da Qualidade ABNT NBR ISO 9001:2015, como recomendado • propor estratégias e indicadores • definir e organizar os processos de trabalho da empresa • criar procedimentos e normas internas • capacitar os empregados da empresa na ABNT NBR ISO 9001:2015 • orientar e acompanhar a realização de auditoria interna • orientar no tratamento das não-conformidades/oportunidades de melhoria identificadas na auditoria interna.`;

  console.log('ANTES:');
  console.log(sampleText);
  console.log('\n---\n');

  const formatted = markdownFormatterAgent.formatMarkdownText(sampleText);

  console.log('DEPOIS:');
  console.log(formatted);
  console.log('\n');

  markdownFormatterAgent.printReport();
}

// Exporta para uso como módulo
export { processJsonFile, processDirectory };

// Se executado diretamente
if (require.main === module) {
  // Descomente uma das opções abaixo:

  // Opção 1: Exemplo direto
  exampleDirectUsage();

  // Opção 2: Processar arquivo específico
  // processJsonFile('./saida/json/seu-arquivo.json');

  // Opção 3: Processar todos os JSONs em um diretório
  // processDirectory('./saida/json');
}
