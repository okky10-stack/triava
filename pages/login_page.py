from nicegui import ui, app
from utils.mobile_layout import mobile_container
from database import get_user, create_user, execute
from datetime import datetime
import re


def login_page():

    # ===== GLOBAL STYLE (IOS 26 GLASS) =====
    ui.add_head_html(
        """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@700;800&display=swap" rel="stylesheet">
<style>
    body {
        background: radial-gradient(circle at 20% 10%, #eef2ff, transparent 40%),
                    radial-gradient(circle at 80% 90%, #e0e7ff, transparent 40%),
                    #f7f9fc;
        font-family: 'Inter', sans-serif;
    }

    /* ===== MAIN GLASS ===== */
    .glass-main {
        background: rgba(255,255,255,0.45);
        backdrop-filter: blur(28px) saturate(180%);
        border-radius: 36px;
        border: 1px solid rgba(255,255,255,0.35);
        box-shadow:
            0 30px 80px rgba(0,0,0,0.12),
            inset 0 2px 0 rgba(255,255,255,0.6);
        position: relative;
        overflow: hidden;
    }

    /* subtle noise */
    .glass-main::before {
        content: "";
        position: absolute;
        inset: 0;
        background-image: url('https://www.transparenttextures.com/patterns/noise.png');
        opacity: 0.04;
        pointer-events: none;
    }

    .glass {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(16px);
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.3);
    }
</style>
""",
        shared=True,
    )

    with mobile_container().classes("items-center w-full mb-24 mt-12 pb-6"):

        # ===== BACKGROUND =====
        ui.html(
            """
<div style="position:fixed; top:-10%; right:-5%; width:500px; height:500px;
background:#c7d2fe; border-radius:50%; filter:blur(140px); z-index:0;"></div>

<div style="position:fixed; bottom:-10%; left:-5%; width:400px; height:400px;
background:#ddd6fe; border-radius:50%; filter:blur(140px); z-index:0;"></div>
""",
            sanitize=False,
        )

        # ===== MAIN GLASS WRAPPER =====
        with ui.column().classes(
            "w-full max-w-md relative z-10 items-center glass-main px-6 py-10"
        ):

            # ===== HEADER =====
            with ui.column().classes(
                "w-full items-center text-center mb-14 gap-2 mt-4"
            ):

                with ui.element("div").classes(
                    "w-24 h-24 rounded-3xl overflow-hidden relative"
                ).style(
                    """
                box-shadow: 
                    0 20px 40px rgba(0,0,0,0.25),
                    0 6px 14px rgba(0,0,0,0.2);
                """
                ):

                    ui.image("/static/icon-512.png").classes(
                        "w-full h-full object-cover rounded-2xl"
                    )

                    # highlight
                    ui.element("div").style(
                        """
                    position:absolute;
                    top:0;left:0;width:100%;height:35%;
                    background:linear-gradient(to bottom, rgba(255,255,255,0.6), transparent);
                    """
                    )

                    # depth
                    ui.element("div").style(
                        """
                    position:absolute;
                    bottom:0;left:0;width:100%;height:60%;
                    background:linear-gradient(to top, rgba(0,0,0,0.2), transparent);
                    """
                    )

                ui.label("Triava").classes(
                    "text-4xl mt-2 font-extrabold tracking-tight"
                ).style("color: #1e1b4b")

                ui.label("Rapid Response. Anytime.").classes("text-gray-800 text-sm text-bold")

            # ===== BUTTON LOGIN =====
            with ui.element("div").classes(
                "w-3/4 mx-auto relative rounded-2xl overflow-hidden cursor-pointer mb-3"
            ).style(
                """
            background: linear-gradient(145deg, #6A00FF, #3F00CC);
            box-shadow: 
                0 12px 30px rgba(106,0,255,0.5),
                inset 0 2px 0 rgba(255,255,255,0.3);
            transition: all 0.15s ease;
            """
            ).on(
                "click", lambda: login_dialog.open()
            ).on(
                "mousedown", lambda e: e.sender.style("transform: scale(0.94)")
            ).on(
                "mouseup", lambda e: e.sender.style("transform: scale(1)")
            ):

                ui.label("MASUK").classes(
                    "w-full text-center py-3 text-white text-lg font-semibold"
                )

                ui.element("div").style(
                    """
                position:absolute;
                top:0;
                left:0;
                width:100%;
                height:35%;
                background: linear-gradient(
                    to bottom,
                    rgba(255,255,255,0.4),
                    transparent
                );
                """
                )

            # ===== REGISTER LINK =====
            with ui.row().classes("justify-center gap-1 mt-1"):
                ui.label("Don't have an account?").classes("text-sm text-gray-500")
                ui.label("Sign Up").classes(
                    "text-sm font-semibold text-indigo-600 hover:underline cursor-pointer"
                ).on("click", lambda: register_dialog.open())

            # ===== FOOTER =====
            with ui.column().classes(
                "items-center justify-center w-full mt-12 text-center"
            ):
                ui.label("Simplified • Fast • Reliable").classes(
                    "text-xs text-gray-500 opacity-80")
                ui.label("Developed in Ruang Dokter's Lab").classes(
                    "text-xs text-gray-500 opacity-80")

    # =====================================================
    # 🔐 LOGIN DIALOG (UNCHANGED)
    # =====================================================
    with ui.dialog() as login_dialog:
        with ui.card().classes("glass p-6 w-80"):

            ui.label("Login").classes("text-xl font-bold text-blue-800 mb-4")

            email = ui.input("Email").classes("w-full mb-4")

            with ui.element("div").classes("relative w-full mb-4"):

                show_password = {"value": False}

                password = ui.input("Password", password=True).classes("w-full")

                eye_icon = ui.icon("visibility_off").classes(
                    "absolute right-2 bottom-3 cursor-pointer text-gray-400 hover:text-blue-600"
                )

                def toggle_password():
                    show_password["value"] = not show_password["value"]
                    password.props(
                        f'type={"text" if show_password["value"] else "password"}'
                    )
                    eye_icon.name = (
                        "visibility" if show_password["value"] else "visibility_off"
                    )

                eye_icon.on("click", toggle_password)

            def login():
                if not consent.value:
                    ui.notify("Anda harus menyetujui kebijakan terlebih dahulu", color="warning")
                    return

                user = get_user(email.value)

                if not user:
                    ui.notify("User tidak ditemukan")
                    return

                if user["password"] != password.value:
                    ui.notify("Password salah")
                    return

                if str(user.get("must_change_password")) == "1":
                    app.storage.user["email"] = user["email"]
                    ui.notify("Silakan ganti password terlebih dahulu", color="warning")
                    change_password_dialog.open()
                    return

                if user["role"] != "admin":

                    if not user["active"]:
                        ui.notify("Akun belum di-approve")
                        return

                    if not user["expired_at"]:
                        ui.notify("Akun belum aktif")
                        return

                    if datetime.now().timestamp() > float(user["expired_at"]):
                        ui.notify("Subscription habis")
                        return

                app.storage.user["email"] = user["email"]
                app.storage.user["role"] = user["role"]
                app.storage.user["active"] = user["active"]
                app.storage.user["expired_at"] = user["expired_at"]

                if user["role"] == "admin":
                    ui.navigate.to("/admin")
                else:
                    ui.navigate.to("/dashboard")

            # 🔒 CONSENT (WAJIB)
            consent = ui.checkbox(
                "Saya menyetujui Kebijakan Privasi, Ketentuan Layanan, dan Disclaimer Medis"
            ).classes("text-xs mt-0")

            # 🔗 LINK LEGAL PAGE
            ui.link(
                "Baca Kebijakan & Ketentuan",
                "/legal"
            ).classes("text-xs text-blue-500")

            # 🔴 MINI DISCLAIMER (BIAR KENA)
            ui.label(
                "Triava hanya alat bantu, bukan pengganti keputusan medis."
            ).classes("text-xs text-red-400 mt-0")

            # 🔘 BUTTON LOGIN
            btn_login = ui.button("Masuk", on_click=login).classes(
                "w-full py-2 rounded-xl text-lg font-bold text-white shadow-lg mt-2"
            ).style("background: linear-gradient(135deg, #6A00FF, #3F00CC) !important")

            # 🔒 DISABLE LOGIC
            def update_button():
                btn_login.props(f'disable={not consent.value}')

            consent.on("update:model-value", lambda e: update_button())

            update_button()

    # =====================================================
    # 🔁 CHANGE PASSWORD (UNCHANGED)
    # =====================================================
    with ui.dialog() as change_password_dialog:
        with ui.card().classes("glass p-6 w-80"):

            ui.label("Ganti Password Baru").classes(
                "text-lg font-bold text-blue-800 mb-3"
            )

            new_pass = ui.input("Password Baru", password=True).classes("w-full mb-3")
            confirm_pass = ui.input("Ulangi Password", password=True).classes(
                "w-full mb-3"
            )

            def save_new_password():
                if not new_pass.value or not confirm_pass.value:
                    ui.notify("Isi semua field", color="warning")
                    return

                if new_pass.value != confirm_pass.value:
                    ui.notify("Password tidak sama", color="negative")
                    return

                if len(new_pass.value) < 6:
                    ui.notify("Minimal 6 karakter", color="warning")
                    return

                execute(
                    """
                    UPDATE users
                    SET password=?,
                        must_change_password=0
                    WHERE email=?
                """,
                    (new_pass.value, app.storage.user.get("email")),
                )

                ui.notify("Password berhasil diubah", color="positive")
                change_password_dialog.close()
                ui.navigate.to("/dashboard")

            ui.button("Simpan Password", on_click=save_new_password).classes(
                "w-full py-2 rounded-xl font-bold text-white"
            ).style("background: linear-gradient(135deg, #6A00FF, #3F00CC) !important")

    # =====================================================
    # 📝 REGISTER (UNCHANGED)
    # =====================================================
    with ui.dialog() as register_dialog:
        with ui.card().classes("glass p-6 w-80"):

            ui.label("Daftar Akun").classes("text-xl font-bold text-blue-800 mb-3")

            email_r = ui.input("Email").classes("w-full mb-2")
            password_r = ui.input("Password", password=True).classes("w-full mb-2")

            nama = ui.input("Nama Faskes").classes("w-full mb-2")
            alamat = ui.input("Address").classes("w-full mb-2")
            pimpinan = ui.input("Pimpinan").classes("w-full mb-2")
            no_wa = ui.input("No WA").classes("w-full mb-2")

            def is_valid_email(e):
                return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", e)

            def register():

                if not all(
                    [
                        email_r.value,
                        password_r.value,
                        nama.value,
                        alamat.value,
                        pimpinan.value,
                        no_wa.value,
                    ]
                ):
                    ui.notify("Semua field wajib diisi", color="warning")
                    return

                if not is_valid_email(email_r.value):
                    ui.notify("Format email tidak valid", color="negative")
                    return

                if len(password_r.value) < 6:
                    ui.notify("Password minimal 6 karakter", color="warning")
                    return

                create_user(
                    email_r.value,
                    password_r.value,
                    role="user",
                    organization=nama.value,
                    alamat=alamat.value,
                    pimpinan=pimpinan.value,
                    no_wa=no_wa.value,
                )

                ui.notify("Berhasil daftar, tunggu approval admin", color="positive")
                register_dialog.close()

            ui.button("Daftar", on_click=register).classes(
                "w-full py-2 rounded-xl font-bold text-white"
            ).style("background: linear-gradient(135deg, #F97316, #FB923C) !important")


            ui.label(
                "Akun Anda akan diverifikasi oleh admin sebelum dapat digunakan."
            ).classes("text-xs text-gray-500 text-center mb-3")

    
