from nicegui import ui, app
from utils.mobile_layout import mobile_container
from session_state import get_patient
from database import save_triage
from utils.triage_engine import calculate_triage

from components.header_triase import header_triase
from components.progress_bar import progress_bar
from components.ui_system import glass_container

# ======================
# FORMAT
# ======================
def format_angka(value, allow_decimal=False):
    if value is None or value == "":
        return ""
    try:
        value = float(value)
        if allow_decimal:
            return f"{value:.1f}"
        return str(int(value))
    except:
        return str(value)


# ======================
# CLEAN PROBLEMS
# ======================
def clean_problems(masalah_list):
    hasil = []
    seen = set()

    for m in masalah_list:
        key = m.lower().strip()

        # ======================
        # 🔥 NORMALISASI DULU (WAJIB SEBELUM APPEND)
        # ======================

        # TAKIPNEA
        if "takipnea" in key or "napas cepat" in key:
            key = "takipnea"
            m = "Takipnea ringan"

        # DEMAM
        elif "suhu tinggi" in key or "demam" in key:
            key = "demam"
            m = "Demam"

        # HIPOKSEMIA
        elif "hipoksemia" in key:
            key = "hipoksemia"
            m = "Hipoksemia"

        # HIPERTENSI
        elif "hipertensi" in key:
            key = "hipertensi"
            m = "Hipertensi"

        # OBESITAS (🔥 INI YANG KAMU BUTUH)
        elif "obesitas" in key:
            key = "obesitas"

            # PRIORITASKAN YANG ADA BMI
            if "bmi" in m.lower():
                # hapus versi lama kalau ada
                hasil = [x for x in hasil if "obesitas" not in x.lower()]
                hasil.append(m)
                seen.add(key)
                continue
            else:
                m = "Obesitas"

        # ======================
        # APPEND TERAKHIR
        # ======================
        if key not in seen:
            hasil.append(m)
            seen.add(key)

    return hasil


# ======================
# RECOMMENDATION ENGINE
# ======================
def generate_recommendation(triage, problems):

    actions = []

    if triage == "RED":
        actions += [
            "Evaluasi segera (resusitasi area)",
            "Monitoring ketat",
            "Pasang IV line",
        ]

    elif triage == "YELLOW":
        actions += ["Observasi ketat", "Re-evaluasi 15–30 menit"]

    elif triage == "GREEN":
        actions += ["Penanganan non-emergensi"]

    for p in problems:
        p = p.lower()

        if "hipoksemia" in p:
            actions.append("Berikan oksigen")

        if "takipnea" in p:
            actions.append("Evaluasi gangguan pernapasan")

        if "hipotensi" in p or "syok" in p:
            actions.append("Resusitasi cairan IV")

        if "takikardia" in p:
            actions.append("Monitoring hemodinamik")

        if "penurunan kesadaran" in p:
            actions.append("Amankan airway")

        if "nyeri dada" in p:
            actions.append("EKG segera")

        if "hemiparesis" in p or "disartria" in p:
            actions.append("Evaluasi stroke / rujuk")

        if "kontraksi uterus" in p:
            actions += [
                "Edukasi kontraksi palsu vs persalinan",
                "Istirahat dan hidrasi cukup",
                "Observasi frekuensi kontraksi",
                "Monitoring gerak janin",
                "Evaluasi DJJ",
            ]

    unique_actions = list(dict.fromkeys(actions))

    need_konsul = False
    for act in unique_actions:
        if any(
            k in act.lower()
            for k in ["oksigen", "resusitasi", "iv line", "rujuk", "ekg"]
        ):
            need_konsul = True
            break

    if need_konsul:
        unique_actions.append("Konsul DPJP")

    return unique_actions


