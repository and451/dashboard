import { useEffect, useState } from "react";
import { api, Evento, KpiEventos } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return <div className="kpi" style={{ borderTopColor: cor }}><span className="kpi-titulo">{titulo}</span><span className="kpi-valor">{valor}</span></div>;
}

function brl(v: number): string {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

export default function EventosPage() {
  const [kpis, setKpis] = useState<KpiEventos | null>(null);
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [porTipo, setPorTipo] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    Promise.all([api.eventosKpis(), api.eventos(), api.eventosPorTipo()])
      .then(([k, e, pt]) => { setKpis(k); setEventos(e); setPorTipo(pt); });
  }, []);

  const optTipo: EChartsOption = {
    series: [{ type: "pie", radius: ["30%", "60%"], data: porTipo.map((t) => ({ value: t.quantidade, name: t.tipo })) }],
  };

  return (
    <div className="app">
      <header className="topo"><div><h1>Eventos — GAB Presidência</h1><p className="subtitulo">Panorama de eventos, cerimônias e audiências</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Total Eventos" valor={String(kpis.total_eventos)} cor="#5e5e5e" />
          <KpiCard titulo="Realizados" valor={String(kpis.realizados)} cor="#2e7d32" />
          <KpiCard titulo="Participantes" valor={String(kpis.participantes_total)} cor="#f29900" />
          <KpiCard titulo="Custo Total" valor={brl(kpis.custo_total)} cor="#1351b4" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Por Tipo</h2><EChart option={optTipo} height={260} /></div>
        <div className="card grande">
          <h2>Eventos</h2>
          <table className="tabela"><thead><tr><th>Título</th><th>Tipo</th><th>Data</th><th>Local</th><th>Público</th><th>Part.</th><th>Custo</th><th>Status</th></tr></thead>
            <tbody>{eventos.map((e) => (<tr key={e.id}><td>{e.titulo}</td><td>{e.tipo}</td><td>{e.data}</td><td>{e.local}</td><td>{e.publico}</td><td>{e.participantes}</td><td>{brl(e.custo)}</td><td>{e.status}</td></tr>))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
