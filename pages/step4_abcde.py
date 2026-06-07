from nicegui import ui, app
from utils.mobile_layout import mobile_container
from session_state import get_patient
from components.header_triase import header_triase
from components.progress_bar import progress_bar
from components.ui_system import glass_container

try:
    from utils.i18n import current_lang
except ImportError:
    def current_lang(): return "id"


# ======================
# ESI CONSTANTS
# ======================
ESI_COLORS = {
    1: ("bg-red-600", "text-white"),
    2: ("bg-red-400", "text-white"),
    3: ("bg-yellow-400", "text-gray-900"),
    4: ("bg-green-500", "text-white"),
    5: ("bg-green-200", "text-gray-800"),
}

ESI_LABELS = {
    "id": {
        1: "ESI 1 — Resusitasi",
        2: "ESI 2 — Emergensi",
        3: "ESI 3 — Urgensi",
        4: "ESI 4 — Semi-Urgensi",
        5: "ESI 5 — Non-Urgensi",
    },
    "en": {
        1: "ESI 1 — Resuscitation",
        2: "ESI 2 — Emergent",
        3: "ESI 3 — Urgent",
        4: "ESI 4 — Less Urgent",
        5: "ESI 5 — Non-Urgent",
    },
}

ESI_DESCS = {
    "id": {
        1: "Intervensi life-saving segera",
        2: "Risiko tinggi / kondisi tidak stabil",
        3: "Butuh ≥2 tindakan/pemeriksaan",
        4: "Butuh 1 tindakan/pemeriksaan",
        5: "Tidak butuh tindakan tambahan",
    },
    "en": {
        1: "Immediate life-saving intervention",
        2: "High-risk / unstable condition",
        3: "Needs ≥2 resources",
        4: "Needs 1 resource",
        5: "No resources needed",
    },
}

HIGH_RISK_OPTIONS = {
    "id": [
        "Nyeri dada (chest pain)",
        "Sesak nafas berat",
        "Tanda stroke (bicara pelo, lemah satu sisi, wajah asimetris)",
        "Konfusi / disorientasi / tidak kooperatif",
        "Letargis / sulit dibangunkan",
        "Perdarahan tidak terkontrol",
        "Gula darah sangat rendah (hipoglikemi)",
        "Overdosis obat / keracunan",
        "Suicidal dengan rencana aktif",
        "Alergi berat / anafilaksis",
    ],
    "en": [
        "Chest pain",
        "Severe shortness of breath",
        "Stroke signs (slurred speech, one-sided weakness, facial droop)",
        "Confusion / disorientation / uncooperative",
        "Lethargic / difficult to arouse",
        "Uncontrolled bleeding",
        "Severe hypoglycemia",
        "Drug overdose / poisoning",
        "Suicidal with active plan",
        "Severe allergy / anaphylaxis",
    ],
}

RESOURCE_OPTIONS = {
    "id": [
        "Laboratorium / darah",
        "EKG / monitoring jantung",
        "Rontgen / X-ray",
        "CT Scan / MRI",
        "Infus / cairan IV",
        "Obat IV/IM/nebulisasi",
        "Perawatan luka / jahit / bidai",
        "Urinalisis / urin rutin",
        "Konsultasi spesialis",
        "Prosedur sederhana (NGT, kateter, dll)",
    ],
    "en": [
        "Lab work / blood tests",
        "ECG / cardiac monitoring",
        "X-ray",
        "CT scan / MRI",
        "IV fluids / IV access",
        "IV/IM/nebulized medications",
        "Wound care / sutures / splint",
        "Urinalysis",
        "Specialist consult",
        "Simple procedure (NGT, catheter, etc.)",
    ],
}

TRIAGE_FROM_ESI = {1: "RED", 2: "RED", 3: "YELLOW", 4: "GREEN", 5: "GREEN"}


