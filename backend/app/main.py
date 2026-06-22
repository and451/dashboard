"""API do PoC - Plataforma de Paineis AEB (dominio Orcamento / SERPRO).

Executar:
    uvicorn app.main:app --reload --port 8000
Docs (Swagger/OpenAPI): http://localhost:8000/docs
"""
from __future__ import annotations

import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from . import services
from .auditoria import obter_saldos_alongados_sinteticos
from .schemas import (
    Acordo, Agenda, Aluno, Ato, AuditoriaResumo, Contrato, Curso,
    Dimensoes, Evento, Integridade, ItemRanking, KPIs, KpiAcordos,
    KpiContratos, KpiDGEP, KpiEducacao, KpiEventos, KpiGovernanca,
    KpiOperacoes, KpiRH, KpiComunicacao, KpiTransfereGov, Lancamento,
    Materia, MetaPDE, Portal, PontoSerie, Postagem, PublicacaoDOU,
    Registro, RegistrosPaginados, Repasse, SaldoAlongado, Satelite,
    Servidor, ProgramaTransfere, Atendimento,
)
from .dominios import (
    contratos_services, rh_services, comunicacao_services,
    educacao_services, operacoes_services, governanca_services,
    eventos_services, transferegov_services, dou_services,
    acordo_services, dgep_services,
)

app = FastAPI(
    title="Plataforma de Paineis AEB - API (PoC)",
    version="0.1.0",
    description=(
        "Prova de conceito que reproduz, de forma documentada e programavel, um "
        "painel de execucao orcamentaria (origem DaaS SERPRO / SIAFI, UO 24205). "
        "Dados sinteticos no PoC; em producao, lidos do Data Warehouse via ELT."
    ),
)

# CORS: dev (Vite) + producao (Vercel + outras)
# Em producao, restringir para a URL especifica do frontend
_origins_str = os.getenv("CORS_ORIGINS", "")
_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
if _origins_str:
    _origins.extend([o.strip() for o in _origins_str.split(",") if o.strip()])
