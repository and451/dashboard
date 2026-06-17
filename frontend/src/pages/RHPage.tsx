import { useEffect, useState } from "react";
import { api, Servidor, KpiRH } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return (
    <div className="kpi" style={{ borderTopColor: cor }}>
      <span className="kpi-titulo">{titulo}</span>
      <span className="kpi-valor">{valor}</span>
    </div>
  );
}

export default function RHPage() {
  const [kpis, setKpis] = useState<KpiRH | null>(null);
  const [servidores, setServidores] = useState<Servidor[]>([]);
  const [porCargo, setPorCargo] = useState<Record<string, any>[]>([]);
  const [porLotacao, setPorLotacao] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    Promise.all([api.rhKpis(), api.servidores(), api.rhPorCargo(), api.rhPorLotacao()])
      .then(([k, s, pc, pl]) => { setKpis(k); setServidores(s); setPorCargo(pc); setPorLotacao(pl); });
  }, []);

  const optCargo: EChartsOption = {
    xAxis: { type: "category", data: porCargo.map((c) => c.cargo) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: porCargo.map((c) => c.quantidade), color: "#1351b4" }],
  };

  const optLotacao: EChartsOption = {
    xAxis: { type: "category", data: porLotacao.map((l) => l.lotacao) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: porLotacao.map((l) => l.quantidade), color: "#2e7d32" }],
  };

  return (
    <div className="app">
      <header className="topo"><div><h1>RH — Gestão de Pessoas</h1><p className="subtitulo">Painel de servidores, força de trabalho e PGD (CGP / DPOA-CGP)</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Total Servidores" valor={String(kpis.total_servidores)} cor="#5e5e5e" />
          <KpiCard titulo="Ativos" valor={String(kpis.ativos)} cor="#2e7d32" />
          <KpiCard titulo="PGD" valor={String(kpis.participantes_pgd)} cor="#f29900" />
          <KpiCard titulo="Média Salarial" valor={kpis.media_salarial.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })} cor="#1351b4" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Por Cargo</h2><EChart option={optCargo} height={280} /></div>
        <div className="card"><h2>Por Lotação</h2><EChart option={optLotacao} height={280} /></div>
        <div className="card grande">
          <h2>Servidores</h2>
          <table className="tabela"><thead><tr><th>Matrícula</th><th>Nome</th><th>Cargo</th><th>Lotação</th><th>Regime</th><th>Salário</th><th>PGD</th></tr></thead>
            <tbody>{servidores.slice(0, 20).map((s) => (
              <tr key={s.matricula}><td>{s.matricula}</td><td>{s.nome}</td><td>{s.cargo}</td><td>{s.lotacao}</td><td>{s.regime}</td>
                <td>{s.salario.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</td>
                <td>{s.pgd_participante ? "Sim" : "Não"}</td></tr>
            ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
