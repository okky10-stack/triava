from nicegui import ui
from utils.mobile_layout import mobile_container
from contextlib import contextmanager

from components.ui_system import btn_secondary
from components.header_triase import header_triase

def legal_page():

    header_triase()
    # =========================================
    # 🔧 CUSTOM EXPANSION STYLE
    # =========================================
    @contextmanager
    def expansion_item(title, icon, default_open=False):
        with ui.expansion(title, icon=icon, value=default_open).classes(
            "w-full rounded-xl overflow-hidden"
        ).props(
            "header-class=bg-indigo-50 text-indigo-800 font-semibold hover:bg-indigo-100 transition"
        ):

            with ui.column().classes("gap-1 p-3"):
                yield

    # =========================================
    # 📄 MAIN CONTENT
    # =========================================
    with mobile_container().classes("items-center w-full py-10"):

        with ui.column().classes("w-full max-w-3xl glass-main px-6 py-10 gap-3"):

            # ===== HEADER =====
            ui.label(
                "Kebijakan Privasi, Ketentuan Layanan, dan Disclaimer Medis"
            ).classes("text-2xl font-bold")

            ui.label("Terakhir diperbarui: April 2026").classes(
                "text-xs text-gray-500 mb-3"
            )

            # =========================================
            # 🔐 1. KEBIJAKAN PRIVASI
            # =========================================
            with expansion_item("Kebijakan Privasi", "lock"):

                ui.label("Data yang dikumpulkan:").classes("text-sm font-semibold")

                ui.label("• Identitas pasien (nama, umur, alamat)").classes(
                    "text-sm leading-tight"
                )
                ui.label(
                    "• Data klinis (anamnesis, vital sign, ABCDE, triage)"
                ).classes("text-sm leading-tight")
                ui.label("• Data pengguna (akun, aktivitas)").classes(
                    "text-sm leading-tight"
                )
                ui.label("• Data teknis (IP, perangkat, log sistem)").classes(
                    "text-sm leading-tight"
                )

                ui.label("Tujuan penggunaan:").classes("text-sm font-semibold mt-2")

                ui.label("• Mendukung triage klinis").classes("text-sm leading-tight")
                ui.label("• Dokumentasi medis internal").classes(
                    "text-sm leading-tight"
                )
                ui.label("• Analisis operasional layanan").classes(
                    "text-sm leading-tight"
                )
                ui.label("• Pengembangan sistem Triava").classes(
                    "text-sm leading-tight"
                )

                ui.label("Keamanan data:").classes("text-sm font-semibold mt-2")
                ui.label(
                    "Data dilindungi dengan kontrol akses dan sistem keamanan."
                ).classes("text-sm leading-tight")

                ui.label("Retensi data:").classes("text-sm font-semibold mt-2")
                ui.label(
                    "Data disimpan sesuai kebutuhan layanan dan dapat dihapus sesuai kebijakan."
                ).classes("text-sm leading-tight")

            # =========================================
            # 📜 2. KETENTUAN LAYANAN
            # =========================================
            with expansion_item("Ketentuan Layanan", "description"):

                ui.label(
                    "Triava adalah alat bantu klinis dan tidak menggantikan keputusan medis profesional."
                ).classes("text-sm leading-tight")

                ui.label("Pengguna wajib:").classes("text-sm font-semibold mt-2")

                ui.label("• Menggunakan sesuai standar medis").classes(
                    "text-sm leading-tight"
                )
                ui.label("• Memasukkan data yang akurat").classes(
                    "text-sm leading-tight"
                )
                ui.label("• Menjaga kerahasiaan akun").classes("text-sm leading-tight")

                ui.label("Dilarang:").classes("text-sm font-semibold mt-2")

                ui.label("• Menggunakan untuk tujuan ilegal").classes(
                    "text-sm leading-tight"
                )
                ui.label("• Mengakses data tanpa izin").classes("text-sm leading-tight")
                ui.label(
                    "• Mengandalkan sistem sebagai satu-satunya keputusan"
                ).classes("text-sm leading-tight")

                ui.label("Ketersediaan sistem:").classes("text-sm font-semibold mt-2")
                ui.label(
                    "Layanan disediakan sebagaimana adanya (as is) tanpa jaminan bebas gangguan."
                ).classes("text-sm leading-tight")

            # =========================================
            # 🔴 3. DISCLAIMER MEDIS
            # =========================================
            with expansion_item("Disclaimer Medis", "warning", default_open=True):

                ui.label(
                    "TRIAVA BUKAN ALAT DIAGNOSIS DAN TIDAK MEMBERIKAN KEPUTUSAN MEDIS FINAL."
                ).classes("text-red-600 text-sm font-semibold leading-tight")

                ui.label(
                    "TRIAVA HANYA ALAT BANTU (CLINICAL DECISION SUPPORT)."
                ).classes("text-red-600 text-sm leading-tight")

                ui.label(
                    "KEPUTUSAN MEDIS SEPENUHNYA TANGGUNG JAWAB TENAGA KESEHATAN."
                ).classes("text-red-600 text-sm leading-tight")

                ui.label(
                    "DALAM KONDISI DARURAT, WAJIB MENGUTAMAKAN PENILAIAN KLINIS LANGSUNG DAN PROTOKOL MEDIS."
                ).classes("text-red-600 text-sm font-semibold leading-tight")

            # =========================================
            # ⚖️ 4. PEMBATASAN TANGGUNG JAWAB
            # =========================================
            with expansion_item("Pembatasan Tanggung Jawab", "gavel"):

                ui.label(
                    "Triava tidak bertanggung jawab atas kerugian langsung maupun tidak langsung."
                ).classes("text-sm leading-tight")

                ui.label(
                    "Termasuk kesalahan medis, kehilangan data, atau kerugian operasional."
                ).classes("text-sm leading-tight")

                ui.label(
                    "Penggunaan sistem sepenuhnya menjadi risiko pengguna."
                ).classes("text-sm leading-tight")

            # =========================================
            # 📞 5. KONTAK
            # =========================================
            with expansion_item("Kontak", "mail"):

                ui.label("Email: support@triava.id").classes("text-sm leading-tight")

            # =========================================
            # 🔙 BUTTON
            # =========================================
            with ui.row().classes("w-full mt-6 justify-center"):
                btn_secondary("Back", lambda: ui.navigate.to("/"))
