import { useState } from "react";
import OrcamentoPage from "./pages/OrcamentoPage";
import AuditoriaPage from "./pages/AuditoriaPage";
import ContratosPage from "./pages/ContratosPage";
import RHPage from "./pages/RHPage";
import ComunicacaoPage from "./pages/ComunicacaoPage";
import EducacaoPage from "./pages/EducacaoPage";
import OperacoesPage from "./pages/OperacoesPage";
import GovernancaPage from "./pages/GovernancaPage";
import EventosPage from "./pages/EventosPage";
import TransfereGovPage from "./pages/TransfereGovPage";
import DouPage from "./pages/DouPage";
import AcordosPage from "./pages/AcordosPage";
import DGEPPage from "./pages/DGEPPage";

type Tab =
  | "orcamento"
  | "auditoria"
  | "contratos"
  | "rh"
  | "comunicacao"
  | "educacao"
  | "operacoes"
  | "governanca"
  | "eventos"
  | "transferegov"
  | "dou"
  | "acordos"
  | "dgep";

const TABS: { key: Tab; label: string; group: string }[] = [
  { key: "orcamento", label: "Orçamento / Execução", group: "Financeiro" },
  { key: "auditoria", label: "Auditoria — Saldos Alongados", group: "Financeiro" },
  { key: "contratos", label: "Contratos e Aquisições", group: "Administrativo" },
  { key: "rh", label: "RH — Gestão de Pessoas", group: "Administrativo" },
  { key: "comunicacao", label: "Comunicação — ARI", group: "Institucional" },
  { key: "eventos", label: "Eventos — GAB", group: "Institucional" },
  { key: "dou", label: "Publicações DOU", group: "Institucional" },
  { key: "educacao", label: "Educação — AEB Escola", group: "Técnico" },
  { key: "operacoes", label: "Operações Espaciais", group: "Técnico" },
  { key: "transferegov", label: "TransfereGov", group: "Técnico" },
  { key: "acordos", label: "Acordos Internacionais", group: "Técnico" },
  { key: "governanca", label: "Governança e Integridade", group: "Estratégico" },
  { key: "dgep", label: "Planejamento Estratégico — DGEP", group: "Estratégico" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("orcamento");
  const [menuOpen, setMenuOpen] = useState(false);

  const groups = [...new Set(TABS.map((t) => t.group))];

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside
        className="side-menu"
        style={{
          width: menuOpen ? 240 : 60,
          background: "#1a237e",
          color: "#fff",
          transition: "width 0.2s",
          overflow: "hidden",
          flexShrink: 0,
        }}
      >
        <div style={{ padding: 12, borderBottom: "1px solid #3949ab", display: "flex", alignItems: "center", gap: 8 }}>
          <button onClick={() => setMenuOpen(!menuOpen)} style={{ background: "none", border: "none", color: "#fff", fontSize: 20, cursor: "pointer" }}>
            {menuOpen ? "\u2266" : "\u2266"}
          </button>
          {menuOpen && <span style={{ fontWeight: 700, fontSize: 14 }}>Painéis AEB</span>}
        </div>
        {groups.map((g) => (
          <div key={g}>
            {menuOpen && (
              <div style={{ padding: "8px 12px", fontSize: 10, textTransform: "uppercase", color: "#9fa8da", letterSpacing: 1 }}>{g}</div>
            )}
            {TABS.filter((t) => t.group === g).map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                style={{
                  width: "100%",
                  textAlign: "left",
                  padding: "10px 12px",
                  background: tab === t.key ? "#3949ab" : "transparent",
                  border: "none",
                  color: "#fff",
                  cursor: "pointer",
                  fontSize: 13,
                  borderLeft: tab === t.key ? "3px solid #f29900" : "3px solid transparent",
                  whiteSpace: "nowrap",
                }}
              >
                {menuOpen ? t.label : t.label.slice(0, 2)}
              </button>
            ))}
          </div>
        ))}
      </aside>
      <main style={{ flex: 1, overflow: "auto" }}>
        {tab === "orcamento" && <OrcamentoPage />}
        {tab === "auditoria" && <AuditoriaPage />}
        {tab === "contratos" && <ContratosPage />}
        {tab === "rh" && <RHPage />}
        {tab === "comunicacao" && <ComunicacaoPage />}
        {tab === "educacao" && <EducacaoPage />}
        {tab === "operacoes" && <OperacoesPage />}
        {tab === "governanca" && <GovernancaPage />}
        {tab === "eventos" && <EventosPage />}
        {tab === "transferegov" && <TransfereGovPage />}
        {tab === "dou" && <DouPage />}
        {tab === "acordos" && <AcordosPage />}
        {tab === "dgep" && <DGEPPage />}
      </main>
    </div>
  );
}
