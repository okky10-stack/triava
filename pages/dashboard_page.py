from nicegui import ui, app
from utils.mobile_layout import mobile_container
from session_state import clear_patient
from datetime import datetime
from database import get_triage_counts

from components.header_triase import header_triase
from components.ui_system import glass_container


# ======================
# BUTTON KHUSUS DASHBOARD (FIX)
# ======================
def btn_primary(label, on_click):
    with ui.element("div").classes("flex-1"):

        with ui.element("div").classes(
            "min-h-[42px] w-full flex items-center justify-center text-center rounded-xl overflow-hidden cursor-pointer relative"
        ).style(
            """
            background: linear-gradient(145deg, #6A00FF, #3F00CC);
            box-shadow:
                0 10px 25px rgba(106,0,255,0.4),
                inset 0 2px 0 rgba(255,255,255,0.3);
            transition: all 0.15s ease;
            """
        ).on(
            "click", lambda e: on_click()
        ).on(
            "mousedown", lambda e: e.sender.style("transform: scale(0.94)")
        ).on(
            "mouseup", lambda e: e.sender.style("transform: scale(1)")
        ):

            ui.label(label).classes("py-2 text-white font-semibold text-sm w-full")

            # highlight layer
            ui.element("div").style(
                """
                position:absolute;
                top:0; left:0;
                width:100%; height:35%;
                background: linear-gradient(
                    to bottom,
                    rgba(255,255,255,0.35),
                    transparent
                );
                pointer-events: none;
                """
            )

def dashboard_page():

    # ======================
    # HEADER
    # ======================
    header_triase()

    # ======================
    # MAIN CONTENT
    # ======================
    with mobile_container().classes("items-center px-4"):

        def new_patient():
            clear_patient()
            app.storage.user["current_step"] = 1
            ui.navigate.to("/step1")

        # ======================
        # BUTTON ROW (FIX TOTAL)
        # ======================
        with ui.column().classes("w-full max-w-sm mx-auto"):
            with ui.row().classes("w-full gap-2 mt-2"):

                btn_primary("Riwayat Pasien", lambda: ui.navigate.to("/history"))

                btn_primary("Pasien Baru", lambda: new_patient())

        # ======================
        # GLASS DASHBOARD
        # ======================
        with glass_container():

            # ===== TITLE =====
            ui.label("Dashboard Triase").classes("text-xl font-bold w-full text-center")

            tanggal_label = ui.label().classes(
                "text-xs text-gray-500 w-full text-center mb-3"
            )

            # ======================
            # WAKTU
            # ======================
            hari_map = {
                "Monday": "Senin",
                "Tuesday": "Selasa",
                "Wednesday": "Rabu",
                "Thursday": "Kamis",
                "Friday": "Jumat",
                "Saturday": "Sabtu",
                "Sunday": "Minggu",
            }

            bulan_map = {
                "January": "Januari",
                "February": "Februari",
                "March": "Maret",
                "April": "April",
                "May": "Mei",
                "June": "Juni",
                "July": "Juli",
                "August": "Agustus",
                "September": "September",
                "October": "Oktober",
                "November": "November",
                "December": "Desember",
            }

            def update_waktu():
                now = datetime.now()
                hari = hari_map[now.strftime("%A")]
                bulan = bulan_map[now.strftime("%B")]
                tanggal_label.set_text(
                    f"{hari}, {now.day} {bulan} {now.year} • {now.strftime('%H:%M')}"
                )

            update_waktu()
            ui.timer(1.0, update_waktu)

            # ======================
            # TRIAGE CARDS
            # ======================
            with ui.card().classes(
                """
                relative w-full mt-2 p-4 rounded-2xl shadow-md
                bg-gradient-to-br from-red-400 to-red-500 text-black
            """
            ):
                ui.label("✱").classes("absolute right-4 top-3 text-6xl opacity-20")
                ui.label("GAWAT DARURAT").classes(
                    "text-xs bg-white/20 px-3 text-bold py-1 rounded-full w-fit mb-1"
                )
                merah_label = ui.label("0").classes("text-3xl font-bold")
                ui.label("MERAH").classes("text-sm text-bold opacity-90")

            with ui.card().classes(
                """
                relative w-full mt-2 p-4 rounded-2xl shadow-sm
                bg-gradient-to-br from-yellow-200 to-yellow-300 text-gray-800
            """
            ):
                ui.label("✱").classes("absolute right-4 top-3 text-5xl opacity-20")
                ui.label("DARURAT").classes(
                    "text-xs bg-white/40 px-3 py-1 text-bold rounded-full w-fit mb-1"
                )
                kuning_label = ui.label("0").classes("text-3xl font-bold")
                ui.label("KUNING").classes("text-sm text-bold opacity-90")

            with ui.card().classes(
                """
                relative w-full mt-2 p-4 rounded-2xl shadow-sm
                bg-gradient-to-br from-green-200 to-green-300 text-gray-800
            """
            ):
                ui.label("✱").classes("absolute right-4 top-3 text-5xl opacity-20")
                ui.label("STABIL").classes(
                    "text-xs bg-white/40 px-3 py-1 rounded-full text-bold w-fit mb-1"
                )
                hijau_label = ui.label("0").classes("text-3xl font-bold")
                ui.label("HIJAU").classes("text-sm text-bold opacity-90")

        # ======================
        # COUNTS
        # ======================
        def update_counts():
            user_id = app.storage.user.get("email")

            if not user_id:
                h, k, m = 0, 0, 0
            else:
                try:
                    h, k, m = get_triage_counts(user_id)
                except:
                    h, k, m = 0, 0, 0

            hijau_label.set_text(str(h))
            kuning_label.set_text(str(k))
            merah_label.set_text(str(m))

        update_counts()
        ui.timer(2.0, update_counts)
