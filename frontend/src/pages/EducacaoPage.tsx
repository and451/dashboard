import { useEffect, useState } from "react";
import { api, Curso, KpiEducacao } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return <div className="kpi" style={{ borderTopColor: cor }}><span className="kpi-titulo">{titulo}</span><span className="kpi-valor">{valor}</span></div>;
}

export default function EducacaoPage() {
  const [kpis, setKpis] = useState<KpiEducacao | null>(null);
  const [cursos, setCursos] = useState<Curso[]>([]);
  const [porUnidade, setPorUnidade] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    Promise.all([api.educacaoKpis(), api.cursos(), api.cursosPorUnidade()])
      .then(([k, c, pu]) => { setKpis(k); setCursos(c); setPorUnidade(pu); });
  }, []);

  const optUnid: EChartsOption = {
    xAxis: { type: "category", data: porUnidade.map((u) => u.unidade) },
    yAxis: { type: "value" },
    series: [
      { name: "Cursos", type: "bar", data: porUnidade.map((u) => u.cursos), color: "#1351b4" },
      { name: "Concluintes", type: "bar", data: porUnidade.map((u) => u.concluintes), color: "#2e7d32" },
    ],
  };

  return (
    <div className="app">
      <header className="topo"><div><h1>Educação — AEB Escola</h1><p className="subtitulo">Cursos, capacitações e monitoramento educacional (DGSE / DIEN / URRN)</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Cursos" valor={String(kpis.total_cursos)} cor="#5e5e5e" />
          <KpiCard titulo="Vagas" valor={String(kpis.total_vagas)} cor="#1351b4" />
          <KpiCard titulo="Inscritos" valor={String(kpis.total_inscritos)} cor="#f29900" />
          <KpiCard titulo="Concluintes" valor={String(kpis.total_concluintes)} cor="#2e7d32" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Cursos por Unidade</h2><EChart option={optUnid} height={280} /></div>
        <div className="card grande">
          <h2>Cursos</h2>
          <table className="tabela"><thead><tr><th>Nome</th><th>Unidade</th><th>Nível</th><th>Vagas</th><th>Inscritos</th><th>Concluintes</th><th>Taxa</th><th>Status</th></tr></thead>
            <tbody>{cursos.map((c) => (
              <tr key={c.id}><td>{c.nome.slice(0, 45)}</td><td>{c.unidade}</td><td>{c.nivel}</td><td>{c.vagas}</td><td>{c.inscritos}</td><td>{c.concluintes}</td><td>{c.taxa_conclusao}%</td><td>{c.status}</td></tr>
            ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
