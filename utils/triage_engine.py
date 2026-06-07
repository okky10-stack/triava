"""
TRIAGE ENGINE v5.1 (SAFE MERGE)

- Semua logic v4 DIPERTAHANKAN
- FIX AVPU (critical bug)
- ABCDE sekarang benar-benar mempengaruhi triage
- Tidak mengubah UX / struktur app
"""


# =========================
# 🔥 SAFE VALUE
# =========================
def safe_val(v, default):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except:
        return default


# =========================
# 🔥 NORMALIZE AVPU (FIX BUG)
# =========================
def normalize_avpu(avpu_text):
    if not avpu_text:
        return ""

    t = avpu_text.lower()

    if "alert" in t:
        return "A"
    elif "voice" in t:
        return "V"
    elif "pain" in t:
        return "P"
    elif "unresponsive" in t:
        return "U"

    return ""


# =========================
# ESI INTEGRATION (v6)
# =========================
ESI_TO_TRIAGE = {1: "RED", 2: "RED", 3: "YELLOW", 4: "GREEN", 5: "GREEN"}

ESI_LABELS = {
    1: "ESI 1 — Resuscitation",
    2: "ESI 2 — Emergent",
    3: "ESI 3 — Urgent",
    4: "ESI 4 — Less Urgent",
    5: "ESI 5 — Non-Urgent",
}


def evaluate_esi(esi_data: dict) -> dict:
    """
    Convert ESI assessment data into a triage result dict.
    Compatible with calculate_triage() output format.
    """
    lvl = esi_data.get("esi_level")
    if lvl is None:
        return None

    triage_color = ESI_TO_TRIAGE.get(lvl, "GREEN")
    label = ESI_LABELS.get(lvl, f"ESI {lvl}")

    problems = []
    reason = [label]

    if esi_data.get("life_threat"):
        problems.append("Immediate life-saving intervention required")

    for flag in esi_data.get("high_risk_flags", []):
        problems.append(flag)

    pain = esi_data.get("pain_score", 0)
    if pain >= 7:
        problems.append(f"Severe pain/distress (NRS {pain}/10)")
    elif pain >= 4:
        problems.append(f"Moderate pain (NRS {pain}/10)")

    for dz in esi_data.get("danger_zone_flags", []):
        problems.append(f"Danger zone vital: {dz}")

    resources = esi_data.get("resources", [])
    if resources:
        problems.append(f"Resources needed: {len(resources)}")

    if not problems and lvl >= 4:
        problems.append("Stable — minimal intervention needed")

    return {
        "triage": triage_color,
        "esi_level": lvl,
        "esi_label": label,
        "reason": reason,
        "score": 0,
        "flags": [],
        "problems": problems,
    }


