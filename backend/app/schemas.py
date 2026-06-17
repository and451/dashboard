"""Esquemas (Pydantic) da API - camada semantica do dominio Orcamento.

Reproduz, de forma documentada, as metricas que um painel de execucao
orcamentaria (origem DaaS SERPRO / SIAFI) entrega.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class Registro(BaseModel):
    """Fato de execucao orcamentaria (grao: ano/mes x dimensoes)."""

    ano: int = Field(..., examples=[2025])
    mes: int = Field(..., ge=1, le=12)
    uo: str = Field(..., description="Unidade Orcamentaria", examples=["24205"])
    programa: str = Field(..., examples=["2107 - Programa Espacial Brasileiro"])
    acao: str = Field(..., examples=["14XJ - Desenvolvimento de Satelites"])
    ptres: str = Field(..., examples=["193456"])
    funcao: str = Field(..., examples=["19 - Ciencia e Tecnologia"])
    grupo_despesa: str = Field(..., examples=["4 - Investimentos"])
    fonte: str = Field(..., examples=["100 - Recursos Ordinarios"])
    dotacao_inicial: float
    dotacao_atual: float
    empenhado: float
    liquidado: float
    pago: float


class KPIs(BaseModel):
    """Indicadores agregados (cards do painel)."""

    dotacao_atual: float
    empenhado: float
    liquidado: float
    pago: float
    pct_empenhado: float = Field(..., description="empenhado / dotacao_atual")
    pct_liquidado: float = Field(..., description="liquidado / dotacao_atual")
    pct_pago: float = Field(..., description="pago / dotacao_atual")
    registros: int


class PontoSerie(BaseModel):
    mes: int
    empenhado: float
    liquidado: float
    pago: float


class ItemRanking(BaseModel):
    rotulo: str
    dotacao_atual: float
    empenhado: float
    liquidado: float
    pago: float
    pct_empenhado: float


class Dimensoes(BaseModel):
    """Valores distintos para popular filtros no frontend."""

    anos: list[int]
    programas: list[str]
    acoes: list[str]
    funcoes: list[str]
    grupos_despesa: list[str]
    fontes: list[str]


class RegistrosPaginados(BaseModel):
    total: int
    pagina: int
    tamanho: int
    itens: list[Registro]


# ============================================================================
# Auditoria — Saldos Alongados (SIAFI / Tesouro Gerencial)
# ============================================================================

class SaldoAlongado(BaseModel):
    """Conta contábil com saldo repetido por N meses consecutivos."""

    ug: str = Field(..., description="Código da UG (ex: 24205000)")
    desc_ug: str
    contabil: str = Field(..., description="Conta contábil (ex: 11111001)")
    desc_contabil: str
    corrente: str
    meses_alongados: int = Field(..., description="Nº de meses consecutivos com saldo igual")
    saldo_atual: float
    mes_referencia: str = Field(..., description="Mês de referência (YYYY-MM)")


class AuditoriaResumo(BaseModel):
    """Resumo da auditoria de saldos alongados."""

    total_contas: int
    total_alongadas: int
    maior_alongamento: int = Field(..., description="Maior nº de meses consecutivos")
    saldo_total_alongado: float
    meses_analisados: int


# ============================================================================
# Contratos
# ============================================================================
class Contrato(BaseModel):
    id: str
    numero: str
    objeto: str
    fornecedor: str
    cnpj: str
    modalidade: str
    area: str
    valor_inicial: float
    valor_atual: float
    aditivos: int
    dt_inicio: str
    dt_fim: str
    status: str
    pct_execucao: float
    saldo_executar: float
    uo: str


class KpiContratos(BaseModel):
    total_contratos: int
    valor_total: float
    saldo_executar: float
    em_execucao: int
    pct_execucao_media: float


# ============================================================================
# RH / Gestão de Pessoas
# ============================================================================
class Servidor(BaseModel):
    matricula: str
    nome: str
    cargo: str
    lotacao: str
    regime: str
    salario: float
    admissao: str
    situacao: str
    pgd_participante: bool
    pgd_programa: str | None
    meta_atual: int
    meta_concluida: int


class KpiRH(BaseModel):
    total_servidores: int
    ativos: int
    participantes_pgd: int
    media_salarial: float


# ============================================================================
# Comunicação
# ============================================================================
class Materia(BaseModel):
    id: str
    titulo: str
    veiculo: str
    tipo: str
    categoria: str
    data: str
    url: str
    clipping: bool
    repercussao: int


class Atendimento(BaseModel):
    id: str
    data: str
    solicitante: str
    assunto: str
    status: str
    prazo_dias: int
    respondido_em_dias: int


class Postagem(BaseModel):
    id: str
    plataforma: str
    data: str
    conteudo: str
    alcance: int
    engajamento: int
    cliques: int


class KpiComunicacao(BaseModel):
    total_materias: int
    total_atendimentos: int
    total_postagens: int
    materias_clipping: int
    repercussao_total: int
    alcance_total: int


# ============================================================================
# Educação
# ============================================================================
class Curso(BaseModel):
    id: str
    nome: str
    unidade: str
    nivel: str
    publico: str
    vagas: int
    inscritos: int
    concluintes: int
    taxa_conclusao: float
    carga_horaria: int
    dt_inicio: str
    status: str
    custo: float


class Aluno(BaseModel):
    id: str
    nome: str
    cpf: str
    idade: int
    escolaridade: str
    instituicao_origem: str
    cursos_concluidos: int
    cursos_em_andamento: int
    certificacoes: int
    avaliacao_media: float


class KpiEducacao(BaseModel):
    total_cursos: int
    total_vagas: int
    total_inscritos: int
    total_concluintes: int
    total_alunos: int
    media_avaliacao: float


# ============================================================================
# Operações Espaciais
# ============================================================================
class Lancamento(BaseModel):
    id: str
    nome: str
    foguete: str
    base: str
    data_prevista: str
    data_real: str | None
    status: str
    carga: str
    altitude_km: float | None
    custo_missao: float
    sucesso: bool | None


class Satelite(BaseModel):
    nome: str
    aplicacao: str
    status: str
    dt_lancamento: str
    operador: str
    vida_util_anos: int
    massa_kg: float
    custo_desenvolvimento: float


class KpiOperacoes(BaseModel):
    total_lancamentos: int
    concluidos: int
    taxa_sucesso: float
    custo_total: float
    satelites_operacionais: int
    investimento_satelites: float


# ============================================================================
# Governança
# ============================================================================
class Ato(BaseModel):
    id: str
    numero: str
    tipo: str
    area: str
    ementa: str
    dt_publicacao: str
    status: str
    link: str


class Integridade(BaseModel):
    id: str
    data: str
    tipo: str
    area: str
    status: str
    dias_aberto: int
    anonimo: bool


class Agenda(BaseModel):
    id: str
    titulo: str
    data: str
    hora: str
    local: str
    participantes: int
    area: str
    tipo: str


class Portal(BaseModel):
    canal: str
    ano: int
    mes: int
    acessos: int
    sessoes: int
    solicitacoes: int
    atendidas: int
    taxa_atendimento: float


class KpiGovernanca(BaseModel):
    total_atos: int
    atos_vigentes: int
    total_integridade: int
    pendencias_integridade: int
    total_agendas: int
    acessos_portais: int


# ============================================================================
# Eventos
# ============================================================================
class Evento(BaseModel):
    id: str
    titulo: str
    tipo: str
    data: str
    local: str
    publico: str
    participantes: int
    participantes_presenciais: int
    custo: float
    status: str
    area_organizadora: str


class KpiEventos(BaseModel):
    total_eventos: int
    realizados: int
    participantes_total: int
    custo_total: float


# ============================================================================
# TransfereGov
# ============================================================================
class ProgramaTransfere(BaseModel):
    programa: str
    codigo: str
    status: str
    valor_total: float
    valor_executado: float
    pct_execucao: float
    repasses: int
    convenentes: int
    dt_inicio: str
    dt_fim_prevista: str


class Repasse(BaseModel):
    id: str
    programa: str
    repasse: str
    valor: float
    data: str
    status: str


class KpiTransfereGov(BaseModel):
    total_programas: int
    valor_total_programado: float
    valor_total_executado: float
    total_repasses: int
    repasses_efetivados: int


# ============================================================================
# DOU
# ============================================================================
class PublicacaoDOU(BaseModel):
    id: str
    data: str
    secao: str
    tipo: str
    orgao: str
    ementa: str
    referencia_aeb: bool
    link: str


# ============================================================================
# Acordos Internacionais
# ============================================================================
class Acordo(BaseModel):
    id: str
    tipo: str
    pais: str
    area: str
    instituicao_parceira: str
    dt_assinatura: str
    dt_vigencia: str
    status: str
    valor_previsto: float | None
    projetos_vinculados: int


class KpiAcordos(BaseModel):
    total_acordos: int
    vigentes: int
    projetos_vinculados: int
    valor_total_previsto: float


# ============================================================================
# DGEP / Planejamento Estratégico
# ============================================================================
class MetaPDE(BaseModel):
    eixo: str
    meta: str
    indicador: str
    meta_ano: int
    valor_previsto: float
    valor_realizado: float
    status: str
    responsavel: str


class KpiDGEP(BaseModel):
    total_metas: int
    concluidas: int
    pct_conclusao: float
    atrasadas: int
