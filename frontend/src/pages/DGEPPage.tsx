import { useEffect, useState } from "react";
import { api, MetaPDE, KpiDGEP } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return <div className="kpi" style={{ borderTopColor: cor }}><span className="kpi-titulo">{titulo}</span><span className="kpi-valor">{valor}</span></div>;
}

export default function DGEPPage() {
  const [kpis, setKpis] = useState<KpiDGEP | null>(null);
  const [metas, setMetas] = useState<MetaPDE[]>([]);
  const [porEixo, setPorEixo] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    Promise.all([api.dgepKpis(), api.pde(), api.metasPorEixo()])
      .then(([k, m, pe]) => { setKpis(k); setMetas(m); setPorEixo(pe); });
  }, []);

  const optEixo: EChartsOption = {
    xAxis: { type: "category", data: porEixo.map((e) => e.eixo.slice(0, 20)) },
    yAxis: { type: "value" },
    series: [
      { name: "Total", type: "bar", data: porEixo.map((e) => e.total), color: "#5e5e5e" },
      { name: "Concluídas", type: "bar", data: porEixo.map((e) => e.concluidas), color: "#2e7d32" },
    ],
  };

  return (
    <div className="app">
      <header className="topo"><div><h1>Planejamento Estratégico — DGEP</h1><p className="subtitulo">PDE: metas, indicadores e acompanhamento estratégico</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Total Metas" valor={String(kpis.total_metas)} cor="#5e5e5e" />
          <KpiCard titulo="Concluídas" valor={String(kpis.concluidas)} cor="#2e7d32" />
          <KpiCard titulo="% Conclusão" valor={kpis.pct_conclusao + "%"} cor="#f29900" />
          <KpiCard titulo="Atrasadas" valor={String(kpis.atrasadas)} cor="#c62828" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Metas por Eixo</h2><EChart option={optEixo} height={280} /></div>
        <div className="card grande">
          <h2>Metas do PDE</h2>
          <table className="tabela"><thead><tr><th>Eixo</th><th>Meta</th><th>Indicador</th><th>Ano</th><th>Previsto</th><th>Realizado</th><th>Status</th><th>Resp.</th></tr></thead>
            <tbody>{metas.map((m) => (<tr key={m.meta}><td>{m.eixo.slice(0, 20)}</td><td>{m.meta.slice(0, 35)}</td><td>{m.indicador.slice(0, 30)}</td><td>{m.meta_ano}</td><td>{m.valor_previsto}</td><td>{m.valor_realizado}</td><td>{m.status}</td><td>{m.responsavel}</td></tr>))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
