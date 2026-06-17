import { useEffect, useState } from "react";
import { api, Contrato, KpiContratos } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function brl(v: number): string {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return (
    <div className="kpi" style={{ borderTopColor: cor }}>
      <span className="kpi-titulo">{titulo}</span>
      <span className="kpi-valor">{valor}</span>
    </div>
  );
}

export default function ContratosPage() {
  const [kpis, setKpis] = useState<KpiContratos | null>(null);
  const [contratos, setContratos] = useState<Contrato[]>([]);
  const [porStatus, setPorStatus] = useState<Record<string, any>[]>([]);
  const [porArea, setPorArea] = useState<Record<string, any>[]>([]);
  const [filtroStatus, setFiltroStatus] = useState("");
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    setCarregando(true);
    Promise.all([
      api.contratosKpis(),
      api.contratos(filtroStatus ? { status: filtroStatus } : undefined),
      api.contratosPorStatus(),
      api.contratosPorArea(),
    ])
      .then(([k, c, ps, pa]) => {
        setKpis(k);
        setContratos(c);
        setPorStatus(ps);
        setPorArea(pa);
      })
      .finally(() => setCarregando(false));
  }, [filtroStatus]);

  const optStatus: EChartsOption = {
    tooltip: { trigger: "item", valueFormatter: (v: any) => brl(Number(v)) },
    series: [{
      type: "pie", radius: ["40%", "70%"],
      data: porStatus.map((s) => ({ value: s.quantidade, name: s.status })),
    }],
  };

  const optArea: EChartsOption = {
    tooltip: { trigger: "axis", valueFormatter: (v: any) => brl(Number(v)) },
    xAxis: { type: "category", data: porArea.map((a) => a.area) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: porArea.map((a) => a.valor), color: "#1351b4" }],
  };

  return (
    <div className="app">
      <header className="topo">
        <div>
          <h1>Contratos e Aquisições</h1>
          <p className="subtitulo">Painel de contratos da AEB (COAD/DCONT/DIAP/DIPA/DSG)</p>
        </div>
      </header>
      <section className="filtros">
        <label>Status <select value={filtroStatus} onChange={(e) => setFiltroStatus(e.target.value)}><option value="">Todos</option><option>Em execução</option><option>Concluído</option><option>Rescisão</option></select></label>
      </section>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Total Contratos" valor={String(kpis.total_contratos)} cor="#5e5e5e" />
          <KpiCard titulo="Valor Total" valor={brl(kpis.valor_total)} cor="#1351b4" />
          <KpiCard titulo="Em Execução" valor={String(kpis.em_execucao)} cor="#f29900" />
          <KpiCard titulo="Saldo a Executar" valor={brl(kpis.saldo_executar)} cor="#c62828" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Por Status</h2><EChart option={optStatus} height={280} /></div>
        <div className="card"><h2>Por Área (R$)</h2><EChart option={optArea} height={280} /></div>
        <div className="card grande">
          <h2>Contratos</h2>
          <table className="tabela"><thead><tr><th>Nº</th><th>Fornecedor</th><th>Objeto</th><th>Área</th><th>Valor</th><th>% Exec</th><th>Status</th></tr></thead>
            <tbody>{contratos.slice(0, 15).map((c) => (
              <tr key={c.id}><td>{c.numero}</td><td>{c.fornecedor}</td><td>{c.objeto.slice(0, 40)}</td><td>{c.area}</td><td>{brl(c.valor_atual)}</td><td>{c.pct_execucao}%</td><td>{c.status}</td></tr>
            ))}</tbody>
          </table>
        </div>
      </section>
      <footer className="rodape">{carregando ? "Atualizando..." : `Contratos: ${contratos.length}`}</footer>
    </div>
  );
}
