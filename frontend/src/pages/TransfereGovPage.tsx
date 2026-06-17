import { useEffect, useState } from "react";
import { api, ProgramaTransfere, Repasse, KpiTransfereGov } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return <div className="kpi" style={{ borderTopColor: cor }}><span className="kpi-titulo">{titulo}</span><span className="kpi-valor">{valor}</span></div>;
}

function brl(v: number): string {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

export default function TransfereGovPage() {
  const [kpis, setKpis] = useState<KpiTransfereGov | null>(null);
  const [programas, setProgramas] = useState<ProgramaTransfere[]>([]);
  const [repasses, setRepasses] = useState<Repasse[]>([]);

  useEffect(() => {
    Promise.all([api.transferegovKpis(), api.programasTransfere(), api.repasses()])
      .then(([k, p, r]) => { setKpis(k); setProgramas(p); setRepasses(r); });
  }, []);

  const optProg: EChartsOption = {
    tooltip: { trigger: "axis", valueFormatter: (v: any) => brl(Number(v)) },
    xAxis: { type: "category", data: programas.map((p) => p.programa.slice(0, 25)) },
    yAxis: { type: "value" },
    series: [
      { name: "Total", type: "bar", data: programas.map((p) => p.valor_total), color: "#1351b4" },
      { name: "Executado", type: "bar", data: programas.map((p) => p.valor_executado), color: "#2e7d32" },
    ],
  };

  return (
    <div className="app">
      <header className="topo"><div><h1>TransfereGov — Programas e Repasses</h1><p className="subtitulo">Acompanhamento de transferências voluntárias (URSJC)</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Programas" valor={String(kpis.total_programas)} cor="#5e5e5e" />
          <KpiCard titulo="Programado" valor={brl(kpis.valor_total_programado)} cor="#1351b4" />
          <KpiCard titulo="Executado" valor={brl(kpis.valor_total_executado)} cor="#2e7d32" />
          <KpiCard titulo="Repasses" valor={String(kpis.repasses_efetivados)} cor="#f29900" />
        </section>
      )}
      <section className="grid">
        <div className="card grande"><h2>Programas</h2><EChart option={optProg} height={320} /></div>
        <div className="card"><h2>Repasses Recentes</h2>
          <table className="tabela"><thead><tr><th>Programa</th><th>Repasse</th><th>Valor</th><th>Data</th><th>Status</th></tr></thead>
            <tbody>{repasses.slice(0, 10).map((r) => (<tr key={r.id}><td>{r.programa.slice(0, 30)}</td><td>{r.repasse}</td><td>{brl(r.valor)}</td><td>{r.data}</td><td>{r.status}</td></tr>))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
