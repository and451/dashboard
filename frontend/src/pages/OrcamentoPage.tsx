import { useEffect, useMemo, useState } from "react";
import type { EChartsOption } from "echarts";
import { api, Dimensoes, Filtros, ItemRanking, KPIs, PontoSerie } from "../api";
import EChart from "../components/EChart";

const MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

function brl(v: number): string {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

function KpiCard({ titulo, valor, sub, cor }: { titulo: string; valor: string; sub?: string; cor: string }) {
  return (
    <div className="kpi" style={{ borderTopColor: cor }}>
      <span className="kpi-titulo">{titulo}</span>
      <span className="kpi-valor">{valor}</span>
      {sub && <span className="kpi-sub">{sub}</span>}
    </div>
  );
}

export default function OrcamentoPage() {
  const [dim, setDim] = useState<Dimensoes | null>(null);
  const [filtros, setFiltros] = useState<Filtros>({});
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [serie, setSerie] = useState<PontoSerie[]>([]);
  const [rankProg, setRankProg] = useState<ItemRanking[]>([]);
  const [rankAcao, setRankAcao] = useState<ItemRanking[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    api.dimensoes().then(setDim).catch((e) => setErro(String(e)));
  }, []);

  useEffect(() => {
    setCarregando(true);
    Promise.all([
      api.kpis(filtros),
      api.serie(filtros),
      api.ranking(filtros, "programa"),
      api.ranking(filtros, "acao"),
    ])
      .then(([k, s, rp, ra]) => {
        setKpis(k);
        setSerie(s);
        setRankProg(rp);
        setRankAcao(ra);
        setErro(null);
      })
      .catch((e) => setErro(String(e)))
      .finally(() => setCarregando(false));
  }, [filtros]);

  const setF = (campo: keyof Filtros, valor: string) =>
    setFiltros((f) => ({ ...f, [campo]: valor === "" ? undefined : campo === "ano" ? Number(valor) : valor }));

  const optSerie = useMemo<EChartsOption>(
    () => ({
      tooltip: { trigger: "axis", valueFormatter: (v) => brl(Number(v)) },
      legend: { data: ["Empenhado", "Liquidado", "Pago"], bottom: 0 },
      grid: { left: 70, right: 20, top: 20, bottom: 50 },
      xAxis: { type: "category", data: serie.map((p) => MESES[p.mes - 1]) },
      yAxis: { type: "value", axisLabel: { formatter: (v: number) => `${(v / 1e6).toFixed(0)} M` } },
      series: [
        { name: "Empenhado", type: "line", smooth: true, data: serie.map((p) => p.empenhado), color: "#1351b4" },
        { name: "Liquidado", type: "line", smooth: true, data: serie.map((p) => p.liquidado), color: "#168821" },
        { name: "Pago", type: "line", smooth: true, data: serie.map((p) => p.pago), color: "#f29900" },
      ],
    }),
    [serie]
  );

  const optRank = (itens: ItemRanking[], cor: string): EChartsOption => ({
    tooltip: { trigger: "axis", valueFormatter: (v) => brl(Number(v)) },
    grid: { left: 220, right: 30, top: 10, bottom: 20 },
    xAxis: { type: "value", axisLabel: { formatter: (v: number) => `${(v / 1e6).toFixed(0)} M` } },
    yAxis: {
      type: "category",
      data: itens.map((i) => i.rotulo).reverse(),
      axisLabel: { width: 200, overflow: "truncate" },
    },
    series: [{ type: "bar", data: itens.map((i) => i.dotacao_atual).reverse(), color: cor }],
  });

  return (
    <div className="app">
      <header className="topo">
        <div>
          <h1>Painel de Execução Orçamentária</h1>
          <p className="subtitulo">
            Agência Espacial Brasileira (UO 24205) — Prova de Conceito · fonte: DaaS SERPRO / SIAFI (dados sintéticos)
          </p>
        </div>
      </header>

      {erro && <div className="erro">Falha ao consultar a API: {erro}. O backend está rodando em :8000?</div>}

      <section className="filtros" aria-label="Filtros">
        <label>
          Ano
          <select value={filtros.ano ?? ""} onChange={(e) => setF("ano", e.target.value)}>
            <option value="">Todos</option>
            {dim?.anos.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </label>
        <label>
          Programa
          <select value={filtros.programa ?? ""} onChange={(e) => setF("programa", e.target.value)}>
            <option value="">Todos</option>
            {dim?.programas.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </label>
        <label>
          Grupo de Despesa
          <select value={filtros.grupo_despesa ?? ""} onChange={(e) => setF("grupo_despesa", e.target.value)}>
            <option value="">Todos</option>
            {dim?.grupos_despesa.map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </label>
        <label>
          Fonte
          <select value={filtros.fonte ?? ""} onChange={(e) => setF("fonte", e.target.value)}>
            <option value="">Todas</option>
            {dim?.fontes.map((f) => (
              <option key={f} value={f}>{f}</option>
            ))}
          </select>
        </label>
        <button className="limpar" onClick={() => setFiltros({})}>Limpar</button>
      </section>

      <section className="kpis">
        <KpiCard titulo="Dotação Atual" valor={kpis ? brl(kpis.dotacao_atual) : "—"} cor="#5e5e5e" />
        <KpiCard titulo="Empenhado" valor={kpis ? brl(kpis.empenhado) : "—"} sub={kpis ? `${kpis.pct_empenhado}% da dotação` : ""} cor="#1351b4" />
        <KpiCard titulo="Liquidado" valor={kpis ? brl(kpis.liquidado) : "—"} sub={kpis ? `${kpis.pct_liquidado}% da dotação` : ""} cor="#168821" />
        <KpiCard titulo="Pago" valor={kpis ? brl(kpis.pago) : "—"} sub={kpis ? `${kpis.pct_pago}% da dotação` : ""} cor="#f29900" />
      </section>

      <section className="grid">
        <div className="card grande">
          <h2>Execução mensal</h2>
          <EChart option={optSerie} />
        </div>
        <div className="card">
          <h2>Dotação por Programa</h2>
          <EChart option={optRank(rankProg, "#1351b4")} height={280} />
        </div>
        <div className="card">
          <h2>Dotação por Ação</h2>
          <EChart option={optRank(rankAcao, "#168821")} height={280} />
        </div>
      </section>

      <footer className="rodape">
        {carregando ? "Atualizando..." : `Registros no filtro atual: ${kpis?.registros ?? 0}`}
        {" · "}API: <a href="/api/v1/orcamento/kpis" target="_blank" rel="noreferrer">/api/v1/orcamento</a>
        {" · "}Docs: <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">Swagger</a>
      </footer>
    </div>
  );
}
