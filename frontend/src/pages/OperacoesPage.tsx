import { useEffect, useState } from "react";
import { api, Lancamento, Satelite, KpiOperacoes } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return <div className="kpi" style={{ borderTopColor: cor }}><span className="kpi-titulo">{titulo}</span><span className="kpi-valor">{valor}</span></div>;
}

function brl(v: number): string {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

export default function OperacoesPage() {
  const [kpis, setKpis] = useState<KpiOperacoes | null>(null);
  const [lancamentos, setLancamentos] = useState<Lancamento[]>([]);
  const [satelites, setSatelites] = useState<Satelite[]>([]);

  useEffect(() => {
    Promise.all([api.operacoesKpis(), api.lancamentos(), api.satelites()])
      .then(([k, l, s]) => { setKpis(k); setLancamentos(l); setSatelites(s); });
  }, []);

  const optStatus: EChartsOption = {
    series: [{ type: "pie", radius: "60%", data: [...new Set(lancamentos.map((l) => l.status))].map((st) => ({ value: lancamentos.filter((l) => l.status === st).length, name: st })) }],
  };

  return (
    <div className="app">
      <header className="topo"><div><h1>Operações Espaciais</h1><p className="subtitulo">Lançamentos, satélites e missões (DGSE)</p></div></header>
      {kpis && (
        <section className="kpis">
          <KpiCard titulo="Lançamentos" valor={String(kpis.total_lancamentos)} cor="#5e5e5e" />
          <KpiCard titulo="Concluídos" valor={String(kpis.concluidos)} cor="#2e7d32" />
          <KpiCard titulo="Taxa Sucesso" valor={kpis.taxa_sucesso + "%"} cor="#f29900" />
          <KpiCard titulo="Investimento" valor={brl(kpis.investimento_satelites)} cor="#1351b4" />
        </section>
      )}
      <section className="grid">
        <div className="card"><h2>Lançamentos por Status</h2><EChart option={optStatus} height={260} /></div>
        <div className="card grande">
          <h2>Lançamentos</h2>
          <table className="tabela"><thead><tr><th>Missão</th><th>Foguete</th><th>Base</th><th>Data Prev.</th><th>Carga</th><th>Custo</th><th>Status</th></tr></thead>
            <tbody>{lancamentos.map((l) => (
              <tr key={l.id}><td>{l.nome}</td><td>{l.foguete}</td><td>{l.base}</td><td>{l.data_prevista}</td><td>{l.carga}</td><td>{brl(l.custo_missao)}</td><td>{l.status}</td></tr>
            ))}</tbody>
          </table>
        </div>
        <div className="card grande">
          <h2>Satélites</h2>
          <table className="tabela"><thead><tr><th>Nome</th><th>Aplicação</th><th>Status</th><th>Lançamento</th><th>Operador</th><th>Vida útil</th><th>Massa (kg)</th></tr></thead>
            <tbody>{satelites.map((s) => (
              <tr key={s.nome}><td>{s.nome}</td><td>{s.aplicacao}</td><td>{s.status}</td><td>{s.dt_lancamento}</td><td>{s.operador}</td><td>{s.vida_util_anos} anos</td><td>{s.massa_kg}</td></tr>
            ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
