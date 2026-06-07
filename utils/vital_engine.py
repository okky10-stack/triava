from datetime import datetime


# ======================
# AGE GROUP (BERDASARKAN TTL)
# ======================
def get_age_group(patient):
    try:
        ttl = patient.get("ttl")

        if not ttl:
            return "dewasa"

        lahir = datetime.strptime(ttl, "%d/%m/%Y")
        today = datetime.today()
        days = (today - lahir).days

        if days < 28:
            return "neonatus"
        elif days < 365:
            return "bayi"
        elif days < 5 * 365:
            return "balita"
        elif days < 12 * 365:
            return "anak"
        else:
            return "dewasa"

    except:
        return "dewasa"


# ======================
# HITUNG UMUR NUMERIK
# ======================
def get_age_numeric(patient):
    try:
        ttl = patient.get("ttl")
        if not ttl:
            return 0, 0

        lahir = datetime.strptime(ttl, "%d/%m/%Y")
        today = datetime.today()

        days = (today - lahir).days
        bulan = days // 30
        tahun = days // 365

        return tahun, bulan
    except:
        return 0, 0


# ======================
# NADI (AGE ADJUSTED)
# ======================
def interpret_nadi(nadi, age_group):

    if nadi is None:
        return ""

    if age_group == "neonatus":
        low, high = 100, 180
    elif age_group == "bayi":
        low, high = 100, 160
    elif age_group == "balita":
        low, high = 90, 140
    elif age_group == "anak":
        low, high = 70, 120
    else:
        low, high = 60, 100

    if nadi < low:
        return "Bradikardia"
    elif low <= nadi <= high:
        return "Normal"
    elif nadi <= high + 20:
        return "Takikardia Ringan"
    elif nadi <= 130:
        return "Takikardia"
    else:
        return "Takikardia berat"


# ======================
# RR (BERDASARKAN IDAI / WHO)
# ======================
def interpret_rr(rr, age_group):

    if rr is None:
        return ""

    # ======================
    # 👶 PEDIATRIK (WHO)
    # ======================
    if age_group == "neonatus":
        normal_max = 60
    elif age_group == "bayi":
        normal_max = 50
    elif age_group == "balita":
        normal_max = 40
    elif age_group == "anak":
        normal_max = 30

    # ======================
    # 👨 DEWASA (MODIFIED EWS)
    # ======================
    else:
        if rr < 12:
            return "Bradipnea"
        elif 12 <= rr <= 20:
            return "Normal"
        elif 21 <= rr <= 24:
            return "Takipnea ringan"
        elif 25 <= rr <= 30:
            return "Takipnea"   
        else:
            return "Distres pernapasan"

    # ======================
    # PEDIATRIC LOGIC
    # ======================
    if rr < 20:
        return "Bradipnea"
    elif rr <= normal_max:
        return "Normal"
    elif rr <= normal_max + 10:
        return "Takipnea"
    else:
        return "Distres pernapasan"


# ======================
# SPO2
# ======================
def interpret_spo2(spo2):

    if spo2 is None:
        return ""

    if spo2 >= 95:
        return "Normal"
    elif 92 <= spo2 < 95:
        return "Hipoksemia ringan"
    elif 90 <= spo2 < 92:
        return "Hipoksemia"
    else:
        return "Hipoksemia berat"


# ======================
# SUHU
# ======================
def interpret_suhu(suhu):

    if suhu is None:
        return ""

    if suhu < 36:
        return "Hipotermia"
    elif 36 <= suhu <= 37.5:
        return "Normal"
    elif 37.5 < suhu <= 38:
        return "Subfebris"
    elif 38 < suhu <= 39:
        return "Demam"
    else:
        return "Demam tinggi"


# ======================
# TEKANAN DARAH (DEWASA)
# ======================
def interpret_td(sys):

    if sys < 90:
        return "Hipotensi"

    elif sys < 130:
        return "Normal"

    elif 130 <= sys < 140:
        return "Tekanan Darah Tinggi (Prehipertensi)"
    
    elif 140 <= sys < 180:
        return "Hipertensi"

    if sys >= 180:
        return "Hipertensi Berat"


