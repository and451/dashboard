import { useEffect, useState } from "react";
import { api, PublicacaoDOU } from "../api";

export default function DouPage() {
  const [publicacoes, setPublicacoes] = useState<PublicacaoDOU[]>([]);
  const [kpis, setKpis] = useState<Record<string, any> | null>(null);

  useEffect(() => {
    Promise.all([api.publicacoesDOU(), api.douKpis()]).then(([p, k]) => { setPublicacoes(p); setKpis(k); });
  }, []);

  return (
    <div className="app">
      <header className="topo"><div><h1>Publicações no DOU</h1><p className="subtitulo">Monitoramento de publicações no Diário Oficial da União (AUDIN)</p></div></header>
      {kpis && (
        <section className="kpis">
          <div className="kpi" style={{ borderTopColor: "#5e5e5e" }}><span className="kpi-titulo">Total Publicações</span><span className="kpi-valor">{kpis.total_publicacoes}</span></div>
          <div className="kpi" style={{ borderTopColor: "#1351b4" }}><span className="kpi-titulo">Referentes AEB</span><span className="kpi-valor">{kpis.referentes_aeb}</span></div>
        </section>
      )}
      <section className="grid">
        <div className="card grande">
          <h2>Publicações</h2>
          <table className="tabela"><thead><tr><th>Data</th><th>Seção</th><th>Tipo</th><th>Órgão</th><th>Ementa</th><th>AEB</th></tr></thead>
            <tbody>{publicacoes.slice(0, 20).map((p) => (
              <tr key={p.id}><td>{p.data}</td><td>{p.secao}</td><td>{p.tipo}</td><td>{p.orgao}</td><td>{p.ementa.slice(0, 50)}</td><td>{p.referencia_aeb ? "Sim" : "Não"}</td></tr>
            ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