# ======================
# RESUME
# ======================
def generate_resume(patient, triage_result, plan_text):

    try:
        vital = patient.get("vital", {})
        abcde = patient.get("abcde", {})

        problems = clean_problems(triage_result.get("problems", []))
        problem_text = "\n".join([f"- {p}" for p in problems])

        recommendations = generate_recommendation(triage_result.get("triage"), problems)
        rec_text = "\n".join([f"- {r}" for r in recommendations])

        # Build assessment section based on whether ESI or ABCDE was used
        esi_data = patient.get("esi", {})
        if esi_data.get("esi_level") is not None:
            esi_lvl = esi_data.get("esi_level")
            esi_lbl = triage_result.get("esi_label", f"ESI {esi_lvl}")
            pain = esi_data.get("pain_score", 0)
            hr_flags = esi_data.get("high_risk_flags", [])
            resources = esi_data.get("resources", [])
            assessment_block = f"""ESI TRIAGE
Level    : {esi_lbl}
Pain     : {pain}/10
High-risk: {", ".join(hr_flags) if hr_flags else "-"}
Resources: {", ".join(resources) if resources else "-"}"""
        else:
            assessment_block = f"""ABCDE
A : {abcde.get("airway","")}
B : {abcde.get("breathing","")}
C : {abcde.get("circulation","")}
D : {abcde.get("avpu","")}
E : {abcde.get("exposure","")}"""

        return f"""
IDENTITAS
Petugas : {patient.get("petugas","")}
Nama : {patient.get("nama","")}
Umur : {patient.get("umur","")}

----------------------------

ANAMNESA
Keluhan utama : {patient.get("keluhan","")}

Resume anamnesa :
{patient.get("resume_anamnesa","")}

----------------------------

VITAL SIGN
BB : {format_angka(vital.get("bb"))} kg
TD : {format_angka(vital.get("td_sys"))}/{format_angka(vital.get("td_dia"))} mmHg
Nadi : {format_angka(vital.get("nadi"))} bpm
RR : {format_angka(vital.get("rr"))}
Suhu : {format_angka(vital.get("suhu"), allow_decimal=True)}
SpO2 : {format_angka(vital.get("spo2"))}

----------------------------

{assessment_block}

----------------------------

TRIASE : {triage_result.get("triage","")}

----------------------------

MASALAH KLINIS:
{problem_text}

----------------------------

REKOMENDASI:
{rec_text}

----------------------------

PLAN / TERAPI:
{plan_text}
"""
    except Exception as e:
        print("ERROR generate_resume:", e)
        return "ERROR GENERATE RESUME"


# ======================
# WA MESSAGE (FIX RAPI)
# ======================
def generate_wa_message(patient, triage_result, plan_text):

    vital = patient.get("vital", {})
    abcde = patient.get("abcde", {})
    problems = triage_result.get("problems", [])

    nama = patient.get("nama", "-")
    umur = patient.get("umur", "-")
    jk = patient.get("jenis_kelamin", "").lower()

    if jk == "L":
        jk_text = "Laki-laki"
    elif jk == "P":
        jk_text = "Perempuan"
    else:
        jk_text = "-"

    triase = triage_result.get("triage", "")
    petugas = patient.get("petugas", "-")

    vital_text = (
        f"TD    : {format_angka(vital.get('td_sys'))}/{format_angka(vital.get('td_dia'))}\n"
        f"Nadi  : {format_angka(vital.get('nadi'))}\n"
        f"RR    : {format_angka(vital.get('rr'))}\n"
        f"SpO2  : {format_angka(vital.get('spo2'))}"
    )

    esi_data = patient.get("esi", {})
    if esi_data.get("esi_level") is not None:
        esi_lvl = esi_data.get("esi_level")
        esi_lbl = triage_result.get("esi_label", f"ESI {esi_lvl}") if isinstance(triage_result, dict) else f"ESI {esi_lvl}"
        assessment_text = (
            f"ESI Level : {esi_lbl}\n"
            f"Pain      : {esi_data.get('pain_score', 0)}/10"
        )
    else:
        assessment_text = (
            f"A     : {abcde.get('airway','')}\n"
            f"B     : {abcde.get('breathing','')}\n"
            f"C     : {abcde.get('circulation','')}\n"
            f"D     : {abcde.get('avpu','')}\n"
            f"E     : {abcde.get('exposure','')}"
        )

    return f"""Mohon izin melaporkan pasien:

Nama : {nama}
{jk_text}, {umur} tahun

TRIASE : {triase}

Keluhan utama:
{patient.get("keluhan","")}

VITAL SIGN:
{vital_text}

ASSESSMENT:
{assessment_text}

MASALAH KLINIS:
{chr(10).join(f"- {p}" for p in problems)}

REKOMENDASI:
{chr(10).join(f"- {r}" for r in generate_recommendation(triase, problems))}

PLAN:
{plan_text}

Mohon advis Dok
Petugas: {petugas}
"""