# ======================
# BB (ANAK vs DEWASA)
# ======================
def interpret_bb(bb, patient, tb=None):

    if bb is None:
        return ""

    try:
        tahun, bulan = get_age_numeric(patient)

        # ======================
        # 👶 ANAK (< 12 tahun)
        # ======================
        if tahun < 12:

            if bulan < 12:
                bb_median = (bulan / 2) + 4
            elif tahun <= 5:
                bb_median = (tahun * 2) + 8
            else:
                bb_median = (tahun * 3) + 7

            if bb_median <= 0:
                return ""

            ratio = bb / bb_median

            if ratio < 0.6:
                return "BB sangat kurang"
            elif ratio < 0.75:
                return "BB kurang"
            elif ratio <= 1.25:
                return "Normal"
            elif ratio <= 1.4:
                return "Risiko overweight"
            else:
                return "Obesitas"

        # ======================
        # 👨 DEWASA (>= 12 tahun)
        # ======================
        else:

            if not tb:
                return "Perlu TB untuk evaluasi BB"

            tinggi_m = tb / 100
            bmi = bb / (tinggi_m**2)

            if bmi < 18.5:
                return f"Underweight (BMI {bmi:.1f})"
            elif bmi < 25:
                return f"Normal (BMI {bmi:.1f})"
            elif bmi < 30:
                return f"Overweight (BMI {bmi:.1f})"
            else:
                return f"Obesitas (BMI {bmi:.1f})"

    except:
        return ""


# ======================
# TRIAGE FLAGS (NEW)
# ======================
def generate_triage_flags(vital, patient=None):

    flags = []

    try:
        nadi = vital.get("nadi")
        rr = vital.get("rr")
        spo2 = vital.get("spo2")
        suhu = vital.get("suhu")
        sys = vital.get("td_sys")
        bb = vital.get("bb")
        tb = vital.get("tb")

        # RESPIRATORY
        if spo2 is not None:
            if spo2 < 90:
                flags.append("Hipoksemia berat")
            elif spo2 < 95:
                flags.append("Hipoksemia ringan")

        if rr is not None:
            if rr >= 35:
                flags.append("Distres pernapasan berat")
            elif rr >30:
                flags.append("Distres pernapasan")

        # CARDIO
        if sys is not None:
            if sys < 80:
                flags.append("Hipotensi berat")
            elif sys < 90:
                flags.append("Hipotensi")
            elif sys > 180:
                flags.append("Hipertensi berat")

        if nadi is not None:
            if nadi >= 150:
                flags.append("Takikardia ekstrem")
            elif nadi > 130:
                flags.append("Takikardia signifikan")
            elif nadi < 40:
                flags.append("Bradikardia ekstrem")
            elif nadi < 50:
                flags.append("Bradikardia signifikan")

        # SUHU
        if suhu is not None:
            if suhu >= 39:
                flags.append("Demam tinggi")
            elif suhu < 36:
                flags.append("Hipotermia")

        # BMI FLAG (DEWASA)
        if patient:
            tahun, _ = get_age_numeric(patient)

            if tahun >= 12 and bb and tb:
                tinggi_m = tb / 100
                bmi = bb / (tinggi_m**2)

                if bmi < 18.5:
                    flags.append("Underweight (risiko malnutrisi)")

        return flags

    except:
        return []


# ======================
# MAIN ENGINE
# ======================
def interpret_vital(vital, patient=None):

    if not vital:
        return {}

    age_group = "dewasa"
    if patient:
        age_group = get_age_group(patient)

    return {
        "nadi": interpret_nadi(vital.get("nadi"), age_group),
        "rr": interpret_rr(vital.get("rr"), age_group),
        "spo2": interpret_spo2(vital.get("spo2")),
        "suhu": interpret_suhu(vital.get("suhu")),
        "td": interpret_td(vital.get("td_sys")),
        "bb": interpret_bb(vital.get("bb"), patient, vital.get("tb")),
        "flags": generate_triage_flags(vital, patient),
    }