# =========================
# MAIN ENTRY FUNCTION
# =========================
def calculate_triage(data: dict) -> dict:

    # =========================
    # 0. ESI FAST PATH (if ESI assessment was completed)
    # =========================
    esi_data = data.get("esi", {})
    if esi_data.get("esi_level") is not None:
        esi_result = evaluate_esi(esi_data)
        if esi_result:
            return esi_result

    result = {"triage": "GREEN", "reason": [], "score": 0, "flags": [], "problems": []}

    # =========================
    # 1. 🚨 IMMEDIATE DANGER (ABCDE PRIORITY)
    # =========================
    red, reason, problems = check_immediate_danger(data)
    if red:
        result["triage"] = "RED"
        result["reason"].append(reason)
        result["problems"].extend(problems)
        return result

    # =========================
    # 1.5 🧠 SPECIAL POPULATION (TIDAK DIUBAH)
    # =========================
    red, reason, problems = check_special_population(data)
    if red:
        result["triage"] = "RED"
        result["reason"].append(reason)
        result["problems"].extend(problems)
        return result
    else:
        result["problems"].extend(problems)

    # =========================
    # 2. ⚠️ ABCDE WARNING (UPGRADE)
    # =========================
    yellow, y_reason, y_problems = check_abcde_warning(data)
    if yellow:
        result["triage"] = "YELLOW"
        result["reason"].append(y_reason)
        result["problems"].extend(y_problems)

    # =========================
    # 3. CLINICAL FLAGS (TIDAK DIUBAH)
    # =========================
    flags, problems = check_clinical_flags(data)
    result["flags"] = flags
    result["problems"].extend(problems)

    # 🔥 EXTREME VITAL OVERRIDE (BARU)
    extreme_flags = [
        "Distres pernapasan berat",
        "Hipoksemia berat",
        "Takikardia ekstrem",
        "Bradikardia ekstrem",
        "Syok berat",
    ]

    matched = [f for f in flags if f in extreme_flags]
    if matched:
        result["triage"] = "RED"
        result["reason"].append(f"Critical vital: {', '.join(matched)}")
        result["problems"].extend(matched)
        return result

    # =========================
    # 4. SCORING (TIDAK DIUBAH)
    # =========================
    score, score_detail, score_problems = calculate_news_like_score(
        data.get("vital", {})
    )
    result["score"] = score
    result["reason"].extend(score_detail)
    result["problems"].extend(score_problems)

    # =========================
    # 🔥 HIPERTENSI BERAT RULE (BARU)
    # =========================
    v = data.get("vital", {})
    sbp = safe_val(v.get("td_sys"), 0)
    dbp = safe_val(v.get("td_dia"), 0)
    s = (data.get("symptoms") or "").lower()

    # 🟡 minimal YELLOW
    if sbp >= 180 or dbp >= 110:
        result["triage"] = max_triage(result["triage"], "YELLOW")
        result["reason"].append("Hipertensi berat")

    # 🔴 jika ada gejala
    if (sbp >= 180 or dbp >= 110) and any(
        x in s for x in ["nyeri dada", "sesak", "lemah separuh", "penurunan kesadaran"]
    ):
        result["triage"] = "RED"
        result["reason"].append("Hypertensive emergency")
        return result

    # 🔥 COMBINATION RULE (BARU)
    if result["triage"] == "GREEN":
        if score >= 3 and len(flags) >= 1:
            result["triage"] = "YELLOW"
            result["reason"].append("Combined risk (score + flag)")

    # =========================
    # 5. FINAL DECISION (TIDAK DIUBAH)
    # =========================
    if score >= 7:
        result["triage"] = "RED"
        result["reason"].append(f"High NEWS-like score ({score})")
        return result

    if score >= 4:
        result["triage"] = max_triage(result["triage"], "YELLOW")
        result["reason"].append(f"Moderate NEWS-like score ({score})")

    # 🔥 SMART FLAG LOGIC
    moderate_flags = [
        "Hipoksemia ringan",
        "Takikardia signifikan",
        "Hipotensi",
        "Hipertensi berat",
        "Demam tinggi",
    ]

    if any(f in flags for f in moderate_flags):
        result["triage"] = max_triage(result["triage"], "YELLOW")
        result["reason"].append("Moderate clinical risk")

    if result["triage"] == "GREEN":
        result["reason"].append("Stable condition")

    return result


# =========================
# 🚨 IMMEDIATE DANGER (UPGRADE ABCDE)
# =========================
def check_immediate_danger(data):

    v = data.get("vital", {})
    a = data.get("abcde", {})
    s = (data.get("symptoms") or "").lower()

    spo2 = safe_val(v.get("spo2"), 100)
    sbp = safe_val(v.get("td_sys"), 120)

    avpu = normalize_avpu(a.get("avpu"))

    airway = (a.get("airway") or "").lower()
    breathing = (a.get("breathing") or "").lower()
    circulation = (a.get("circulation") or "").lower()
    exposure = (a.get("exposure") or "").lower()

    # 🔴 AIRWAY (TIDAK DIUBAH)
    if "obstruksi" in airway or "obstructed" in airway or "snoring" in airway:
        return True, "Airway compromise", ["Gangguan jalan napas"]

    # 🔴 BREATHING (BARU)
    if "apnea" in breathing:
        return True, "Apnea", ["Apnea"]

    # 🔥 LEBIH ROBUST (TIDAK MUDAH MISS)
    if any(x in breathing for x in ["apnea", "distres", "sesak berat"]):
        return True, "Respiratory distress", ["Distres pernapasan"]

    if spo2 < 90:
        return True, "Severe hypoxia", ["Hipoksemia berat"]

    # 🔴 CIRCULATION (BARU)
    if any(x in circulation for x in ["syok", "shock"]):
        return True, "Shock", ["Syok"]

    if "perdarahan" in circulation:
        return True, "Active bleeding", ["Perdarahan aktif"]

    if sbp < 90:
        return True, "Shock", ["Syok / hipotensi"]

    # 🔴 DISABILITY (FIX)
    gcs = a.get("gcs")
    if gcs and gcs <= 8:
        return True, "Low GCS", ["Penurunan kesadaran"]

    # 🔴 EXPOSURE (BARU)
    if "luka bakar" in exposure:
        return True, "Burn injury", ["Luka bakar"]

    # 🔴 NEURO (TIDAK DIUBAH)
    neuro_terms = extract_neuro_terms(s)
    if neuro_terms:
        return True, "Neurological emergency", neuro_terms

    return False, None, []


