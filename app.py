from nicegui import ui, app
import os


# ======================
# 🌐 PWA + MOBILE CORE
# ======================
ui.add_head_html(
    """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#2563eb">

<!-- iOS -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Triava">

<!-- Android -->
<meta name="mobile-web-app-capable" content="yes">

<link rel="manifest" href="/static/manifest.json">

<style>
html {
  -webkit-text-size-adjust: 100%;
}
body {
  overflow-x: hidden;
  background: #f5f7fb;
}

/* Fix zoom iOS */
input, textarea {
  font-size: 16px !important;
}

/* Touch friendly */
button {
  min-height: 44px;
}

/* Safe area iPhone */
.safe-area {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
""",
    shared=True,
)


# ======================
# 📁 STATIC FILE (FIX PATH)
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.add_static_files("/static", os.path.join(BASE_DIR, "static"))


# ======================
# 🔧 SERVICE WORKER
# ======================
ui.add_head_html(
    """
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/sw.js');
}
</script>
""",
    shared=True,
)


# ======================
# 🎨 GLOBAL STYLE FUNCTION (AMAN)
# ======================
def inject_global_style():
    ui.add_head_html(
        """
        <style>
        body {
            background-color: #f5f7fb;
        }

        .nice-card {
            border-radius: 16px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
            background: white;
        }

        .nice-button {
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.15s ease;
        }
        .nice-button:active {
            transform: scale(0.97);
        }

        .card-green {
            background: linear-gradient(135deg, #34d399, #059669);
            color: white;
        }
        .card-yellow {
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            color: white;
        }
        .card-red {
            background: linear-gradient(135deg, #f87171, #dc2626);
            color: white;
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
        }

        .subtitle {
            font-size: 13px;
            color: #6b7280;
        }
        </style>
        """,
        shared=True,
    )


# ======================
# 🔐 GUARD
# ======================
def auth_guard(page_func):
    def wrapper():
        if not app.storage.user.get("email"):
            ui.navigate.to("/login")
            return
        inject_global_style()
        return page_func()

    return wrapper


def admin_guard(page_func):
    def wrapper():
        if not app.storage.user.get("email"):
            ui.navigate.to("/login")
            return

        if app.storage.user.get("role") != "admin":
            ui.navigate.to("/dashboard")
            return

        inject_global_style()
        return page_func()

    return wrapper


# ======================
# IMPORT
# ======================
from database import init_db, init_user_table

from pages.landing_page import landing_page
from pages.legal_page import legal_page
from pages.history_page import history_page
from pages.login_page import login_page
from pages.dashboard_page import dashboard_page
from pages.step1_identitas import step1_page
from pages.step2_anamnesa import step2_page
from pages.step3_vital import step3_page
from pages.step4_abcde import step4_page
from pages.step5_triage import step5_page
from pages.admin_page import admin_page


# ======================
# INIT DB
# ======================
init_user_table()
init_db()


# ======================
# ROUTES
# ======================


# 🔓 PUBLIC
def landing_wrapper():
    landing_page()


def login_wrapper():
    inject_global_style()
    login_page()


ui.page("/")(landing_wrapper)
ui.page("/login")(login_wrapper)


def legal_wrapper():
    inject_global_style()
    legal_page()


ui.page("/legal")(legal_wrapper)

# 🔐 USER
ui.page("/dashboard")(auth_guard(dashboard_page))
ui.page("/history")(auth_guard(history_page))

ui.page("/step1")(auth_guard(step1_page))
ui.page("/step2")(auth_guard(step2_page))
ui.page("/step3")(auth_guard(step3_page))
ui.page("/step4")(auth_guard(step4_page))
ui.page("/step5")(auth_guard(step5_page))


# 👑 ADMIN
ui.page("/admin")(admin_guard(admin_page))

from fastapi import Request
from fastapi.responses import RedirectResponse, FileResponse


# ======================
# 🌐 SET LANG ENDPOINT
# ======================
@app.get("/set-lang")
async def set_lang_route(request: Request, lang: str = "id", next: str = "/"):
    from nicegui import app as napp
    # Store in NiceGUI user session via cookie-based storage isn't direct,
    # so we redirect and let the landing page read from a cookie instead.
    resp = RedirectResponse(url=next)
    resp.set_cookie("triava_lang", lang, max_age=60 * 60 * 24 * 365, path="/")
    return resp


# ======================
# RUN
# ======================
ui.run(
    host="0.0.0.0",
    port=int(os.getenv("PORT", 8080)),
    storage_secret="triage-secret-0326",
    reload=False,
)
