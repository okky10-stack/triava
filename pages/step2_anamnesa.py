from nicegui import ui, app
from utils.mobile_layout import mobile_container
from session_state import get_patient
from ai_engine import analyze_keluhan

from components.header_triase import header_triase
from components.progress_bar import progress_bar
from components.ui_system import glass_container


def step2_page():

    # GUARD
    if app.storage.user.get("current_step", 1) < 2:
        ui.navigate.to("/step1")
        return

    patient = get_patient()

    # ======================
    # HEADER
    # ======================
    header_triase()

    # ======================
    # CONTENT
    # ======================
    with mobile_container():

        progress_bar(current_step=2, total_step=5)


        # ======================
        # 🔥 GLASS CONTAINER (MAIN)
        # ======================
        with glass_container():
            ui.label("Anamnesa").classes(
            "text-2xl font-bold text-center w-full text-slate-700 mb-0"
        )
            # ======================
            # KATEGORI PASIEN
            # ======================
            ui.label("Kategori Pasien").classes("text-sm text-gray-500")

            kategori = ui.select(
                ["Umum", "Ibu Hamil", "Postpartum", "Bayi/Anak"],
                value=patient.get("kategori", "Umum"),
            ).classes("w-full mt-1")


            # ======================
            # KELUHAN
            # ======================
            ui.label("Keluhan Utama").classes("text-sm text-gray-500")

            keluhan = ui.input(placeholder="Contoh: Nyeri dada sejak 2 jam").classes(
                "w-full text-gray-800 mt-1"
            )


            # ======================
            # AI
            # ======================
            ui.label("AI Clinical Assistant").classes(
                "text-sm font-semibold text-indigo-800 py-0"
            )

            ui.label("Pertanyaan Pelengkap").classes("text-[11px] text-gray-400")

            ai_output = ui.markdown("").classes(
                "w-full text-sm max-h-32 overflow-y-auto mt-1"
            )

            def analisis_ai():
                if not keluhan.value:
                    ui.notify("Isi keluhan utama dulu", color="warning")
                    return

                hasil = analyze_keluhan(keluhan.value, kategori=kategori.value)
                ai_output.set_content(hasil)

                resume.value = f"""Keluhan utama:
{keluhan.value}

Anamnesa:
"""

            # 🔥 BUTTON PRIMARY
            with ui.element("div").classes(
                "w-full text-center rounded-xl cursor-pointer overflow-hidden mt-0"
            ).style(
                """
                background: linear-gradient(145deg, #6A00FF, #3F00CC);
                box-shadow:
                    0 10px 25px rgba(106,0,255,0.4),
                    inset 0 2px 0 rgba(255,255,255,0.3);
                """
            ).on(
                "click", analisis_ai
            ):

                ui.label("✨ Generate Pertanyaan").classes(
                    "py-2 text-white font-semibold text-sm w-full"
                )

            # DISCLAIMER
            ui.label(
                "AI dapat melakukan kesalahan. Gunakan sebagai rekomendasi tambahan."
            ).classes("text-[11px] text-gray-400 text-center w-full mt-0")

            ui.separator().classes("my-0")

            # ======================
            # RESUME
            # ======================
            ui.label("Resume Anamnesa").classes("text-sm text-gray-500")

            resume = ui.textarea().classes("w-full min-h-[150px] mt-0")

        # ======================
        # ACTION (TETAP)
        # ======================
        with ui.grid(columns=3).classes("w-full max-w-sm mx-auto gap-2 mt-2"):

            def save_data():
                patient["keluhan"] = keluhan.value
                patient["resume_anamnesa"] = resume.value
                patient["symptoms"] = (keluhan.value or "").lower()
                patient["kategori"] = kategori.value
                ui.notify("Anamnesa tersimpan", color="positive")

            def go_next():
                save_data()
                app.storage.user["current_step"] = 3
                ui.navigate.to("/step3")

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
                "click", lambda: ui.navigate.to("/step1")
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
                "click", save_data
            ):

                ui.label("Save").classes("py-2 text-white font-semibold text-sm w-full")

            # NEXT
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
                "click", go_next
            ):

                ui.label("Next").classes("py-2 text-white font-semibold text-sm w-full")
