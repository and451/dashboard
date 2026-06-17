// Cliente da API do backend (FastAPI). Em dev, o Vite faz proxy de /api -> :8000.

export interface KPIs {
  dotacao_atual: number;
  empenhado: number;
  liquidado: number;
  pago: number;
  pct_empenhado: number;
  pct_liquidado: number;
  pct_pago: number;
  registros: number;
}

export interface PontoSerie {
  mes: number;
  empenhado: number;
  liquidado: number;
  pago: number;
}

export interface ItemRanking {
  rotulo: string;
  dotacao_atual: number;
  empenhado: number;
  liquidado: number;
  pago: number;
  pct_empenhado: number;
}

export interface Dimensoes {
  anos: number[];
  programas: string[];
  acoes: string[];
  funcoes: string[];
  grupos_despesa: string[];
  fontes: string[];
}

export type Filtros = {
  ano?: number;
  programa?: string;
  acao?: string;
  funcao?: string;
  grupo_despesa?: string;
  fonte?: string;
};

// Auditoria
export interface SaldoAlongado {
  ug: string; desc_ug: string; contabil: string; desc_contabil: string;
  corrente: string; meses_alongados: number; saldo_atual: number; mes_referencia: string;
}
export interface AuditoriaResumo {
  total_contas: number; total_alongadas: number; maior_alongamento: number;
  saldo_total_alongado: number; meses_analisados: number;
}

// Contratos
export interface Contrato {
  id: string; numero: string; objeto: string; fornecedor: string; cnpj: string;
  modalidade: string; area: string; valor_inicial: number; valor_atual: number;
  aditivos: number; dt_inicio: string; dt_fim: string; status: string;
  pct_execucao: number; saldo_executar: number; uo: string;
}
export interface KpiContratos {
  total_contratos: number; valor_total: number; saldo_executar: number;
  em_execucao: number; pct_execucao_media: number;
}

// RH
export interface Servidor {
  matricula: string; nome: string; cargo: string; lotacao: string; regime: string;
  salario: number; admissao: string; situacao: string; pgd_participante: boolean;
  pgd_programa: string | null; meta_atual: number; meta_concluida: number;
}
export interface KpiRH {
  total_servidores: number; ativos: number; participantes_pgd: number; media_salarial: number;
}

// Comunicação
export interface Materia {
  id: string; titulo: string; veiculo: string; tipo: string; categoria: string;
  data: string; url: string; clipping: boolean; repercussao: number;
}
export interface Atendimento {
  id: string; data: string; solicitante: string; assunto: string; status: string;
  prazo_dias: number; respondido_em_dias: number;
}
export interface Postagem {
  id: string; plataforma: string; data: string; conteudo: string; alcance: number;
  engajamento: number; cliques: number;
}
export interface KpiComunicacao {
  total_materias: number; total_atendimentos: number; total_postagens: number;
  materias_clipping: number; repercussao_total: number; alcance_total: number;
}

// Educação
export interface Curso {
  id: string; nome: string; unidade: string; nivel: string; publico: string;
  vagas: number; inscritos: number; concluintes: number; taxa_conclusao: number;
  carga_horaria: number; dt_inicio: string; status: string; custo: number;
}
export interface Aluno {
  id: string; nome: string; cpf: string; idade: number; escolaridade: string;
  instituicao_origem: string; cursos_concluidos: number; cursos_em_andamento: number;
  certificacoes: number; avaliacao_media: number;
}
export interface KpiEducacao {
  total_cursos: number; total_vagas: number; total_inscritos: number;
  total_concluintes: number; total_alunos: number; media_avaliacao: number;
}

// Operações
export interface Lancamento {
  id: string; nome: string; foguete: string; base: string; data_prevista: string;
  data_real: string | null; status: string; carga: string; altitude_km: number | null;
  custo_missao: number; sucesso: boolean | null;
}
export interface Satelite {
  nome: string; aplicacao: string; status: string; dt_lancamento: string;
  operador: string; vida_util_anos: number; massa_kg: number; custo_desenvolvimento: number;
}
export interface KpiOperacoes {
  total_lancamentos: number; concluidos: number; taxa_sucesso: number;
  custo_total: number; satelites_operacionais: number; investimento_satelites: number;
}

// Governança
export interface Ato {
  id: string; numero: string; tipo: string; area: string; ementa: string;
  dt_publicacao: string; status: string; link: string;
}
export interface Integridade {
  id: string; data: string; tipo: string; area: string; status: string;
  dias_aberto: number; anonimo: boolean;
}
export interface Agenda {
  id: string; titulo: string; data: string; hora: string; local: string;
  participantes: number; area: string; tipo: string;
}
export interface Portal {
  canal: string; ano: number; mes: number; acessos: number; sessoes: number;
  solicitacoes: number; atendidas: number; taxa_atendimento: number;
}
export interface KpiGovernanca {
  total_atos: number; atos_vigentes: number; total_integridade: number;
  pendencias_integridade: number; total_agendas: number; acessos_portais: number;
}

