export interface Etapa {
  id: string;
  titulo: string;
  ordem: number;
  percentual: number;
  tipo: string;
  descricao: string;
  entrega: string;
}

export interface PerguntaDiagnostico {
  id: string;
  pergunta: string;
  tipo: 'sim_nao' | 'texto' | 'multipla' | 'multipla_escolha';
  obrigatoria: boolean;
  opcoes?: string[];
}

export interface EditalPorEstado {
  [estado: string]: {
    url?: string;
    status?: 'ativo' | 'suspenso' | 'nao_disponivel';
  };
}

export interface HistoricoAlteracao {
  data?: string;
  dataAlteracao?: string;
  versao: number;
  descricao?: string;
  usuario?: string;
  alteradoPor?: string;
  camposAlterados?: string[];
}

export interface Solution {
  id: string;
  nomeSolucao: string;
  codigo?: string;
  valorTeto?: number;
  dataAtualizacaoEscopo?: string;
  dataAtualizacaoValor?: string;
  tema: string;
  subtema: string;
  tipoServico: string;
  modalidade: string;
  setor?: string;
  setorial?: string[];
  ods?: string[];
  publicoAlvo?: string[];
  estadosDisponiveis?: string[];
  editalPorEstado?: EditalPorEstado;
  objetivo?: string;
  descricao: string;
  beneficiosResultadosEsperados?: string;
  estruturaMateriais?: string;
  responsabilidadeEmpresaDemandante?: string;
  responsabilidadePrestadora?: string;
  perfilDesejadoPrestadora?: string;
  etapas?: Etapa[];
  perguntasDiagnostico?: PerguntaDiagnostico[];
  observacoesGerais?: string;
  observacoesEspecificas?: string;
  versaoAtual?: number;
  historicoAlteracoes?: HistoricoAlteracao[];
  status?: string;
  criadoEm?: string;
  criadoPor?: string;
  atualizadoEm?: string;
  codigoCdt?: string;
  unidade?: string;
  numeroOferta?: string;
}
