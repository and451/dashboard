import { useEffect, useState } from "react";
import { api, Materia, Postagem, KpiComunicacao } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return <div className="kpi" style={{ borderTopColor: cor }}><span className="kpi-titulo">{titulo}</span><span className="kpi-valor">{valor}</span></div>;
}

export default function ComunicacaoPage() {
  const [kpis, setKpis] = useState<KpiComunicacao | null>(null);
  const [materias, setMaterias] = useState<Materia[]>([]);
  const [postagens, setPostagens] = useState<Postagem[]>([]);
  const [porCategoria, setPorCategoria] = useState<Record<string, any>[]>([]);
  const [porPlataforma, setPorPlataforma] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    Promise.all([api.comunicacaoKpis(), api.materias(), api.postagens(), api.materiasPorCategoria(), api.postagensPorPlataforma()])
      .then(([k, m, p, pc, pp]) => { setKpis(k); setMaterias(m); setPostagens(p); setPorCategoria(pc); setPorPlataforma(pp); });
  }, []);

  const optCat: EChartsOption = { series: [{ type: "pie", radius: "60%", data: porCategoria.map((c) => ({ value: c.quantidade, name: c.categoria })) }] };
  const optPlat: EChartsOption = { xAxis: { type: "category", data: porPlataforma.map((p) => p.plataforma) }, yAxis: { type: "value" }, series: [{ type: "bar", data: porPlataforma.map((p) => p.alcance), color: "#1351b4" }] };

  return (
    <div className="app">
      <header className="topo"><div><h1>Comunicação — ARI</h1><p className="subtitulo">Matérias, atendimentos à imprensa e postagens em redes sociais</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Matérias" valor={String(kpis.total_materias)} cor="#5e5e5e" />
          <KpiCard titulo="Clipping" valor={String(kpis.materias_clipping)} cor="#2e7d32" />
          <KpiCard titulo="Postagens" valor={String(kpis.total_postagens)} cor="#f29900" />
          <KpiCard titulo="Alcance" valor={(kpis.alcance_total / 1e6).toFixed(1) + "M"} cor="#1351b4" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Matérias por Categoria</h2><EChart option={optCat} height={260} /></div>
        <div className="card"><h2>Alcance por Plataforma</h2><EChart option={optPlat} height={260} /></div>
        <div className="card"><h2>Matérias Recentes</h2>
          <table className="tabela"><thead><tr><th>Data</th><th>Título</th><th>Veículo</th><th>Categoria</th><th>Repercussão</th></tr></thead>
            <tbody>{materias.slice(0, 10).map((m) => (<tr key={m.id}><td>{m.data}</td><td>{m.titulo.slice(0, 40)}</td><td>{m.veiculo}</td><td>{m.categoria}</td><td>{m.repercussao.toLocaleString("pt-BR")}</td></tr>))}</tbody>
          </table>
        </div>
        <div className="card"><h2>Postagens</h2>
          <table className="tabela"><thead><tr><th>Plataforma</th><th>Conteúdo</th><th>Alcance</th><th>Engajamento</th></tr></thead>
            <tbody>{postagens.slice(0, 10).map((p) => (<tr key={p.id}><td>{p.plataforma}</td><td>{p.conteudo}</td><td>{p.alcance.toLocaleString("pt-BR")}</td><td>{p.engajamento.toLocaleString("pt-BR")}</td></tr>))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