# Fallback: permite tudo em dev, mas em producao usar CORS_ORIGINS
allow_all = os.getenv("ENV", "development") == "development"
app.add_middleware(
    CORSMiddleware,
    allow_origins="*" if allow_all else _origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

V1 = "/api/v1"


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok"}


@app.get(f"{V1}/orcamento/dimensoes", response_model=Dimensoes, tags=["orcamento"])
def get_dimensoes() -> Dimensoes:
    """Valores distintos para popular os filtros do painel."""
    return Dimensoes(**services.dimensoes())


@app.get(f"{V1}/orcamento/kpis", response_model=KPIs, tags=["orcamento"])
def kpis_endpoint(
    ano: int | None = None,
    programa: str | None = None,
    acao: str | None = None,
    funcao: str | None = None,
    grupo_despesa: str | None = None,
    fonte: str | None = None,
    uo: str = Query("24205", description="Unidade Orçamentária (default: AEB 24205)"),
) -> KPIs:
    """Indicadores agregados (cards): dotacao, empenhado, liquidado, pago e %."""
    regs = services.filtrar(ano, programa, acao, funcao, grupo_despesa, fonte, uo)
    return KPIs(**services.kpis(regs))


@app.get(f"{V1}/orcamento/serie-mensal", response_model=list[PontoSerie], tags=["orcamento"])
def serie_mensal(
    ano: int | None = None,
    programa: str | None = None,
    acao: str | None = None,
    funcao: str | None = None,
    grupo_despesa: str | None = None,
    fonte: str | None = None,
    uo: str = Query("24205", description="Unidade Orçamentária (default: AEB 24205)"),
) -> list[PontoSerie]:
    """Execucao por mes (linha): empenhado, liquidado, pago."""
    regs = services.filtrar(ano, programa, acao, funcao, grupo_despesa, fonte, uo)
    return [PontoSerie(**p) for p in services.serie_mensal(regs)]


@app.get(f"{V1}/orcamento/ranking", response_model=list[ItemRanking], tags=["orcamento"])
def ranking(
    por: str = Query("programa", pattern="^(programa|acao|funcao|grupo_despesa|fonte)$"),
    limite: int = Query(10, ge=1, le=50),
    ano: int | None = None,
    programa: str | None = None,
    acao: str | None = None,
    funcao: str | None = None,
    grupo_despesa: str | None = None,
    fonte: str | None = None,
    uo: str = Query("24205", description="Unidade Orçamentária (default: AEB 24205)"),
) -> list[ItemRanking]:
    """Ranking por dimensao (barras): top N por dotacao atual."""
    regs = services.filtrar(ano, programa, acao, funcao, grupo_despesa, fonte, uo)
    return [ItemRanking(**i) for i in services.ranking(regs, por, limite)]


@app.get(f"{V1}/orcamento/registros", response_model=RegistrosPaginados, tags=["orcamento"])
def registros(
    pagina: int = Query(1, ge=1),
    tamanho: int = Query(50, ge=1, le=500),
    ano: int | None = None,
    programa: str | None = None,
    acao: str | None = None,
    funcao: str | None = None,
    grupo_despesa: str | None = None,
    fonte: str | None = None,
    uo: str = Query("24205", description="Unidade Orçamentária (default: AEB 24205)"),
) -> RegistrosPaginados:
    """Registros detalhados (tabela), paginados."""
    regs = services.filtrar(ano, programa, acao, funcao, grupo_despesa, fonte, uo)
    ini = (pagina - 1) * tamanho
    itens = [Registro(**r) for r in regs[ini : ini + tamanho]]
    return RegistrosPaginados(total=len(regs), pagina=pagina, tamanho=tamanho, itens=itens)


# ============================================================================
# Auditoria — Saldos Alongados (SIAFI / Tesouro Gerencial)
# ============================================================================

@app.get(
    f"{V1}/auditoria/saldos-alongados",
    response_model=list[SaldoAlongado],
    tags=["auditoria"],
)
def saldos_alongados(
    meses: int = Query(12, ge=3, le=36, description="Meses de historico a analisar"),
    min_meses: int = Query(3, ge=2, le=12, description="Minimo de meses consecutivos para reportar"),
    ug: str | None = Query(None, description="Filtrar por UG específica (ex: 24205000)"),
) -> list[SaldoAlongado]:
    """Contas contabeis cujo saldo permaneceu inalterado por N meses consecutivos.

    Dados sinteticos no PoC. Em producao, consome:
    - Arquivos exportados do SIAFI / Tesouro Gerencial
    - API Siconfi (MSC Orcamentaria): http://apidatalake.tesouro.gov.br/docs/siconfi/
    - API Portal da Transparencia: portaldatransparencia.gov.br/api-de-dados
    """
    resultados = obter_saldos_alongados_sinteticos(meses=meses, min_meses=min_meses, ug=ug)
    return [
        SaldoAlongado(
            ug=r.ug,
            desc_ug=r.desc_ug,
            contabil=r.contabil,
            desc_contabil=r.desc_contabil,
            corrente=r.corrente,
            meses_alongados=r.meses_alongados,
            saldo_atual=r.saldo_atual,
            mes_referencia=r.mes_referencia.strftime("%Y-%m"),
        )
        for r in resultados
    ]


@app.get(
    f"{V1}/auditoria/saldos-alongados/resumo",
    response_model=AuditoriaResumo,
    tags=["auditoria"],
)
def saldos_alongados_resumo(
    meses: int = Query(12, ge=3, le=36),
    ug: str | None = Query(None, description="Filtrar por UG específica (ex: 24205000)"),
) -> AuditoriaResumo:
    """Resumo agregado da auditoria de saldos alongados."""
    from .auditoria import gerar_dados_sinteticos, calcular_alongamento

    todos = gerar_dados_sinteticos(meses=meses)
    if ug:
        todos = [r for r in todos if r.ug == ug]
    alongados = calcular_alongamento(todos)

    return AuditoriaResumo(
        total_contas=len({(r.ug, r.contabil, r.corrente) for r in todos}),
        total_alongadas=len([a for a in alongados if a.meses_alongados >= 2]),
        maior_alongamento=max((a.meses_alongados for a in alongados), default=0),
        saldo_total_alongado=sum(a.saldo_atual for a in alongados if a.meses_alongados >= 2),
        meses_analisados=meses,
    )


# ============================================================================
# Contratos (COAD/DCONT/DIAP/DIPA/DSG)
# ============================================================================
@app.get(f"{V1}/contratos", response_model=list[Contrato], tags=["contratos"])
def get_contratos(
    status: str | None = None,
    modalidade: str | None = None,
    area: str | None = None,
    fornecedor: str | None = None,
    ano: int | None = None,
) -> list[Contrato]:
    regs = contratos_services.filtrar(status, modalidade, area, fornecedor, ano)
    return [Contrato(**r) for r in regs]


@app.get(f"{V1}/contratos/kpis", response_model=KpiContratos, tags=["contratos"])
def get_contratos_kpis() -> KpiContratos:
    regs = contratos_services.filtrar()
    return KpiContratos(**contratos_services.kpis(regs))


@app.get(f"{V1}/contratos/por-status", tags=["contratos"])
def get_contratos_por_status() -> list[dict]:
    regs = contratos_services.filtrar()
    return contratos_services.por_status(regs)


@app.get(f"{V1}/contratos/por-area", tags=["contratos"])
def get_contratos_por_area() -> list[dict]:
    regs = contratos_services.filtrar()
    return contratos_services.por_area(regs)


# ============================================================================
# RH / Gestão de Pessoas (CGP, DPOA/CGP)
# ============================================================================
@app.get(f"{V1}/rh/servidores", response_model=list[Servidor], tags=["rh"])
def get_servidores(
    cargo: str | None = None,
    lotacao: str | None = None,
    regime: str | None = None,
    situacao: str | None = None,
) -> list[Servidor]:
    regs = rh_services.filtrar_servidores(cargo, lotacao, regime, situacao)
    return [Servidor(**r) for r in regs]


@app.get(f"{V1}/rh/kpis", response_model=KpiRH, tags=["rh"])
def get_rh_kpis() -> KpiRH:
    regs = rh_services.filtrar_servidores()
    return KpiRH(**rh_services.kpis_rh(regs))


@app.get(f"{V1}/rh/por-cargo", tags=["rh"])
def get_rh_por_cargo() -> list[dict]:
    regs = rh_services.filtrar_servidores()
    return rh_services.por_cargo(regs)


@app.get(f"{V1}/rh/por-lotacao", tags=["rh"])
def get_rh_por_lotacao() -> list[dict]:
    regs = rh_services.filtrar_servidores()
    return rh_services.por_lotacao(regs)


@app.get(f"{V1}/rh/forca-trabalho", tags=["rh"])
def get_forca_trabalho() -> list[dict]:
    return rh_services.forca_trabalho()


# ============================================================================
# Comunicação (ARI)
# ============================================================================
@app.get(f"{V1}/comunicacao/materias", response_model=list[Materia], tags=["comunicacao"])
def get_materias(
    veiculo: str | None = None,
    categoria: str | None = None,
    clipping: bool | None = None,
) -> list[Materia]:
    regs = comunicacao_services.materias(veiculo, categoria, clipping)
    return [Materia(**r) for r in regs]


@app.get(f"{V1}/comunicacao/atendimentos", response_model=list[Atendimento], tags=["comunicacao"])
def get_atendimentos() -> list[Atendimento]:
    from .dominios.comunicacao_data import gerar_atendimentos
    return [Atendimento(**r) for r in gerar_atendimentos()]


@app.get(f"{V1}/comunicacao/postagens", response_model=list[Postagem], tags=["comunicacao"])
def get_postagens() -> list[Postagem]:
    from .dominios.comunicacao_data import gerar_postagens
    return [Postagem(**r) for r in gerar_postagens()]


@app.get(f"{V1}/comunicacao/kpis", response_model=KpiComunicacao, tags=["comunicacao"])
def get_comunicacao_kpis() -> KpiComunicacao:
    return KpiComunicacao(**comunicacao_services.kpis_comunicacao())


@app.get(f"{V1}/comunicacao/materias-por-categoria", tags=["comunicacao"])
def get_materias_por_categoria() -> list[dict]:
    return comunicacao_services.materias_por_categoria()


@app.get(f"{V1}/comunicacao/postagens-por-plataforma", tags=["comunicacao"])
def get_postagens_por_plataforma() -> list[dict]:
    return comunicacao_services.postagens_por_plataforma()


# ============================================================================
# Educação (DGSE, DIEN, URRN)
# ============================================================================
@app.get(f"{V1}/educacao/cursos", response_model=list[Curso], tags=["educacao"])
def get_cursos(
    unidade: str | None = None,
    nivel: str | None = None,
    status: str | None = None,
) -> list[Curso]:
    regs = educacao_services.cursos(unidade, nivel, status)
    return [Curso(**r) for r in regs]


@app.get(f"{V1}/educacao/alunos", response_model=list[Aluno], tags=["educacao"])
def get_alunos() -> list[Aluno]:
    from .dominios.educacao_data import gerar_alunos_aeb_escola
    return [Aluno(**r) for r in gerar_alunos_aeb_escola()]


@app.get(f"{V1}/educacao/kpis", response_model=KpiEducacao, tags=["educacao"])
def get_educacao_kpis() -> KpiEducacao:
    return KpiEducacao(**educacao_services.kpis_educacao())


@app.get(f"{V1}/educacao/cursos-por-unidade", tags=["educacao"])
def get_cursos_por_unidade() -> list[dict]:
    return educacao_services.cursos_por_unidade()


# ============================================================================
# Operações Espaciais (DGSE)
# ============================================================================
@app.get(f"{V1}/operacoes/lancamentos", response_model=list[Lancamento], tags=["operacoes"])
def get_lancamentos(
    status: str | None = None,
    foguete: str | None = None,
    base: str | None = None,
) -> list[Lancamento]:
    regs = operacoes_services.lancamentos(status, foguete, base)
    return [Lancamento(**r) for r in regs]


@app.get(f"{V1}/operacoes/satelites", response_model=list[Satelite], tags=["operacoes"])
def get_satelites(
    status: str | None = None,
    aplicacao: str | None = None,
) -> list[Satelite]:
    regs = operacoes_services.satelites(status, aplicacao)
    return [Satelite(**r) for r in regs]


@app.get(f"{V1}/operacoes/kpis", response_model=KpiOperacoes, tags=["operacoes"])
def get_operacoes_kpis() -> KpiOperacoes:
    return KpiOperacoes(**operacoes_services.kpis_operacoes())


# ============================================================================
# Governança (DPOA/Assessoria)
# ============================================================================
@app.get(f"{V1}/governanca/atos", response_model=list[Ato], tags=["governanca"])
def get_atos(
    tipo: str | None = None,
    area: str | None = None,
    status: str | None = None,
) -> list[Ato]:
    regs = governanca_services.atos(tipo, area, status)
    return [Ato(**r) for r in regs]


@app.get(f"{V1}/governanca/integridade", response_model=list[Integridade], tags=["governanca"])
def get_integridade(
    tipo: str | None = None,
    status: str | None = None,
) -> list[Integridade]:
    regs = governanca_services.integridade(tipo, status)
    return [Integridade(**r) for r in regs]


@app.get(f"{V1}/governanca/agendas", response_model=list[Agenda], tags=["governanca"])
def get_agendas(area: str | None = None) -> list[Agenda]:
    regs = governanca_services.agendas(area)
    return [Agenda(**r) for r in regs]


@app.get(f"{V1}/governanca/portais", response_model=list[Portal], tags=["governanca"])
def get_portais() -> list[Portal]:
    return [Portal(**r) for r in governanca_services.portais()]


@app.get(f"{V1}/governanca/kpis", response_model=KpiGovernanca, tags=["governanca"])
def get_governanca_kpis() -> KpiGovernanca:
    return KpiGovernanca(**governanca_services.kpis_governanca())


# ============================================================================
# Eventos (GAB Presidência)
# ============================================================================
@app.get(f"{V1}/eventos", response_model=list[Evento], tags=["eventos"])
def get_eventos(
    tipo: str | None = None,
    status: str | None = None,
    area: str | None = None,
) -> list[Evento]:
    regs = eventos_services.eventos(tipo, status, area)
    return [Evento(**r) for r in regs]


@app.get(f"{V1}/eventos/kpis", response_model=KpiEventos, tags=["eventos"])
def get_eventos_kpis() -> KpiEventos:
    return KpiEventos(**eventos_services.kpis_eventos())


@app.get(f"{V1}/eventos/por-tipo", tags=["eventos"])
def get_eventos_por_tipo() -> list[dict]:
    return eventos_services.eventos_por_tipo()


# ============================================================================
# TransfereGov (URSJC)
# ============================================================================
@app.get(f"{V1}/transferegov/programas", response_model=list[ProgramaTransfere], tags=["transferegov"])
def get_programas_transfere(status: str | None = None) -> list[ProgramaTransfere]:
    regs = transferegov_services.programas(status)
    return [ProgramaTransfere(**r) for r in regs]


@app.get(f"{V1}/transferegov/repasses", response_model=list[Repasse], tags=["transferegov"])
def get_repasses(status: str | None = None) -> list[Repasse]:
    regs = transferegov_services.repasses(status)
    return [Repasse(**r) for r in regs]


@app.get(f"{V1}/transferegov/kpis", response_model=KpiTransfereGov, tags=["transferegov"])
def get_transferegov_kpis() -> KpiTransfereGov:
    return KpiTransfereGov(**transferegov_services.kpis_transferegov())


# ============================================================================
# DOU (AUDIN)
# ============================================================================
@app.get(f"{V1}/dou/publicacoes", response_model=list[PublicacaoDOU], tags=["dou"])
def get_publicacoes_dou(
    secao: str | None = None,
    tipo: str | None = None,
    orgao: str | None = None,
    referencia_aeb: bool | None = None,
) -> list[PublicacaoDOU]:
    regs = dou_services.publicacoes(secao, tipo, orgao, referencia_aeb)
    return [PublicacaoDOU(**r) for r in regs]


@app.get(f"{V1}/dou/kpis", tags=["dou"])
def get_dou_kpis() -> dict:
    return dou_services.kpis_dou()


# ============================================================================
# Acordos Internacionais (ACI)
# ============================================================================
@app.get(f"{V1}/acordos", response_model=list[Acordo], tags=["acordos"])
def get_acordos(
    tipo: str | None = None,
    pais: str | None = None,
    status: str | None = None,
    area: str | None = None,
) -> list[Acordo]:
    regs = acordo_services.acordos(tipo, pais, status, area)
    return [Acordo(**r) for r in regs]


@app.get(f"{V1}/acordos/kpis", response_model=KpiAcordos, tags=["acordos"])
def get_acordos_kpis() -> KpiAcordos:
    return KpiAcordos(**acordo_services.kpis_acordos())


@app.get(f"{V1}/acordos/por-pais", tags=["acordos"])
def get_acordos_por_pais() -> list[dict]:
    return acordo_services.acordos_por_pais()


# ============================================================================
# DGEP / Planejamento Estratégico
# ============================================================================
@app.get(f"{V1}/dgep/pde", response_model=list[MetaPDE], tags=["dgep"])
def get_pde(
    eixo: str | None = None,
    status: str | None = None,
) -> list[MetaPDE]:
    regs = dgep_services.pde(eixo, status)
    return [MetaPDE(**r) for r in regs]


@app.get(f"{V1}/dgep/kpis", response_model=KpiDGEP, tags=["dgep"])
def get_dgep_kpis() -> KpiDGEP:
    return KpiDGEP(**dgep_services.kpis_dgep())


@app.get(f"{V1}/dgep/metas-por-eixo", tags=["dgep"])
def get_metas_por_eixo() -> list[dict]:
    return dgep_services.metas_por_eixo()