# ======================
# PAGE
# ======================
def step5_page():

    if app.storage.user.get("current_step", 1) < 5:
        ui.navigate.to("/step4")
        return

    patient = get_patient()
    triage_result = calculate_triage(patient)

    masalah_vital = patient.get("masalah_vital", [])
    combined = triage_result.get("problems", []) + masalah_vital
    triage_result["problems"] = clean_problems(combined)

    triase_map = {
        "RED": ("MERAH", "bg-red-500"),
        "YELLOW": ("KUNING", "bg-yellow-500"),
        "GREEN": ("HIJAU", "bg-green-500"),
    }

    triase, color = triase_map.get(triage_result["triage"], ("UNKNOWN", "bg-gray-500"))

    # ESI label (if ESI was used)
    esi_label_text = triage_result.get("esi_label", "")

    saved = {"done": False}

    with mobile_container().classes("items-center"):

        header_triase()
        progress_bar(current_step=5, total_step=5)

        with glass_container():

    # ======================
    # HASIL TRIASE
    # ======================
            ui.label("Hasil Triase").classes("text-sm text-gray-500 text-center mb-1")

            with ui.element("div").classes(
                f"{color} text-white w-full flex items-center justify-center rounded-xl py-2 flex-col gap-0"
            ):
                ui.label(triase).classes("text-2xl font-bold")
                if esi_label_text:
                    ui.label(esi_label_text).classes("text-xs opacity-90 font-medium")

            ui.separator().classes("my-1")

            # ======================
            # MASALAH KLINIS
            # ======================
            ui.label("Masalah Klinis").classes("text-sm text-gray-600")

            if triage_result["problems"]:
                with ui.column().classes("gap-1 mt-1"):
                    for p in triage_result["problems"]:
                        ui.label(f"- {p}").classes("text-sm text-gray-800 leading-tight")
            else:
                ui.label("- Tidak ada masalah signifikan").classes(
                    "text-sm text-gray-400"
                )

            ui.separator().classes("my-1")

            # ======================
            # PLAN
            # ======================
            ui.label("Plan / Terapi").classes("text-sm text-gray-600")
            plan = ui.textarea().classes("w-full min-h-[70px] mt-1 my-0")


            # ======================
            # RESUME
            # ======================
            ui.label("Resume Pemeriksaan").classes("text-sm text-gray-600")

            resume_box = ui.textarea().classes("w-full min-h-[140px] text-xs mt-1")

            def update_resume():
                resume_box.value = generate_resume(
                    patient, triage_result, plan.value or ""
                )

            with ui.column().classes("w-full items-center mt-2"):
                with ui.element("div").classes(
                    "w-full text-center rounded-xl cursor-pointer overflow-hidden"
                ).style(
                    """
                    background: linear-gradient(145deg, #6A00FF, #3F00CC);
                    box-shadow:
                        0 10px 25px rgba(106,0,255,0.4),
                        inset 0 2px 0 rgba(255,255,255,0.3);
                    """
                ).on("click", update_resume):

                    ui.label("Update").classes(
                        "py-2 text-white font-semibold text-sm w-full"
                    )

                update_resume()


        def do_save():
            if saved["done"]:
                return

            try:
                user_id = app.storage.user.get("email")
                save_triage(patient, triage_result, plan.value or "", user_id)
                saved["done"] = True
            except Exception as e:
                print("ERROR SAVE:", e)

        from urllib.parse import quote

        def copy_text():
            do_save()

            try:
                text = generate_wa_message(patient, triage_result, plan.value or "")

                # 🔥 TANPA INDENT (INI KUNCI)
                text = f"```\n{text}\n```"

                encoded = quote(text)
                url = f"https://wa.me/?text={encoded}"

                ui.run_javascript(f"window.open('{url}', '_blank')")

                ui.notify("WhatsApp dibuka")

            except Exception as e:
                ui.notify("Gagal", color="red")

        with ui.row().classes("w-full max-w-sm mx-auto gap-3"):

            with ui.element("div").classes(
                "flex-1 text-center rounded-xl cursor-pointer overflow-hidden"
            ).style(
                """
                background: rgba(230,235,255,0.35);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(120,140,255,0.25);
                box-shadow:
                    0 6px 18px rgba(80,100,255,0.15),
                    inset 0 1px 0 rgba(255,255,255,0.4);
            """
            ).on(
                "click", lambda: ui.navigate.to("/step4")
            ):

                ui.label("Back").classes(
                    "py-2 text-slate-800 font-semibold text-sm w-full"
                )

            with ui.element("div").classes(
                "flex-1 text-center rounded-xl cursor-pointer overflow-hidden"
            ).style(
                """
                background: linear-gradient(145deg, #6A00FF, #3F00CC);
                box-shadow:
                    0 10px 25px rgba(106,0,255,0.4),
                    inset 0 2px 0 rgba(255,255,255,0.3);
            """
            ).on(
                "click", copy_text
            ):

                ui.label("Save & Copy").classes(
                    "py-2 text-white font-semibold text-sm w-full"
                )

            def end_case():
                do_save()
                ui.navigate.to("/dashboard")

            with ui.element("div").classes(
                "flex-1 text-center rounded-xl cursor-pointer overflow-hidden"
            ).style(
                """
                background: linear-gradient(145deg, #6A00FF, #3F00CC);
                box-shadow:
                    0 10px 25px rgba(106,0,255,0.4),
                    inset 0 2px 0 rgba(255,255,255,0.3);
            """
            ).on(
                "click", end_case
            ):

                ui.label("End").classes("py-2 text-white font-semibold text-sm w-full")