// Eventos
export interface Evento {
  id: string; titulo: string; tipo: string; data: string; local: string; publico: string;
  participantes: number; participantes_presenciais: number; custo: number;
  status: string; area_organizadora: string;
}
export interface KpiEventos {
  total_eventos: number; realizados: number; participantes_total: number; custo_total: number;
}

// TransfereGov
export interface ProgramaTransfere {
  programa: string; codigo: string; status: string; valor_total: number;
  valor_executado: number; pct_execucao: number; repasses: number; convenentes: number;
  dt_inicio: string; dt_fim_prevista: string;
}
export interface Repasse {
  id: string; programa: string; repasse: string; valor: number; data: string; status: string;
}
export interface KpiTransfereGov {
  total_programas: number; valor_total_programado: number; valor_total_executado: number;
  total_repasses: number; repasses_efetivados: number;
}

// DOU
export interface PublicacaoDOU {
  id: string; data: string; secao: string; tipo: string; orgao: string;
  ementa: string; referencia_aeb: boolean; link: string;
}

// Acordos
export interface Acordo {
  id: string; tipo: string; pais: string; area: string; instituicao_parceira: string;
  dt_assinatura: string; dt_vigencia: string; status: string; valor_previsto: number | null;
  projetos_vinculados: number;
}
export interface KpiAcordos {
  total_acordos: number; vigentes: number; projetos_vinculados: number; valor_total_previsto: number;
}

// DGEP
export interface MetaPDE {
  eixo: string; meta: string; indicador: string; meta_ano: number;
  valor_previsto: number; valor_realizado: number; status: string; responsavel: string;
}
export interface KpiDGEP {
  total_metas: number; concluidas: number; pct_conclusao: number; atrasadas: number;
}

const BASE = "/api/v1/orcamento";

