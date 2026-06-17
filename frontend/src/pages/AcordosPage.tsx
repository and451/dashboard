import { useEffect, useState } from "react";
import { api, Acordo, KpiAcordos } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return <div className="kpi" style={{ borderTopColor: cor }}><span className="kpi-titulo">{titulo}</span><span className="kpi-valor">{valor}</span></div>;
}

export default function AcordosPage() {
  const [kpis, setKpis] = useState<KpiAcordos | null>(null);
  const [acordos, setAcordos] = useState<Acordo[]>([]);
  const [porPais, setPorPais] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    Promise.all([api.acordosKpis(), api.acordos(), api.acordosPorPais()])
      .then(([k, a, pp]) => { setKpis(k); setAcordos(a); setPorPais(pp); });
  }, []);

  const optPais: EChartsOption = {
    xAxis: { type: "category", data: porPais.map((p) => p.pais) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: porPais.map((p) => p.quantidade), color: "#1351b4" }],
  };

  return (
    <div className="app">
      <header className="topo"><div><h1>Acordos Internacionais</h1><p className="subtitulo">Cooperação internacional e parcerias espaciais (ACI)</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Total Acordos" valor={String(kpis.total_acordos)} cor="#5e5e5e" />
          <KpiCard titulo="Vigentes" valor={String(kpis.vigentes)} cor="#2e7d32" />
          <KpiCard titulo="Projetos" valor={String(kpis.projetos_vinculados)} cor="#f29900" />
          <KpiCard titulo="Valor Previsto" valor={(kpis.valor_total_previsto / 1e6).toFixed(0) + "M"} cor="#1351b4" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Por País</h2><EChart option={optPais} height={280} /></div>
        <div className="card grande">
          <h2>Acordos</h2>
          <table className="tabela"><thead><tr><th>Tipo</th><th>País</th><th>Área</th><th>Instituição</th><th>Assinatura</th><th>Status</th><th>Projetos</th></tr></thead>
            <tbody>{acordos.map((a) => (<tr key={a.id}><td>{a.tipo}</td><td>{a.pais}</td><td>{a.area}</td><td>{a.instituicao_parceira}</td><td>{a.dt_assinatura}</td><td>{a.status}</td><td>{a.projetos_vinculados}</td></tr>))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
