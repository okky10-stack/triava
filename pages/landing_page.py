from nicegui import ui, app
from nicegui.client import Client


def landing_page():
    # Read lang from cookie (set by /set-lang) or fall back to user storage
    try:
        cookie_lang = Client.current.cookies.get("triava_lang", None)
        lang = cookie_lang if cookie_lang in ("id", "en") else app.storage.user.get("lang", "id")
    except Exception:
        lang = app.storage.user.get("lang", "id")

    # Keep user storage in sync
    app.storage.user["lang"] = lang

    # ── CSS overrides: break out of NiceGUI container ──────────────────────
    ui.add_head_html("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* Kill NiceGUI wrapper constraints */
html, body { margin:0; padding:0; background:#0a0a0f !important; overflow-x:hidden; }
.q-layout, .q-page-container, .q-page { padding:0 !important; min-height:100vh; }
.nicegui-content {
    padding: 0 !important;
    max-width: 100vw !important;
    width: 100vw !important;
    margin: 0 !important;
}

/* ── Landing shell ── */
#lp-root {
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
    background: #0a0a0f;
    min-height: 100vh;
    width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
}

/* ── Blobs ── */
.blob {
    position: fixed;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.18;
    pointer-events: none;
    z-index: 0;
    animation: blobFloat 8s ease-in-out infinite alternate;
}
.blob-1 { width:520px; height:520px; background:#6d28d9; top:-100px; left:-140px; animation-delay:0s; }
.blob-2 { width:420px; height:420px; background:#2563eb; bottom:-80px; right:-100px; animation-delay:3s; }
.blob-3 { width:260px; height:260px; background:#7c3aed; top:40%; left:55%; animation-delay:1.5s; }
@keyframes blobFloat {
    from { transform: translate(0,0) scale(1); }
    to   { transform: translate(20px,30px) scale(1.06); }
}

/* ── Nav ── */
#lp-nav {
    position: sticky; top:0; z-index:100;
    width:100%; box-sizing:border-box;
    padding: 14px 24px;
    display: flex; align-items:center; justify-content:space-between;
    background: rgba(10,10,15,0.7);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.nav-brand { display:flex; align-items:center; gap:10px; }
.nav-logo  { width:34px; height:34px; border-radius:8px; }
.nav-title { font-size:18px; font-weight:800; color:#fff; letter-spacing:0.5px; }
.nav-right { display:flex; align-items:center; gap:10px; }

/* Lang pill */
.lang-pill {
    display:flex; border-radius:999px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    overflow:hidden;
}
.lang-btn {
    padding: 5px 14px; font-size:12px; font-weight:600;
    cursor:pointer; border:none; background:transparent;
    color: rgba(255,255,255,0.5); transition: all 0.2s;
    white-space: nowrap;
}
.lang-btn.active {
    background: rgba(109,40,217,0.7);
    color: #fff;
}

/* Masuk button */
.nav-masuk {
    padding: 7px 20px; border-radius:999px; border:none;
    background: linear-gradient(135deg,#6d28d9,#4f46e5);
    color:#fff; font-size:13px; font-weight:700;
    cursor:pointer;
    box-shadow: 0 4px 14px rgba(109,40,217,0.5);
    transition: transform 0.15s;
}
.nav-masuk:active { transform:scale(0.95); }

/* ── Hero ── */
#lp-hero {
    position:relative; z-index:1;
    width:100%; box-sizing:border-box;
    padding: 80px 24px 60px;
    display: flex; flex-direction:column; align-items:center;
    text-align: center;
}
.hero-badge {
    display:inline-block;
    padding:5px 14px; border-radius:999px;
    background: rgba(109,40,217,0.2);
    border: 1px solid rgba(109,40,217,0.4);
    font-size:12px; font-weight:600; color:#a78bfa;
    margin-bottom:20px;
}
.hero-h1 {
    font-size: clamp(32px,7vw,62px);
    font-weight:800; line-height:1.1;
    color:#fff; margin:0 0 12px;
    max-width:700px;
}
.hero-accent { color:#a78bfa; }
.hero-sub {
    font-size: clamp(14px,2vw,18px);
    color: rgba(226,232,240,0.7);
    max-width:520px; line-height:1.6;
    margin:0 auto 36px;
}
.hero-cta {
    display:inline-block;
    padding:14px 40px; border-radius:999px; border:none;
    background: linear-gradient(135deg,#6d28d9,#4f46e5);
    color:#fff; font-size:16px; font-weight:700;
    cursor:pointer;
    box-shadow: 0 8px 30px rgba(109,40,217,0.55);
    transition: transform 0.15s, box-shadow 0.15s;
    text-decoration:none;
}
.hero-cta:hover { transform:translateY(-2px); box-shadow:0 12px 40px rgba(109,40,217,0.65); }
.hero-cta:active { transform:scale(0.97); }

/* ── Mockup strip ── */
#lp-mockup {
    position:relative; z-index:1;
    display:flex; justify-content:center; align-items:center;
    padding: 0 24px 60px;
}
.mockup-frame {
    width: min(320px, 85vw);
    border-radius:28px;
    border:2px solid rgba(255,255,255,0.1);
    box-shadow: 0 30px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05);
    overflow:hidden;
}
.mockup-frame img { width:100%; display:block; }

/* ── Features ── */
#lp-features {
    position:relative; z-index:1;
    width:100%; box-sizing:border-box;
    padding: 20px 24px 60px;
    max-width:860px; margin:0 auto;
}
.feat-grid {
    display:grid;
    grid-template-columns: repeat(auto-fill, minmax(240px,1fr));
    gap:16px;
}
.feat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius:18px; padding:22px;
    transition: border-color 0.2s, transform 0.2s;
}
.feat-card:hover { border-color:rgba(109,40,217,0.5); transform:translateY(-3px); }
.feat-icon { font-size:28px; margin-bottom:10px; }
.feat-title { font-size:15px; font-weight:700; color:#fff; margin-bottom:6px; }
.feat-desc  { font-size:13px; color:rgba(226,232,240,0.6); line-height:1.5; }

/* ── Section title ── */
.section-label {
    text-align:center; margin-bottom:32px;
}
.section-label h2 {
    font-size: clamp(22px,4vw,32px);
    font-weight:800; color:#fff; margin:0 0 8px;
}
.section-label p {
    font-size:14px; color:rgba(226,232,240,0.55); margin:0;
}

/* ── Footer ── */
#lp-footer {
    position:relative; z-index:1;
    text-align:center; padding:28px 24px;
    border-top:1px solid rgba(255,255,255,0.06);
    font-size:12px; color:rgba(226,232,240,0.35);
}

/* ── Mobile tweaks ── */
@media (max-width:480px) {
    #lp-hero { padding-top:52px; }
    .hero-h1 { font-size:28px; }
}
</style>
""")

    # ── Content (server-side bilingual) ────────────────────────────────────
    is_id = (lang == "id")

    badge      = "🏥 Sistem Triase Klinis Digital" if is_id else "🏥 Digital Clinical Triage System"
    h1_line1   = "Triase Cepat," if is_id else "Rapid Triage,"
    h1_accent  = "Keputusan Tepat" if is_id else "Right Decisions"
    hero_sub   = (
        "Triava membantu tenaga kesehatan melakukan penilaian awal pasien secara terstruktur, cepat, dan akurat — kapan saja, di mana saja."
        if is_id else
        "Triava helps healthcare workers perform structured, rapid, and accurate patient assessment — anytime, anywhere."
    )
    cta_text   = "Mulai Sekarang" if is_id else "Get Started"
    feat_title = "Fitur Unggulan" if is_id else "Key Features"
    feat_sub   = "Dirancang untuk kebutuhan klinis nyata" if is_id else "Designed for real clinical needs"

    features = [
        ("⚡", "ESI Triage 5-Level" if is_id else "ESI 5-Level Triage",
         "Penilaian prioritas pasien berdasarkan standar Emergency Severity Index internasional."
         if is_id else
         "Patient priority scoring based on the international Emergency Severity Index standard."),
        ("🧠", "Anamnesa Terstruktur" if is_id else "Structured Anamnesis",
         "Panduan SAMPLE & OPQRST memastikan tidak ada keluhan yang terlewat."
         if is_id else
         "SAMPLE & OPQRST guides ensure no complaint is missed."),
        ("📊", "Vital Signs Otomatis" if is_id else "Automatic Vital Signs",
         "Interpretasi otomatis tekanan darah, nadi, saturasi, dan pernapasan."
         if is_id else
         "Automatic interpretation of BP, pulse, SpO₂, and respiratory rate."),
        ("📋", "Laporan PDF" if is_id else "PDF Report",
         "Ekspor rekam triase pasien ke PDF dalam satu klik untuk dokumentasi."
         if is_id else
         "Export patient triage records to PDF in one click for documentation."),
        ("🏥", "Riwayat Pasien" if is_id else "Patient History",
         "Akses cepat ke riwayat triase pasien sebelumnya untuk tindak lanjut optimal."
         if is_id else
         "Quick access to previous triage records for optimal follow-up."),
        ("💊", "Modul Farmasi" if is_id else "Pharmacy Module",
         "Pencatatan obat dan resep terintegrasi dalam alur triase."
         if is_id else
         "Integrated medication and prescription recording within the triage workflow."),
        ("📱", "Mobile-First" if is_id else "Mobile-First",
         "Antarmuka responsif yang nyaman digunakan di ponsel maupun tablet."
         if is_id else
         "Responsive interface comfortable on phones and tablets alike."),
        ("🔒", "Privasi & Keamanan" if is_id else "Privacy & Security",
         "Data pasien terenkripsi, akses berbasis peran, dan audit trail lengkap."
         if is_id else
         "Encrypted patient data, role-based access, and complete audit trail."),
    ]

    lang_id_cls = "active" if is_id else ""
    lang_en_cls = "" if is_id else "active"
    footer_txt  = (
        f"v3.0.1 · Ruang Dokter's Lab · © 2025 Triava"
        if is_id else
        f"v3.0.1 · Ruang Dokter's Lab · © 2025 Triava"
    )

    feat_cards_html = "\n".join(
        f"""<div class="feat-card">
  <div class="feat-icon">{icon}</div>
  <div class="feat-title">{title}</div>
  <div class="feat-desc">{desc}</div>
</div>"""
        for icon, title, desc in features
    )

    masuk_label = "Masuk" if is_id else "Sign In"

    html_content = f"""
<div id="lp-root">
  <!-- blobs -->
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="blob blob-3"></div>

  <!-- NAV -->
  <nav id="lp-nav">
    <div class="nav-brand">
      <img class="nav-logo" src="/static/icon-192.png" alt="Triava">
      <span class="nav-title">Triava</span>
    </div>
    <div class="nav-right">
      <div class="lang-pill">
        <button class="lang-btn {lang_id_cls}" onclick="setLang('id')">🇮🇩 ID</button>
        <button class="lang-btn {lang_en_cls}" onclick="setLang('en')">🇬🇧 EN</button>
      </div>
      <button class="nav-masuk" onclick="window.location='/login'">{masuk_label}</button>
    </div>
  </nav>

  <!-- HERO -->
  <section id="lp-hero">
    <div class="hero-badge">{badge}</div>
    <h1 class="hero-h1">
      {h1_line1}<br><span class="hero-accent">{h1_accent}</span>
    </h1>
    <p class="hero-sub">{hero_sub}</p>
    <a class="hero-cta" href="/login">{cta_text} →</a>
  </section>

  <!-- MOCKUP -->
  <div id="lp-mockup">
    <div class="mockup-frame">
      <img src="/static/icon-512.png" alt="Triava App">
    </div>
  </div>

  <!-- FEATURES -->
  <section id="lp-features">
    <div class="section-label">
      <h2>{feat_title}</h2>
      <p>{feat_sub}</p>
    </div>
    <div class="feat-grid">
      {feat_cards_html}
    </div>
  </section>

  <!-- FOOTER -->
  <footer id="lp-footer">{footer_txt}</footer>
</div>
"""

    ui.html(html_content)

    ui.add_body_html("""
<script>
function setLang(l) {
  fetch('/set-lang?lang=' + l + '&next=/', {redirect:'follow'})
    .then(() => location.reload());
}
</script>
""")
