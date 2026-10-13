from pathlib import Path

p = Path(r"F:\edu_Final\static\css\estilos.css")
s = p.read_text(encoding="utf-8")

inicio = s.find("/* ============================================================\n   EDUTURNOS - DASHBOARD MAESTRO FINAL")
fin = s.find("/* ============================================================\n   FIN DASHBOARD MAESTRO", inicio)
fin = s.find("*/", fin) + 2

nuevo = """/* ============================================================
   EDUTURNOS — DASHBOARD UNIFICADO
   ============================================================ */

.dashboard-page[class*="dashboard-rol-"] {
    --dash-ink:#172b4d;
    --dash-blue:#1769e0;
    --dash-gold:#e8ad3d;
    --dash-bg:#f5f7fb;
    --dash-line:#dfe6ef;
    --dash-muted:#66758a;
    background:var(--dash-bg)!important;
    color:var(--dash-ink)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-head {
    position:relative;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:28px;
    padding:30px;
    margin-bottom:22px;
    background:linear-gradient(135deg,#fff,#eef5ff)!important;
    border:1px solid var(--dash-line)!important;
    border-radius:22px!important;
    box-shadow:0 12px 30px rgba(23,43,77,.08)!important;
    overflow:hidden;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-head::before {
    content:"";
    position:absolute;
    top:0;
    left:0;
    width:100%;
    height:5px;
    background:linear-gradient(90deg,var(--dash-blue),var(--dash-gold));
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-head h1 {
    color:var(--dash-ink)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-head .muted {
    color:var(--dash-muted)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-head-info .badge,
.dashboard-page[class*="dashboard-rol-"] .dashboard-card-head .badge {
    background:#e9f2ff!important;
    color:var(--dash-blue)!important;
    border:1px solid #c8dcf8!important;
    border-radius:999px;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-role-art {
    background:linear-gradient(145deg,#fff,#eaf2ff)!important;
    border:1px solid #d5e3f5!important;
    box-shadow:0 8px 20px rgba(23,105,224,.10)!important;
}

.dashboard-page[class*="dashboard-rol-"] .role-symbol {
    background:#edf5ff!important;
    border-color:#cfe0f6!important;
}

.dashboard-page[class*="dashboard-rol-"] .role-symbol span {
    background:linear-gradient(135deg,var(--dash-blue),#0f4fae)!important;
}

.dashboard-page[class*="dashboard-rol-"] .role-symbol i {
    background:var(--dash-gold)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-logout {
    background:var(--dash-ink)!important;
    border-color:var(--dash-ink)!important;
    color:#fff!important;
    border-radius:11px;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-logout:hover {
    background:var(--dash-blue)!important;
    border-color:var(--dash-blue)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-kpis {
    display:grid!important;
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
    gap:16px!important;
    margin-bottom:22px;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-kpi,
.dashboard-page[class*="dashboard-rol-"] .dashboard-card {
    background:#fff!important;
    border:1px solid var(--dash-line)!important;
    border-radius:20px!important;
    box-shadow:0 10px 25px rgba(23,43,77,.06)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-kpi strong {
    color:var(--dash-blue)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-kpi span {
    color:var(--dash-muted)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-card-head h2 {
    color:var(--dash-ink)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action-grid {
    display:grid!important;
    grid-template-columns:repeat(3,minmax(0,1fr))!important;
    gap:16px!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action {
    min-height:170px!important;
    padding:20px!important;
    display:flex!important;
    flex-direction:column!important;
    background:#fff!important;
    border:1px solid var(--dash-line)!important;
    border-radius:17px!important;
    box-shadow:0 7px 18px rgba(23,43,77,.055)!important;
    transition:.2s ease!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action::before {
    content:"";
    width:42px;
    height:4px;
    margin-bottom:16px;
    border-radius:999px;
    background:linear-gradient(90deg,var(--dash-blue),var(--dash-gold));
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action:hover {
    transform:translateY(-4px)!important;
    border-color:#c8d9ee!important;
    box-shadow:0 14px 28px rgba(23,105,224,.11)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action-top {
    display:none!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action-icon {
    display:inline-flex!important;
    width:max-content;
    padding:5px 9px;
    margin-bottom:10px;
    border-radius:8px;
    background:#edf5ff!important;
    border:1px solid #d3e3f7!important;
    color:var(--dash-blue)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action h3 {
    margin:0 0 7px!important;
    color:var(--dash-ink)!important;
    font-size:17px!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action p {
    margin:0!important;
    color:var(--dash-muted)!important;
    line-height:1.5!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-action-link {
    margin-top:auto!important;
    padding-top:15px!important;
    color:var(--dash-blue)!important;
    font-weight:800;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-account-card {
    padding:22px;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-account-text {
    color:var(--dash-muted)!important;
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-account-action {
    margin-top:18px;
    padding-top:16px;
    border-top:1px solid var(--dash-line);
}

.dashboard-page[class*="dashboard-rol-"] .dashboard-account-card .boton {
    background:var(--dash-blue)!important;
    border-color:var(--dash-blue)!important;
    color:#fff!important;
    border-radius:11px;
}

@media(max-width:1000px) {
    .dashboard-page[class*="dashboard-rol-"] .dashboard-action-grid {
        grid-template-columns:repeat(2,minmax(0,1fr))!important;
    }
}

@media(max-width:700px) {
    .dashboard-page[class*="dashboard-rol-"] .dashboard-head {
        flex-direction:column;
        align-items:flex-start;
    }

    .dashboard-page[class*="dashboard-rol-"] .dashboard-kpis {
        grid-template-columns:repeat(2,minmax(0,1fr))!important;
    }

    .dashboard-page[class*="dashboard-rol-"] .dashboard-action-grid {
        grid-template-columns:1fr!important;
    }
}

@media(max-width:520px) {
    .dashboard-page[class*="dashboard-rol-"] .dashboard-kpis {
        grid-template-columns:1fr!important;
    }
}

/* ============================================================
   FIN DASHBOARD UNIFICADO
   ============================================================ */
"""

if inicio < 0 or fin < 0:
    raise SystemExit("ERROR: BLOQUE NO ENCONTRADO")

p.write_text(s[:inicio] + nuevo + s[fin:], encoding="utf-8")
print("OK - DASHBOARD UNIFICADO")
