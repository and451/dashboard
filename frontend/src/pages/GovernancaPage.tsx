import { useEffect, useState } from "react";
import { api, Ato, Integridade, Agenda, KpiGovernanca } from "../api";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return <div className="kpi" style={{ borderTopColor: cor }}><span className="kpi-titulo">{titulo}</span><span className="kpi-valor">{valor}</span></div>;
}

export default function GovernancaPage() {
  const [kpis, setKpis] = useState<KpiGovernanca | null>(null);
  const [atos, setAtos] = useState<Ato[]>([]);
  const [integridade, setIntegridade] = useState<Integridade[]>([]);
  const [agendas, setAgendas] = useState<Agenda[]>([]);

  useEffect(() => {
    Promise.all([api.governancaKpis(), api.atos(), api.integridade(), api.agendas()])
      .then(([k, a, i, ag]) => { setKpis(k); setAtos(a); setIntegridade(i); setAgendas(ag); });
  }, []);

  return (
    <div className="app">
      <header className="topo"><div><h1>Governança e Integridade</h1><p className="subtitulo">Atos normativos, integridade, agendas e portais (DPOA/Assessoria)</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Atos Normativos" valor={String(kpis.total_atos)} cor="#5e5e5e" />
          <KpiCard titulo="Vigentes" valor={String(kpis.atos_vigentes)} cor="#2e7d32" />
          <KpiCard titulo="Integridade" valor={String(kpis.total_integridade)} cor="#f29900" />
          <KpiCard titulo="Pendências" valor={String(kpis.pendencias_integridade)} cor="#c62828" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Atos Normativos Recentes</h2>
          <table className="tabela"><thead><tr><th>Número</th><th>Tipo</th><th>Área</th><th>Data</th><th>Status</th></tr></thead>
            <tbody>{atos.slice(0, 10).map((a) => (<tr key={a.id}><td>{a.numero}</td><td>{a.tipo}</td><td>{a.area}</td><td>{a.dt_publicacao}</td><td>{a.status}</td></tr>))}</tbody>
          </table>
        </div>
        <div className="card"><h2>Integridade</h2>
          <table className="tabela"><thead><tr><th>ID</th><th>Tipo</th><th>Área</th><th>Status</th><th>Dias Aberto</th></tr></thead>
            <tbody>{integridade.slice(0, 10).map((i) => (<tr key={i.id}><td>{i.id}</td><td>{i.tipo}</td><td>{i.area}</td><td>{i.status}</td><td>{i.dias_aberto}</td></tr>))}</tbody>
          </table>
        </div>
        <div className="card"><h2>Agendas</h2>
          <table className="tabela"><thead><tr><th>Título</th><th>Data</th><th>Hora</th><th>Local</th><th>Participantes</th><th>Tipo</th></tr></thead>
            <tbody>{agendas.slice(0, 10).map((a) => (<tr key={a.id}><td>{a.titulo}</td><td>{a.data}</td><td>{a.hora}</td><td>{a.local}</td><td>{a.participantes}</td><td>{a.tipo}</td></tr>))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