def _safe(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def _check_danger_zone(patient: dict) -> list:
    """Return list of danger-zone vital findings from step3 data."""
    v = patient.get("vital", {})
    hr = _safe(v.get("nadi"), 80)
    rr = _safe(v.get("rr"), 16)
    spo2 = _safe(v.get("spo2"), 98)
    sbp = _safe(v.get("td_sys"), 120)

    flags = []
    if hr > 100:
        flags.append(f"HR {int(hr)} bpm (>100)")
    elif hr < 50:
        flags.append(f"HR {int(hr)} bpm (<50)")
    if rr > 20:
        flags.append(f"RR {int(rr)} (/min >20)")
    elif rr < 10:
        flags.append(f"RR {int(rr)} (/min <10)")
    if spo2 < 92:
        flags.append(f"SpO2 {int(spo2)}% (<92%)")
    if sbp < 90:
        flags.append(f"SBP {int(sbp)} mmHg (<90)")
    return flags


# ======================
# MAIN PAGE
# ======================
def step4_page():

    if app.storage.user.get("current_step", 1) < 4:
        ui.navigate.to("/step3")
        return

    patient = get_patient()
    lang = current_lang()
    esi_saved = patient.get("esi", {})
    danger_flags = _check_danger_zone(patient)

    # ── mutable state ──────────────────────────────────────
    state = {
        "life_threat": esi_saved.get("life_threat", None),   # None | True | False
        "high_risk": set(esi_saved.get("high_risk_flags", [])),
        "pain_score": int(esi_saved.get("pain_score", 0)),
        "resources": set(esi_saved.get("resources", [])),
        "esi_level": esi_saved.get("esi_level", None),
    }

    def compute_esi() -> int | None:
        if state["life_threat"] is True:
            state["esi_level"] = 1
        elif state["life_threat"] is False:
            if state["high_risk"] or state["pain_score"] >= 7:
                state["esi_level"] = 2
            else:
                count = len(state["resources"])
                if count >= 2:
                    # Danger zone vitals → promote to ESI 2
                    if danger_flags:
                        state["esi_level"] = 2
                    else:
                        state["esi_level"] = 3
                elif count == 1:
                    state["esi_level"] = 4
                else:
                    state["esi_level"] = 5
        else:
            state["esi_level"] = None
        return state["esi_level"]

    # ── build UI ───────────────────────────────────────────
    header_triase()

    with mobile_container():
        progress_bar(current_step=4, total_step=5)

        with glass_container():

            # Title
            title_text = "ESI Triage Assessment" if lang == "en" else "Penilaian Triase ESI"
            ui.label(title_text).classes(
                "text-2xl font-bold text-center w-full text-slate-700 mb-1"
            )

            # ── ESI BADGE (live) ────────────────────────────
            badge_container = ui.element("div").classes("w-full mb-3")

            def render_badge():
                badge_container.clear()
                lvl = state["esi_level"]
                with badge_container:
                    if lvl is None:
                        with ui.element("div").classes(
                            "w-full bg-gray-100 rounded-xl py-3 text-center"
                        ):
                            lbl = "Answer questions below" if lang == "en" else "Jawab pertanyaan di bawah"
                            ui.label(lbl).classes("text-gray-400 text-sm")
                    else:
                        bg, txt = ESI_COLORS[lvl]
                        with ui.element("div").classes(
                            f"{bg} {txt} w-full rounded-xl py-3 text-center"
                        ):
                            ui.label(ESI_LABELS[lang][lvl]).classes(
                                "text-xl font-bold"
                            )
                            ui.label(ESI_DESCS[lang][lvl]).classes(
                                "text-sm opacity-90"
                            )
                        # Danger zone warning for ESI 3 promoted to 2
                        if lvl == 2 and danger_flags and len(state["resources"]) >= 2 and not state["high_risk"] and state["pain_score"] < 7:
                            w_title = "Danger Zone Vitals — promoted to ESI 2" if lang == "en" else "Vital Danger Zone — naik ke ESI 2"
                            with ui.element("div").classes(
                                "w-full bg-orange-100 border border-orange-300 rounded-xl px-3 py-2 mt-2"
                            ):
                                ui.label(f"⚠ {w_title}").classes(
                                    "text-orange-700 text-xs font-semibold"
                                )
                                for f in danger_flags:
                                    ui.label(f"• {f}").classes(
                                        "text-orange-600 text-xs"
                                    )

            render_badge()

            # ── Danger zone vitals info ─────────────────────
            if danger_flags:
                dz_title = "⚠ Danger Zone Vitals Detected" if lang == "en" else "⚠ Vital Tanda Bahaya Terdeteksi"
                with ui.element("div").classes(
                    "w-full bg-orange-50 border border-orange-200 rounded-xl px-3 py-2 mb-2"
                ):
                    ui.label(dz_title).classes(
                        "text-orange-700 text-xs font-semibold mb-1"
                    )
                    for f in danger_flags:
                        ui.label(f"• {f}").classes("text-orange-600 text-xs")

            ui.separator().classes("my-2")

            # ══════════════════════════════════════════════
            # STEP A — LIFE THREAT
            # ══════════════════════════════════════════════
            q_a = (
                "Does this patient require an immediate life-saving intervention?"
                if lang == "en"
                else "Apakah pasien ini membutuhkan intervensi life-saving segera?"
            )
            ui.label("A").classes(
                "text-xs font-bold bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center"
            )
            ui.label(q_a).classes("text-sm font-semibold text-slate-700 mt-1")

            eg_a = (
                "e.g. not breathing, pulseless, needs intubation / BVM / defibrillation"
                if lang == "en"
                else "misal: tidak bernafas, nadi tidak teraba, butuh intubasi / BVM / defibrilasi"
            )
            ui.label(eg_a).classes("text-xs text-gray-400 italic mb-2")

            a_row = ui.row().classes("w-full gap-2 mt-0")

            with a_row:
                btn_yes_el = ui.element("div").classes(
                    "flex-1 text-center rounded-xl cursor-pointer py-3 border-2"
                )
                with btn_yes_el:
                    ui.label("YES" if lang == "en" else "YA").classes(
                        "font-bold text-sm pointer-events-none"
                    )

                btn_no_el = ui.element("div").classes(
                    "flex-1 text-center rounded-xl cursor-pointer py-3 border-2"
                )
                with btn_no_el:
                    ui.label("NO" if lang == "en" else "TIDAK").classes(
                        "font-bold text-sm pointer-events-none"
                    )

            # Section B & C containers (shown/hidden)
            section_b = ui.column().classes("w-full mt-3")
            section_c = ui.column().classes("w-full mt-3")

            def style_a_buttons():
                if state["life_threat"] is True:
                    btn_yes_el.style(
                        "background:#dc2626;border-color:#dc2626;color:white;"
                    )
                    btn_no_el.style(
                        "background:transparent;border-color:#d1d5db;color:#374151;"
                    )
                elif state["life_threat"] is False:
                    btn_yes_el.style(
                        "background:transparent;border-color:#d1d5db;color:#374151;"
                    )
                    btn_no_el.style(
                        "background:#16a34a;border-color:#16a34a;color:white;"
                    )
                else:
                    btn_yes_el.style(
                        "background:transparent;border-color:#d1d5db;color:#374151;"
                    )
                    btn_no_el.style(
                        "background:transparent;border-color:#d1d5db;color:#374151;"
                    )

            # Initial style
            style_a_buttons()
            section_b.visible = state["life_threat"] is False
            section_c.visible = state["life_threat"] is False

            # High-risk checkbox refs
            hr_checkboxes: dict = {}
            pain_label_ref = {}
            resource_checkboxes: dict = {}

            def on_yes():
                state["life_threat"] = True
                state["high_risk"] = set()
                state["resources"] = set()
                state["pain_score"] = 0
                compute_esi()
                style_a_buttons()
                section_b.visible = False
                section_c.visible = False
                render_badge()

            def on_no():
                state["life_threat"] = False
                compute_esi()
                style_a_buttons()
                section_b.visible = True
                section_c.visible = True
                render_badge()

            btn_yes_el.on("click", on_yes)
            btn_no_el.on("click", on_no)

            # ════════════════════════════════════════════════
            # STEP B — HIGH-RISK / ALTERED MENTAL STATUS
            # ════════════════════════════════════════════════
            with section_b:
                ui.separator().classes("mb-2")
                ui.label("B").classes(
                    "text-xs font-bold bg-orange-500 text-white rounded-full w-5 h-5 flex items-center justify-center"
                )
                q_b = (
                    "Is this a high-risk situation or does the patient appear altered?"
                    if lang == "en"
                    else "Apakah ini situasi berisiko tinggi atau pasien tampak tidak stabil?"
                )
                ui.label(q_b).classes("text-sm font-semibold text-slate-700 mt-1 mb-2")

                opts = HIGH_RISK_OPTIONS[lang]
                for opt in opts:
                    cb = ui.checkbox(opt, value=(opt in state["high_risk"])).classes(
                        "text-sm w-full"
                    )
                    hr_checkboxes[opt] = cb

                    def _on_hr_change(e, o=opt):
                        if e.sender.value:
                            state["high_risk"].add(o)
                        else:
                            state["high_risk"].discard(o)
                        compute_esi()
                        render_badge()

                    cb.on("update:model-value", _on_hr_change)

                ui.separator().classes("my-2")

                pain_q = (
                    "Pain / distress score (NRS 0–10)"
                    if lang == "en"
                    else "Skor nyeri / distres pasien (NRS 0–10)"
                )
                ui.label(pain_q).classes("text-sm font-semibold text-slate-700")
                pain_hint = (
                    "Score ≥7 = ESI 2 regardless of resources"
                    if lang == "en"
                    else "Skor ≥7 = ESI 2 meskipun sumber daya sedikit"
                )
                ui.label(pain_hint).classes("text-xs text-gray-400 italic mb-1")

                pain_val_label = ui.label(f"{state['pain_score']} / 10").classes(
                    "text-lg font-bold text-center w-full text-slate-700"
                )
                pain_label_ref["lbl"] = pain_val_label

                pain_slider = ui.slider(
                    min=0, max=10, step=1, value=state["pain_score"]
                ).classes("w-full mt-1")

                with ui.row().classes("w-full justify-between text-xs text-gray-400"):
                    ui.label("0" if lang == "en" else "0")
                    ui.label("No pain" if lang == "en" else "Tidak nyeri")
                    ui.label("10")
                    ui.label("Worst" if lang == "en" else "Terberat")

                def on_pain_change(e):
                    state["pain_score"] = int(e.sender.value)
                    pain_val_label.text = f"{state['pain_score']} / 10"
                    compute_esi()
                    render_badge()

                pain_slider.on("update:model-value", on_pain_change)

            # ════════════════════════════════════════════════
            # STEP C — RESOURCE COUNT
            # ════════════════════════════════════════════════
            with section_c:
                ui.separator().classes("my-2 mt-4")
                ui.label("C").classes(
                    "text-xs font-bold bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center"
                )
                q_c = (
                    "How many resources will this patient need?"
                    if lang == "en"
                    else "Berapa banyak tindakan/pemeriksaan yang dibutuhkan pasien ini?"
                )
                ui.label(q_c).classes("text-sm font-semibold text-slate-700 mt-1")
                hint_c = (
                    "Select all that apply. 0=ESI 5 · 1=ESI 4 · ≥2=ESI 3"
                    if lang == "en"
                    else "Pilih semua yang sesuai. 0=ESI 5 · 1=ESI 4 · ≥2=ESI 3"
                )
                ui.label(hint_c).classes("text-xs text-gray-400 italic mb-2")

                res_count_label = ui.label(
                    f"{'Selected' if lang == 'en' else 'Dipilih'}: {len(state['resources'])}"
                ).classes("text-sm font-semibold text-blue-600")

                opts_r = RESOURCE_OPTIONS[lang]
                for opt in opts_r:
                    cb = ui.checkbox(opt, value=(opt in state["resources"])).classes(
                        "text-sm w-full"
                    )
                    resource_checkboxes[opt] = cb

                    def _on_res_change(e, o=opt):
                        if e.sender.value:
                            state["resources"].add(o)
                        else:
                            state["resources"].discard(o)
                        res_count_label.text = (
                            f"{'Selected' if lang == 'en' else 'Dipilih'}: {len(state['resources'])}"
                        )
                        compute_esi()
                        render_badge()

                    cb.on("update:model-value", _on_res_change)

            ui.separator().classes("my-3")

        # ======================
        # SAVE FUNCTION
        # ======================
        def save_esi():
            lvl = compute_esi()
            data = {
                "esi_level": lvl,
                "life_threat": state["life_threat"],
                "high_risk_flags": list(state["high_risk"]),
                "pain_score": state["pain_score"],
                "resources": list(state["resources"]),
                "danger_zone": bool(danger_flags),
                "danger_zone_flags": danger_flags,
                "triage_color": TRIAGE_FROM_ESI.get(lvl) if lvl else None,
            }
            patient["esi"] = data

            # Also write backwards-compatible abcde keys
            # so step5/triage_engine still works
            patient.setdefault("abcde", {})["esi_level"] = lvl

        # ======================
        # BUTTONS
        # ======================
        with ui.grid(columns=3).classes("w-full max-w-sm mx-auto gap-2 mt-2"):

            with ui.element("div").classes(
                "flex-1 text-center rounded-xl cursor-pointer overflow-hidden"
            ).style(
                "background:rgba(230,235,255,0.35);backdrop-filter:blur(16px);"
                "border:1px solid rgba(120,140,255,0.25);"
                "box-shadow:0 6px 18px rgba(80,100,255,0.15),inset 0 1px 0 rgba(255,255,255,0.4);"
            ).on("click", lambda: ui.navigate.to("/step3")):
                ui.label("Back").classes("py-2 text-slate-800 font-semibold text-sm")

            with ui.element("div").classes(
                "flex-1 text-center rounded-xl cursor-pointer overflow-hidden"
            ).style(
                "background:linear-gradient(145deg,#6A00FF,#3F00CC);"
                "box-shadow:0 10px 25px rgba(106,0,255,0.4),inset 0 2px 0 rgba(255,255,255,0.3);"
            ).on("click", lambda: (save_esi(), ui.notify("Saved" if lang == "en" else "Tersimpan"))):
                ui.label("Save").classes("py-2 text-white font-semibold text-sm")

            def next_step():
                save_esi()
                if state["esi_level"] is None:
                    ui.notify(
                        "Please complete the assessment first"
                        if lang == "en"
                        else "Lengkapi penilaian terlebih dahulu",
                        color="red",
                    )
                    return
                app.storage.user["current_step"] = 5
                ui.navigate.to("/step5")

            with ui.element("div").classes(
                "flex-1 text-center rounded-xl cursor-pointer overflow-hidden"
            ).style(
                "background:linear-gradient(145deg,#6A00FF,#3F00CC);"
                "box-shadow:0 10px 25px rgba(106,0,255,0.4),inset 0 2px 0 rgba(255,255,255,0.3);"
            ).on("click", next_step):
                ui.label("Next").classes("py-2 text-white font-semibold text-sm")
