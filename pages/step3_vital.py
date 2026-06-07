from nicegui import ui, app
from utils.mobile_layout import mobile_container
from session_state import get_patient
from utils.vital_engine import interpret_vital

from components.header_triase import header_triase
from components.progress_bar import progress_bar
from components.ui_system import glass_container


def is_abnormal(text):
    if not text:
        return False
    text = text.lower()
    return not ("normal" in text or "dalam batas" in text)


def set_color(label, text):
    if not text:
        label.text = ""
        return

    if "normal" in text.lower():
        label.classes(replace="text-green-600")
    else:
        label.classes(replace="text-red-600")

    label.text = text


def step3_page():

    if app.storage.user.get("current_step", 1) < 3:
        ui.navigate.to("/step2")
        return

    patient = get_patient()
    vital = patient.get("vital", {})

    header_triase()

    with mobile_container():

        progress_bar(current_step=3, total_step=5)

        # ======================
        # STYLE CARD (SAMA STEP 2)
        # ======================
        CARD = """
        w-full rounded-2xl p-3
        backdrop-blur-xl bg-white/60
        border border-white/30
        shadow-[0_10px_30px_rgba(0,0,0,0.08)]
        """

        GRID = "w-full items-center gap-1"
        LABEL = "text-xs text-gray-500"
        INPUT = "w-full text-gray-800 text-sm"
        INFO = "text-xs break-words"

        with glass_container():

            ui.label("Vital Signs").classes(
                "text-2xl font-bold text-center w-full text-slate-700 mb-0"
            )

            # ======================
            # BB / TB
            # ======================
            ui.label("⚖️ Berat Badan").classes("text-sm font-semibold mt-2")

            with ui.grid(columns="90px 70px 1fr").classes(GRID):
                ui.label("BB (kg)").classes(LABEL)
                bb = ui.number(value=vital.get("bb")).classes(INPUT)
                bb_info = ui.label("").classes(INFO)

            with ui.grid(columns="90px 70px 1fr").classes(GRID):
                ui.label("TB (cm)").classes(LABEL)
                tb = ui.number(value=vital.get("tb")).classes(INPUT)
                tb_info = ui.label("").classes(INFO)

            ui.separator().classes("my-2")

            # ======================
            # TD
            # ======================
            ui.label("🫀 Tekanan Darah").classes("text-sm font-semibold")

            with ui.grid(columns="90px 70px 1fr").classes(GRID):
                ui.label("Sistolik").classes(LABEL)
                td_sys = ui.number(value=vital.get("td_sys")).classes(INPUT)
                td_info = ui.label("").classes(INFO)

            with ui.grid(columns="90px 70px 1fr").classes(GRID):
                ui.label("Diastolik").classes(LABEL)
                td_dia = ui.number(value=vital.get("td_dia")).classes(INPUT)
                ui.label("")

            ui.separator().classes("my-2")

            # ======================
            # NADI
            # ======================
            ui.label("❤️ Nadi").classes("text-sm font-semibold")

            with ui.grid(columns="90px 70px 1fr").classes(GRID):
                ui.label("Nadi").classes(LABEL)
                nadi = ui.number(value=vital.get("nadi")).classes(INPUT)
                nadi_info = ui.label("").classes(INFO)

            ui.separator().classes("my-2")

            # ======================
            # RR
            # ======================
            ui.label("🌬️ RR").classes("text-sm font-semibold")

            with ui.grid(columns="90px 70px 1fr").classes(GRID):
                ui.label("RR").classes(LABEL)
                rr = ui.number(value=vital.get("rr")).classes(INPUT)
                rr_info = ui.label("").classes(INFO)

            ui.separator().classes("my-2")

            # ======================
            # SUHU
            # ======================
            ui.label("🌡️ Suhu").classes("text-sm font-semibold")

            with ui.grid(columns="90px 70px 1fr").classes(GRID):
                ui.label("Suhu").classes(LABEL)
                suhu = ui.number(value=vital.get("suhu")).classes(INPUT)
                suhu_info = ui.label("").classes(INFO)

            ui.separator().classes("my-2")

            # ======================
            # SPO2
            # ======================
            ui.label("🩸 SpO2").classes("text-sm font-semibold")

            with ui.grid(columns="90px 70px 1fr").classes(GRID):
                ui.label("SpO2").classes(LABEL)
                spo2 = ui.number(value=vital.get("spo2")).classes(INPUT)
                spo2_info = ui.label("").classes(INFO)

        # ======================
        # INTERPRETASI
        # ======================
        def update_interpretasi():

            data = {
                "td_sys": td_sys.value,
                "nadi": nadi.value,
                "rr": rr.value,
                "suhu": suhu.value,
                "spo2": spo2.value,
                "bb": bb.value,
                "tb": tb.value,
            }

            hasil = interpret_vital(data, patient)

            set_color(td_info, hasil.get("td"))
            set_color(nadi_info, hasil.get("nadi"))
            set_color(rr_info, hasil.get("rr"))
            set_color(suhu_info, hasil.get("suhu"))
            set_color(spo2_info, hasil.get("spo2"))
            set_color(bb_info, hasil.get("bb"))

        for comp in [td_sys, nadi, rr, suhu, spo2, bb, tb]:
            comp.on("update:model-value", lambda e: update_interpretasi())

        update_interpretasi()

        # ======================
        # SAVE
        # ======================
        def save_vital():

            data = {
                "td_sys": td_sys.value,
                "td_dia": td_dia.value,
                "nadi": nadi.value,
                "rr": rr.value,
                "suhu": suhu.value,
                "spo2": spo2.value,
                "bb": bb.value,
                "tb": tb.value,
            }

            patient["vital"] = data

            hasil = interpret_vital(data, patient)

            masalah = []
            for key, v in hasil.items():
                if isinstance(v, list):
                    for item in v:
                        if is_abnormal(item):
                            masalah.append(item)
                else:
                    if is_abnormal(v):
                        masalah.append(v)

            patient["masalah_vital"] = list(set(masalah))

            ui.notify("Vital tersimpan", color="positive")

        # ======================
        # BUTTON (SAMA STEP 2)
        # ======================
        with ui.grid(columns=3).classes("w-full max-w-sm mx-auto gap-2 mt-2"):

            # BACK
            with ui.element("div").classes(
                "flex-1 text-center rounded-xl cursor-pointer overflow-hidden"
            ).style(
                """
                background: rgba(230,235,255,0.35);
                backdrop-filter: blur(16px) saturate(180%);
                border: 1px solid rgba(120,140,255,0.25);
                box-shadow:
                    0 6px 18px rgba(80,100,255,0.15),
                    inset 0 1px 0 rgba(255,255,255,0.4);
            """
            ).on(
                "click", lambda: ui.navigate.to("/step2")
            ):

                ui.label("Back").classes(
                    "py-2 text-slate-800 font-semibold text-sm w-full"
                )

            # SAVE
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
                "click", save_vital
            ):

                ui.label("Save").classes("py-2 text-white font-semibold text-sm w-full")

            # NEXT
            def next_step():
                save_vital()
                app.storage.user["current_step"] = 4
                ui.navigate.to("/step4")

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
                "click", next_step
            ):

                ui.label("Next").classes("py-2 text-white font-semibold text-sm w-full")
