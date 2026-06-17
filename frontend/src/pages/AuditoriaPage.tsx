import { useEffect, useState } from "react";
import { api, AuditoriaResumo, SaldoAlongado } from "../api";
import EChart from "../components/EChart";
import type { EChartsOption } from "echarts";

function brl(v: number): string {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

function KpiCard({ titulo, valor, cor }: { titulo: string; valor: string; cor: string }) {
  return (
    <div className="kpi" style={{ borderTopColor: cor }}>
      <span className="kpi-titulo">{titulo}</span>
      <span className="kpi-valor">{valor}</span>
    </div>
  );
}

const UGS = [
  { cod: "", nome: "Todas as UGs da AEB" },
  { cod: "24205000", nome: "24205000 — AEB Sede" },
  { cod: "24205001", nome: "24205001 — ULA (Alcântara)" },
  { cod: "24205002", nome: "24205002 — INPE" },
];

export default function AuditoriaPage() {
  const [meses, setMeses] = useState(12);
  const [minMeses, setMinMeses] = useState(3);
  const [ug, setUg] = useState("");
  const [dados, setDados] = useState<SaldoAlongado[]>([]);
  const [resumo, setResumo] = useState<AuditoriaResumo | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    setCarregando(true);
    Promise.all([api.auditoriaSaldos(meses, minMeses, ug || undefined), api.auditoriaResumo(meses, ug || undefined)])
      .then(([saldos, res]) => {
        setDados(saldos);
        setResumo(res);
        setErro(null);
      })
      .catch((e) => setErro(String(e)))
      .finally(() => setCarregando(false));
  }, [meses, minMeses, ug]);

  const optRanking: EChartsOption = {
    tooltip: { trigger: "axis", valueFormatter: (v) => brl(Number(v)) },
    grid: { left: 220, right: 30, top: 10, bottom: 20 },
    xAxis: { type: "value", axisLabel: { formatter: (v: number) => `${(v / 1e6).toFixed(0)} M` } },
    yAxis: {
      type: "category",
      data: dados.map((d) => `${d.contabil} — ${d.desc_contabil.slice(0, 30)}`).reverse(),
      axisLabel: { width: 200, overflow: "truncate" },
    },
    series: [
      { type: "bar", data: dados.map((d) => d.saldo_atual).reverse(), color: "#c62828" },
    ],
  };

  const optMeses: EChartsOption = {
    tooltip: { trigger: "axis" },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: "category", data: dados.map((d) => d.contabil) },
    yAxis: { type: "value", name: "Meses" },
    series: [
      {
        type: "bar",
        data: dados.map((d) => d.meses_alongados),
        color: "#f29900",
        label: { show: true, position: "top" },
      },
    ],
  };

  return (
    <div className="app">
      <header className="topo">
        <div>
          <h1>Auditoria — Saldos Alongados</h1>
          <p className="subtitulo">
            Detecção de contas contábeis com saldo inalterado por N meses consecutivos
            (origem: SIAFI / Tesouro Gerencial)
          </p>
        </div>
      </header>

      {erro && <div className="erro">Falha ao consultar a API: {erro}</div>}

      <section className="filtros" aria-label="Parâmetros">
        <label>
          UG
          <select value={ug} onChange={(e) => setUg(e.target.value)}>
            {UGS.map((u) => (
              <option key={u.cod} value={u.cod}>{u.nome}</option>
            ))}
          </select>
        </label>
        <label>
          Meses analisados
          <select value={meses} onChange={(e) => setMeses(Number(e.target.value))}>
            {[6, 9, 12, 18, 24, 36].map((m) => (
              <option key={m} value={m}>{m} meses</option>
            ))}
          </select>
        </label>
        <label>
          Mín. meses consecutivos
          <select value={minMeses} onChange={(e) => setMinMeses(Number(e.target.value))}>
            {[2, 3, 4, 6, 9, 12].map((m) => (
              <option key={m} value={m}>{m} meses</option>
            ))}
          </select>
        </label>
      </section>

      {resumo && (
        <section className="kpis">
          <KpiCard titulo="Total de Contas" valor={String(resumo.total_contas)} cor="#5e5e5e" />
          <KpiCard titulo="Contas Alongadas" valor={String(resumo.total_alongadas)} cor="#c62828" />
          <KpiCard titulo="Maior Alongamento" valor={`${resumo.maior_alongamento} meses`} cor="#f29900" />
          <KpiCard titulo="Saldo Total Alongado" valor={brl(resumo.saldo_total_alongado)} cor="#1351b4" />
        </section>
      )}

      <section className="grid">
        <div className="card grande">
          <h2>Ranking por Saldo Alongado</h2>
          <EChart option={optRanking} height={Math.max(300, dados.length * 40 + 40)} />
        </div>
        <div className="card">
          <h2>Meses Consecutivos por Conta</h2>
          <EChart option={optMeses} height={320} />
        </div>
        <div className="card">
          <h2>Detalhamento</h2>
          <table className="tabela">
            <thead>
              <tr>
                <th>UG</th>
                <th>Conta</th>
                <th>Descrição</th>
                <th>Corrente</th>
                <th>Meses</th>
                <th>Saldo</th>
                <th>Ref.</th>
              </tr>
            </thead>
            <tbody>
              {dados.map((d) => (
                <tr key={`${d.ug}-${d.contabil}-${d.corrente}`}>
                  <td>{d.ug}</td>
                  <td>{d.contabil}</td>
                  <td>{d.desc_contabil}</td>
                  <td>{d.corrente}</td>
                  <td>{d.meses_alongados}</td>
                  <td>{brl(d.saldo_atual)}</td>
                  <td>{d.mes_referencia}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="rodape">
        {carregando ? "Atualizando..." : `Contas exibidas: ${dados.length}`}
        {" · "}API: <a href="/api/v1/auditoria/saldos-alongados" target="_blank" rel="noreferrer">/api/v1/auditoria</a>
      </footer>
    </div>
  );
}
