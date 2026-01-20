import { Solution } from './types/solution';

// Template padrão para normalizar fichas com informações incompletas
// Campos faltantes serão preenchidos com valores vazios

export function normalizarFicha(dadosExtraidos: any): Solution {
  const fichaFinal: Solution = {
    // Campos obrigatórios
    id: dadosExtraidos.id || "",
    nomeSolucao: dadosExtraidos.nomeSolucao || "",
    codigo: dadosExtraidos.codigo || "",
    
    // Valores monetários
    valorTeto: dadosExtraidos.valorTeto || 0,
    
    // Datas
    dataAtualizacaoEscopo: dadosExtraidos.dataAtualizacaoEscopo || "",
    dataAtualizacaoValor: dadosExtraidos.dataAtualizacaoValor || "",
    
    // Classificação
    tema: dadosExtraidos.tema || "",
    subtema: dadosExtraidos.subtema || "",
    tipoServico: dadosExtraidos.tipoServico || "",
    modalidade: dadosExtraidos.modalidade || "",
    
    // Arrays - deixados vazios se não informados
    setorial: dadosExtraidos.setorial || [],
    ods: dadosExtraidos.ods || [], // ⬅️ Ficará em branco se não informado
    publicoAlvo: dadosExtraidos.publicoAlvo || [],
    estadosDisponiveis: dadosExtraidos.estadosDisponiveis || [],
    
    // Editais por estado
    editalPorEstado: dadosExtraidos.editalPorEstado || {},
    
    // Descrições e objetivos
    objetivo: dadosExtraidos.objetivo || "",
    descricao: dadosExtraidos.descricao || "",
    beneficiosResultadosEsperados: dadosExtraidos.beneficiosResultadosEsperados || "",
    estruturaMateriais: dadosExtraidos.estruturaMateriais || "",
    
    // Responsabilidades
    responsabilidadeEmpresaDemandante: dadosExtraidos.responsabilidadeEmpresaDemandante || "",
    responsabilidadePrestadora: dadosExtraidos.responsabilidadePrestadora || "",
    
    // Perfil
    perfilDesejadoPrestadora: dadosExtraidos.perfilDesejadoPrestadora || "",
    
    // Etapas e diagnóstico
    etapas: dadosExtraidos.etapas || [],
    perguntasDiagnostico: dadosExtraidos.perguntasDiagnostico || [],
    
    // Observações
    observacoesGerais: dadosExtraidos.observacoesGerais || "",
    observacoesEspecificas: dadosExtraidos.observacoesEspecificas || "",
    
    // Versionamento
    versaoAtual: dadosExtraidos.versaoAtual || 1,
    historicoAlteracoes: dadosExtraidos.historicoAlteracoes || []
  };

  return fichaFinal;
}

// Exemplo de uso com dados incompletos
export const exemploFichaIncompleta = {
  id: "2",
  nomeSolucao: "Consultoria em Marketing Digital",
  codigo: "415082",
  // ods está faltando - ficará vazio
  // publicoAlvo está faltando - ficará vazio
  // estadosDisponiveis está faltando - ficará vazio
  tema: "Gestão Empresarial",
  subtema: "Marketing",
  tipoServico: "Consultoria",
  modalidade: "Presencial",
  objetivo: "Auxiliar empresas na implementação de estratégias de marketing digital.",
  descricao: "Serviço de consultoria em marketing digital.",
  // ... outros campos podem estar incompletos
};

// Resultado após normalização
export const fichaProcessada = normalizarFicha(exemploFichaIncompleta);

// Saída esperada:
// {
//   ...outros campos,
//   ods: [],              // ⬅️ Vazio conforme solicitado
//   publicoAlvo: [],      // ⬅️ Vazio conforme solicitado
//   estadosDisponiveis: [],  // ⬅️ Vazio conforme solicitado
//   ...
// }
