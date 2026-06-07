from nicegui import ui, app
from utils.mobile_layout import mobile_container
from session_state import get_patient
from datetime import datetime
import calendar

# ===== IMPORT COMPONENT =====
from components.header_triase import header_triase
from components.progress_bar import progress_bar

# ✅ TAMBAHAN UI SYSTEM
from components.ui_system import glass_container, glass_card, btn_primary, btn_secondary

# ======================
# FORMAT TANGGAL
# ======================
def format_tanggal(text):
    if len(text) == 8 and text.isdigit():
        return f"{text[:2]}/{text[2:4]}/{text[4:]}"
    return text


def format_tanggal_live(text):
    angka = "".join(filter(str.isdigit, text))

    if len(angka) <= 2:
        return angka
    elif len(angka) <= 4:
        return f"{angka[:2]}/{angka[2:]}"
    else:
        return f"{angka[:2]}/{angka[2:4]}/{angka[4:8]}"


# ======================
# HITUNG UMUR DETAIL
# ======================
def hitung_umur_detail(ttl):
    try:
        lahir = datetime.strptime(ttl, "%d/%m/%Y")
        today = datetime.today()

        tahun = today.year - lahir.year
        bulan = today.month - lahir.month
        hari = today.day - lahir.day

        if hari < 0:
            bulan -= 1
            last_month = (today.month - 1) or 12
            last_year = today.year if today.month != 1 else today.year - 1
            hari += calendar.monthrange(last_year, last_month)[1]

        if bulan < 0:
            tahun -= 1
            bulan += 12

        if tahun == 0:
            return f"{bulan} bulan {hari} hari"
        elif bulan == 0:
            return f"{tahun} tahun {hari} hari"
        else:
            return f"{tahun} tahun {bulan} bulan {hari} hari"

    except:
        return ""


def is_valid_date(text):
    try:
        datetime.strptime(text, "%d/%m/%Y")
        return True
    except:
        return False


def step1_page():

    patient = get_patient()

    # ======================
    # HEADER (STICKY)
    # ======================
    header_triase()

    # ======================
    # CONTENT
    # ======================
    with mobile_container():
        progress_bar(current_step=1, total_step=5)

        # 🔥 MASTER GLASS CONTAINER
        with glass_container():

            ui.label("Identitas").classes("text-2xl font-bold text-center w-full mt-1")

            # ===== CARD PETUGAS =====

            ui.label("Petugas Pemeriksa").classes(
                "text-lg font-semibold text-blue-600"
            )

            petugas = (
                ui.input(
                    "Nama Petugas",
                    value=patient.get("petugas", ""),
                    placeholder="Dokter / Perawat",
                )
                .props("clearable")
                .classes("w-full rounded-xl")
                )

            ui.label("Data Pasien").classes(
                "text-lg font-semibold text-gray-700"
            )

            nama = (
                ui.input("Nama", value=patient.get("nama", ""), placeholder="Nama lengkap pasien")
                .props("clearable")
                .classes("w-full rounded-xl")
            )

            with ui.row().classes("w-full justify-center"):
                jenis_kelamin = ui.radio(["Laki-laki", "Perempuan"],
                        value=patient.get("jenis_kelamin") or None,
                ).props("inline")

            ttl = (
                ui.input(
                    "Tanggal Lahir",
                    value=patient.get("ttl", ""),
                    placeholder="ddmmyyyy",
                )
                .props("clearable inputmode='numeric' maxlength=10 autocomplete='off'")
                .classes("w-full rounded-xl")
            )

            umur = (
                ui.input(
                    "Umur (otomatis)",
                    value=patient.get("umur", ""),
                )
                .props("readonly")
                .classes("w-full rounded-xl italic bg-gray-100")
                )

            alamat = (
                ui.input("Alamat / Ruang", value=patient.get("alamat", ""))
                .props("clearable")
                .classes("w-full rounded-xl")
            )

            hp = (
                ui.input("Nomor HP", value=patient.get("hp", ""))
                .props('inputmode="numeric" clearable')
                .classes("w-full rounded-xl")
            )

            # ======================
            # AUTO HITUNG UMUR
            # ======================
            def update_umur():
                formatted = format_tanggal(ttl.value)
                umur.value = hitung_umur_detail(formatted)

            def on_ttl_input(e):
                raw = e.sender.value or ""
                angka = ''.join(filter(str.isdigit, raw))[:8]

                formatted = ""

                # 🔥 BUILD STEP BY STEP (BIAR KELIHATAN KETIK)
                for i, c in enumerate(angka):
                    if i == 2 or i == 4:
                        formatted += "/"
                    formatted += c

                # 🔥 FORCE UPDATE TANPA JUMP
                if e.sender.value != formatted:
                    e.sender.set_value(formatted)

                # 🔥 AUTO UMUR
                if len(angka) == 8:
                    umur.value = hitung_umur_detail(formatted)
                else:
                    umur.value = ""

            ttl.on("blur", lambda e: update_umur())
            ttl.on("input", on_ttl_input)
            ttl.on("change", on_ttl_input)

            # ======================
            # NEXT STEP
            # ======================
            def next_step():
                # ======================
                # VALIDASI WAJIB
                # ======================
                if not petugas.value:
                    ui.notify("Petugas pemeriksa wajib diisi", color="negative")
                    return  

                if not nama.value:
                    ui.notify("Nama pasien wajib diisi", color="negative")
                    return

                if not jenis_kelamin.value:
                    ui.notify("Jenis kelamin wajib dipilih", color="negative")
                    return

                if not ttl.value:
                    ui.notify("Tanggal lahir wajib diisi", color="negative")
                    return

                angka = ''.join(filter(str.isdigit, ttl.value))
                if len(angka) != 8:
                    ui.notify("Tanggal lahir harus terdiri dari 8 digit (ddmmyyyy)", color="negative")
                    return
                formatted = f"{angka[:2]}/{angka[2:4]}/{angka[4:]}"

                if not is_valid_date(formatted):
                    ui.notify("Tanggal lahir tidak valid", color="negative")
                    return
                ttl.value = formatted  # pastikan format benar

                if not alamat.value:
                    ui.notify("Alamat wajib diisi", color="negative")
                    return

                patient["petugas"] = petugas.value
                patient["nama"] = nama.value
                patient["jenis_kelamin"] = jenis_kelamin.value
                patient["ttl"] = ttl.value
                patient["umur"] = umur.value
                patient["alamat"] = alamat.value
                patient["hp"] = hp.value

                app.storage.user["current_step"] = 2

                ui.navigate.to("/step2")

            # ======================
            # BUTTON
            # ======================
            with ui.row().classes("w-full gap-2 mt-4"):

                btn_secondary("Back", lambda: ui.navigate.to("/dashboard"), "gray")

                btn_primary("Next", next_step)