function qs(filtros: Filtros): string {
  const p = new URLSearchParams();
  Object.entries(filtros).forEach(([k, v]) => {
    if (v !== undefined && v !== "" && v !== null) p.append(k, String(v));
  });
  const s = p.toString();
  return s ? `?${s}` : "";
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Erro ${res.status} em ${path}`);
  return res.json() as Promise<T>;
}

function qsWith(filtros: Filtros, extra: Record<string, string>): string {
  const p = new URLSearchParams();
  Object.entries(filtros).forEach(([k, v]) => {
    if (v !== undefined && v !== "" && v !== null) p.append(k, String(v));
  });
  Object.entries(extra).forEach(([k, v]) => p.append(k, v));
  const s = p.toString();
  return s ? `?${s}` : "";
}

const BASE_AUDITORIA = "/api/v1/auditoria";
const BASE_CONTRATOS = "/api/v1/contratos";
const BASE_RH = "/api/v1/rh";
const BASE_COM = "/api/v1/comunicacao";
const BASE_EDU = "/api/v1/educacao";
const BASE_OPS = "/api/v1/operacoes";
const BASE_GOV = "/api/v1/governanca";
const BASE_EVT = "/api/v1/eventos";
const BASE_TG = "/api/v1/transferegov";
const BASE_DOU = "/api/v1/dou";
const BASE_ACD = "/api/v1/acordos";
const BASE_DGEP = "/api/v1/dgep";

export const api = {
  // Orçamento
  dimensoes: () => get<Dimensoes>(`${BASE}/dimensoes`),
  kpis: (f: Filtros) => get<KPIs>(`${BASE}/kpis${qs(f)}`),
  serie: (f: Filtros) => get<PontoSerie[]>(`${BASE}/serie-mensal${qs(f)}`),
  ranking: (f: Filtros, por: string) => get<ItemRanking[]>(`${BASE}/ranking${qsWith(f, { por })}`),

  // Auditoria
  auditoriaSaldos: (meses: number, minMeses: number, ug?: string) => {
    const q = `meses=${meses}&min_meses=${minMeses}` + (ug ? `&ug=${encodeURIComponent(ug)}` : "");
    return get<SaldoAlongado[]>(`${BASE_AUDITORIA}/saldos-alongados?${q}`);
  },
  auditoriaResumo: (meses: number, ug?: string) => {
    const q = `meses=${meses}` + (ug ? `&ug=${encodeURIComponent(ug)}` : "");
    return get<AuditoriaResumo>(`${BASE_AUDITORIA}/saldos-alongados/resumo?${q}`);
  },

  // Contratos
  contratos: (params?: Record<string, string>) => get<Contrato[]>(`${BASE_CONTRATOS}${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  contratosKpis: () => get<KpiContratos>(`${BASE_CONTRATOS}/kpis`),
  contratosPorStatus: () => get<Record<string, any>[]>(`${BASE_CONTRATOS}/por-status`),
  contratosPorArea: () => get<Record<string, any>[]>(`${BASE_CONTRATOS}/por-area`),

  // RH
  servidores: (params?: Record<string, string>) => get<Servidor[]>(`${BASE_RH}/servidores${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  rhKpis: () => get<KpiRH>(`${BASE_RH}/kpis`),
  rhPorCargo: () => get<Record<string, any>[]>(`${BASE_RH}/por-cargo`),
  rhPorLotacao: () => get<Record<string, any>[]>(`${BASE_RH}/por-lotacao`),
  forcaTrabalho: () => get<Record<string, any>[]>(`${BASE_RH}/forca-trabalho`),

  // Comunicação
  materias: (params?: Record<string, string>) => get<Materia[]>(`${BASE_COM}/materias${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  atendimentos: () => get<Atendimento[]>(`${BASE_COM}/atendimentos`),
  postagens: () => get<Postagem[]>(`${BASE_COM}/postagens`),
  comunicacaoKpis: () => get<KpiComunicacao>(`${BASE_COM}/kpis`),
  materiasPorCategoria: () => get<Record<string, any>[]>(`${BASE_COM}/materias-por-categoria`),
  postagensPorPlataforma: () => get<Record<string, any>[]>(`${BASE_COM}/postagens-por-plataforma`),

  // Educação
  cursos: (params?: Record<string, string>) => get<Curso[]>(`${BASE_EDU}/cursos${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  alunos: () => get<Aluno[]>(`${BASE_EDU}/alunos`),
  educacaoKpis: () => get<KpiEducacao>(`${BASE_EDU}/kpis`),
  cursosPorUnidade: () => get<Record<string, any>[]>(`${BASE_EDU}/cursos-por-unidade`),

  // Operações
  lancamentos: (params?: Record<string, string>) => get<Lancamento[]>(`${BASE_OPS}/lancamentos${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  satelites: (params?: Record<string, string>) => get<Satelite[]>(`${BASE_OPS}/satelites${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  operacoesKpis: () => get<KpiOperacoes>(`${BASE_OPS}/kpis`),

  // Governança
  atos: (params?: Record<string, string>) => get<Ato[]>(`${BASE_GOV}/atos${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  integridade: (params?: Record<string, string>) => get<Integridade[]>(`${BASE_GOV}/integridade${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  agendas: (params?: Record<string, string>) => get<Agenda[]>(`${BASE_GOV}/agendas${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  portais: () => get<Portal[]>(`${BASE_GOV}/portais`),
  governancaKpis: () => get<KpiGovernanca>(`${BASE_GOV}/kpis`),

  // Eventos
  eventos: (params?: Record<string, string>) => get<Evento[]>(`${BASE_EVT}${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  eventosKpis: () => get<KpiEventos>(`${BASE_EVT}/kpis`),
  eventosPorTipo: () => get<Record<string, any>[]>(`${BASE_EVT}/por-tipo`),

  // TransfereGov
  programasTransfere: (status?: string) => get<ProgramaTransfere[]>(`${BASE_TG}/programas${status ? "?status=" + status : ""}`),
  repasses: (status?: string) => get<Repasse[]>(`${BASE_TG}/repasses${status ? "?status=" + status : ""}`),
  transferegovKpis: () => get<KpiTransfereGov>(`${BASE_TG}/kpis`),

  // DOU
  publicacoesDOU: (params?: Record<string, string>) => get<PublicacaoDOU[]>(`${BASE_DOU}/publicacoes${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  douKpis: () => get<Record<string, any>>(`${BASE_DOU}/kpis`),

  // Acordos
  acordos: (params?: Record<string, string>) => get<Acordo[]>(`${BASE_ACD}${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  acordosKpis: () => get<KpiAcordos>(`${BASE_ACD}/kpis`),
  acordosPorPais: () => get<Record<string, any>[]>(`${BASE_ACD}/por-pais`),

  // DGEP
  pde: (params?: Record<string, string>) => get<MetaPDE[]>(`${BASE_DGEP}/pde${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  dgepKpis: () => get<KpiDGEP>(`${BASE_DGEP}/kpis`),
  metasPorEixo: () => get<Record<string, any>[]>(`${BASE_DGEP}/metas-por-eixo`),
};