# =========================
# 🟡 ABCDE WARNING (UPGRADE)
# =========================
def check_abcde_warning(data):

    v = data.get("vital", {})
    a = data.get("abcde", {})

    problems = []

    spo2 = safe_val(v.get("spo2"), 100)
    rr = safe_val(v.get("rr"), 16)

    avpu = normalize_avpu(a.get("avpu"))

    breathing = (a.get("breathing") or "").lower()
    circulation = (a.get("circulation") or "").lower()

    # 🟡 BREATHING
    if "dangkal" in breathing or "asimetris" in breathing:
        problems.append("Gangguan pernapasan")

    # 🟡 CIRCULATION
    if "nadi lemah" in circulation:
        problems.append("Perfusi buruk")

    # 🟡 DISABILITY
    if avpu == "V":
        problems.append("Penurunan kesadaran ringan")

    # 🟡 SUPPORT VITAL
    if spo2 < 94:
        problems.append("Hipoksemia ringan")

    if rr > 20:
        problems.append("Takipnea ringan")

    if problems:
        return True, "ABCDE warning", problems

    return False, None, []


# =========================
# 🧠 SPECIAL POPULATION (TIDAK DIUBAH)
# =========================
def check_special_population(data):

    kategori = (data.get("kategori") or "").lower()
    s = (data.get("symptoms") or "").lower()

    problems = []

    if "hamil" in kategori:

        if "perdarahan" in s:
            return True, "Obstetric emergency", ["Perdarahan pada kehamilan"]

        if "kejang" in s:
            return True, "Eclampsia risk", ["Kejang pada kehamilan"]

        if "tidak gerak janin" in s:
            return True, "Fetal distress", ["Gerak janin berkurang"]

        if "kenceng" in s or "kontraksi" in s:
            problems.append("Kontraksi uterus (observasi)")

    if "bayi" in kategori or "anak" in kategori:

        if "kejang" in s:
            return True, "Pediatric emergency", ["Kejang"]

        if "tidak mau minum" in s:
            problems.append("Tidak mau minum")

        if "sesak" in s:
            problems.append("Gangguan napas (anak)")

    if problems:
        return False, None, problems

    return False, None, []


# =========================
# CLINICAL FLAGS (TIDAK DIUBAH)
# =========================
def check_clinical_flags(data):

    v = data.get("vital", {})
    s = (data.get("symptoms") or "").lower()

    flags = []
    problems = []

    sbp = safe_val(v.get("td_sys"), 0)
    dbp = safe_val(v.get("db_dia"), 0)

    if sbp >= 180 or dbp >= 110:
        flags.append("Hipertensi berat")
        problems.append("Hipertensi berat")

    if "nyeri dada" in s:
        flags.append("Cardiac risk")
        problems.append("Nyeri dada")

    neuro_terms = extract_neuro_terms(s)
    if neuro_terms:
        flags.append("Neurological deficit")
        problems.extend(neuro_terms)

    return flags, problems


# =========================
# NEURO (TIDAK DIUBAH)
# =========================
def extract_neuro_terms(text: str):

    problems = []

    if "lemah separuh" in text or "tidak bisa menggerakkan satu sisi" in text:
        problems.append("Hemiparesis")

    if "tidak bisa gerak sama sekali" in text:
        problems.append("Hemiplegia")

    if "bicara pelo" in text or "bicara tidak jelas" in text:
        problems.append("Disartria")

    if "tidak bisa bicara" in text or "afasia" in text:
        problems.append("Afasia")

    return problems


# =========================
# NEWS-LIKE SCORING (TIDAK DIUBAH)
# =========================
def calculate_news_like_score(v):

    score = 0
    detail = []
    problems = []

    rr = safe_val(v.get("rr"), 16)
    spo2 = safe_val(v.get("spo2"), 98)
    sbp = safe_val(v.get("td_sys"), 120)
    hr = safe_val(v.get("nadi"), 80)
    temp = safe_val(v.get("suhu"), 36.5)

    # RR (UNIFIED LABEL)
    if rr >= 21:
        problems.append("Takipnea ringan")

    if rr >= 25:
        score += 3
        detail.append("RR ≥ 25")
    elif rr >= 21:
        score += 2

    if spo2 <= 91:
        score += 3
        problems.append("Hipoksemia")

    elif spo2 <= 94:
        score += 2
        problems.append("Hipoksemia ringan")

    if sbp >= 180:
        score += 3
        problems.append("Hipertensi Berat")

    if sbp <= 90:
        score += 3
        problems.append("Hipotensi")

    if hr >= 130:
        score += 3
        problems.append("Takikardia")

    elif hr <= 40:
        score += 3
        problems.append("Bradikardia")

    if temp >= 39:
        score += 2
        problems.append("Hipertermia")

    elif temp <= 35:
        score += 3
        problems.append("Hipotermia")

    return score, detail, problems


# =========================
# HELPER (TIDAK DIUBAH)
# =========================
def max_triage(current, new):

    priority = {"GREEN": 1, "YELLOW": 2, "RED": 3}

    return new if priority[new] > priority[current] else current
