from nicegui import ui, app
from datetime import datetime


# ======================
# HELPER EXPIRED
# ======================
def get_expired_label():
    expiry = app.storage.user.get('expired_at')

    if not expiry:
        return "Expired: -"

    try:
        expiry_ts = float(expiry)
        delta = int((expiry_ts - datetime.now().timestamp()) / 86400)

        if delta < 0:
            return "Expired"
        elif delta == 0:
            return "Expired hari ini"
        else:
            return f"Expired: {delta} hari"

    except:
        return "Expired: -"


def header_triase():

    # ======================
    # ABOUT DIALOG
    # ======================
    with ui.dialog() as about_dialog:
        with ui.card().classes("""
            w-72 p-4 rounded-2xl shadow-xl
            bg-white text-center
        """):

            ui.label("TRIAVA")\
                .classes("text-lg font-bold text-gray-800 w-full")

            ui.label(
                "Triava adalah aplikasi clinical triage system yang membantu tenaga kesehatan dalam penilaian awal pasien secara cepat dan terstruktur."
            ).classes("text-sm text-gray-600 mt-2")

            ui.label("© Triava System")\
                .classes("text-xs text-gray-400 mt-3 w-full")

    # ======================
    # STICKY HEADER (MOBILE WIDTH)
    # ======================
    with ui.column().classes("""
        sticky top-0 z-50
        w-full flex items-center
        bg-white/0 backdrop-blur-md
    """):

        # wrapper mobile (ini kunci supaya tidak full layar)
        with ui.column().classes("w-full max-w-md mx-auto"):

            with ui.row().classes("""
                w-full items-center justify-between
                px-2 py-1 mt-1
            """):

                # LEFT
                with ui.row().classes("items-center gap-2"):
                    ui.image("/static/icon-192.png").classes("w-6 h-6 rounded-lg")
                    with ui.column().classes("gap-0"):
                        ui.label("TRIAVA")\
                            .classes("text-base font-bold text-gray-800 tracking-wide")
                        ui.label("Triage Assistant App")\
                            .classes("text-[10px] text-gray-500 -mt-1")
                # RIGHT MENU
                with ui.button(icon='menu')\
                    .props('flat round dense')\
                    .classes("text-gray-700"):

                    with ui.menu():

                        ui.label(app.storage.user.get('email', 'User'))\
                            .classes("px-4 pt-2 text-sm font-semibold text-gray-800")

                        # 🔥 EXPIRED
                        ui.label(get_expired_label())\
                            .classes("px-4 pb-2 text-xs text-gray-500")

                        ui.separator()

                        ui.menu_item("Tentang Triava", on_click=about_dialog.open)

                        def logout():
                            app.storage.user.clear()
                            ui.navigate.to('/login')

                        ui.menu_item("Logout", on_click=logout)

            ui.separator().classes("w-full opacity-30 mb-1")
