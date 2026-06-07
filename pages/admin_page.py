from nicegui import ui, app
from database import (
    get_all_users,
    activate_user,
    delete_user,
    deactivate_user,
    get_all_users_triage_counts,
    reset_password,
    get_all_triage,  # 🔥 tambahan
)
import datetime

from components.header_triase import header_triase
from components.ui_system import glass_card, triage_badge, btn_primary_compact # 🔥 pakai UI system


@ui.page("/admin")
def admin_page():

    dialog_open = False

    # ======================
    # 🔐 AUTH
    # ======================
    if app.storage.user.get("role") != "admin":
        ui.label("❌ Unauthorized").classes("text-red text-xl")
        return

    with ui.column().classes("w-full"):

        header_triase()

        with ui.column().classes("w-full max-w-md mx-auto px-4 pt-1 pb-12 gap-4"):

            # ======================
            # 🔔 PENDING ALERT
            # ======================
            users_all = get_all_users()
            pending_users = [u for u in users_all if u["active"] == 0]

            if pending_users:
                with glass_card().classes("bg-yellow-50 border border-yellow-200"):
                    ui.label(f"⚠️ {len(pending_users)} user menunggu approval").classes(
                        "text-sm text-yellow-700 font-semibold text-center"
                    )

            # ======================
            # HEADER
            # ======================
            ui.label("ADMIN CONTROL").classes("text-lg font-bold text-center w-full")

            ui.label("User management & triage monitoring").classes(
                "text-xs text-gray-500 text-center w-full"
            )

            # ======================
            # 🔎 FILTER
            # ======================
            with glass_card():
                search = (
                    ui.input(placeholder="Search user...")
                    .props("outlined dense clearable")
                    .classes("w-full mb-2")
                )

                sort = (
                    ui.select(["All", "Active", "Pending"], value="All")
                    .props("outlined dense")
                    .classes("w-full")
                )

            table_container = ui.column().classes("w-full gap-3")

            # ======================
            # ACTION HANDLER
            # ======================
            def handle_quick_action(action, email):

                if action == "approve":
                    activate_user(email, 30)

                elif action == "deactivate":
                    deactivate_user(email)

                elif action == "delete":
                    delete_user(email)

                elif action == "reset":
                    reset_password(email)

                refresh_table()

            # ======================
            # TRIAGE MAP (SUMMARY)
            # ======================
            def get_triage_map():
                stats = get_all_users_triage_counts()
                return {
                    s["user_id"]: {"h": s["hijau"], "k": s["kuning"], "m": s["merah"]}
                    for s in stats
                }

            # ======================
            # FORMAT TANGGAL
            # ======================
            def format_short(dt):
                try:
                    if isinstance(dt, str):
                        dt = datetime.datetime.fromisoformat(dt)
                    return dt.strftime("%d-%m-%Y")
                except:
                    return str(dt)

            # ======================
            # 🔥 DETAIL USER + HISTORY
            # ======================
            def show_user_detail(u):
                nonlocal dialog_open
                dialog_open = True

                triage_data = get_all_triage(u["email"])
                triage_data = triage_data[:10]

                with ui.dialog() as dialog:

                    # 🔥 HANDLE CLOSE
                    def on_close():
                        nonlocal dialog_open
                        dialog_open = False

                    dialog.on("hide", lambda: on_close())

                    with glass_card().classes("w-80"):

                        ui.label("Detail User").classes(
                            "text-lg font-bold text-gray-800 mb-2"
                        )

                        ui.separator()

                        ui.label(f"📧 {u['email']}").classes("text-xs text-gray-500")

                        ui.label(u.get("organization") or "-").classes(
                            "text-sm font-semibold text-blue-700 mt-2"
                        )

                        ui.label(f"📍 {u.get('alamat') or '-'}").classes(
                            "text-xs text-gray-600"
                        )

                        ui.label(f"👨‍⚕️ {u.get('pimpinan') or '-'}").classes(
                            "text-xs text-gray-600"
                        )

                        ui.label(f"📱 {u.get('no_wa') or '-'}").classes(
                            "text-xs text-gray-600"
                        )

                        ui.separator().classes("my-2")

                        status = "Active" if u["active"] == 1 else "Pending"
                        ui.label(f"Status: {status}").classes("text-xs text-gray-500")

                        # ======================
                        # 🔥 BUTTON 4 SEJAJAR
                        # ======================
                        with ui.row().classes("w-full gap-1 mt-3"):

                            btn_primary_compact(
                                "Approve",
                                lambda: (
                                    handle_quick_action("approve", u["email"]),
                                    dialog.close(),
                                ),
                            )

                            btn_primary_compact(
                                "Deactivate",
                                lambda: (
                                    handle_quick_action("deactivate", u["email"]),
                                    dialog.close(),
                                ),
                            )

                            btn_primary_compact(
                                "Reset",
                                lambda: (
                                    handle_quick_action("reset", u["email"]),
                                    dialog.close(),
                                ),
                            )

                            btn_primary_compact(
                                "Delete",
                                lambda: (
                                    handle_quick_action("delete", u["email"]),
                                    dialog.close(),
                                ),
                            )

                       # ======================
                        # 🔥 TRIAGE SUMMARY (ALL TIME)
                        # ======================
                        ui.separator().classes("my-2")

                        ui.label("Total Triage").classes("text-sm font-semibold text-center w-full")

                        # ambil summary
                        stats = get_all_users_triage_counts()
                        user_stat = next(
                            (s for s in stats if s["user_id"] == u["email"]),
                            {"hijau": 0, "kuning": 0, "merah": 0},
                        )

                        with ui.row().classes("w-full justify-center gap-1 mt-1"):
                            triage_badge(user_stat["hijau"], "green")
                            triage_badge(user_stat["kuning"], "yellow")
                            triage_badge(user_stat["merah"], "red")


                dialog.open()

            # ======================
            # TABLE RENDER
            # ======================
            def refresh_table():
                table_container.clear()

                users = get_all_users()
                triage_map = get_triage_map()
                keyword = (search.value or "").lower()

                def get_days_left(u):
                    if not u["expired_at"]:
                        return 999
                    dt = datetime.datetime.fromtimestamp(float(u["expired_at"]))
                    return (dt - datetime.datetime.now()).days

                users.sort(key=get_days_left)

                with table_container:

                    for u in users:

                        email = u["email"].lower()

                        if keyword and keyword not in email:
                            continue

                        if sort.value == "Active" and u["active"] == 0:
                            continue
                        if sort.value == "Pending" and u["active"] == 1:
                            continue

                        status = "Active" if u["active"] == 1 else "Pending"
                        status_color = (
                            "text-green-600" if u["active"] else "text-yellow-500"
                        )

                        t = triage_map.get(u["email"], {"h": 0, "k": 0, "m": 0})

                        with glass_card().classes(
                            "cursor-pointer active:scale-[0.98] transition"
                        ).on("click", lambda e, u=u: show_user_detail(u)):

                            with ui.row().classes(
                                "justify-between items-center w-full"
                            ):

                                with ui.column().classes("gap-0"):
                                    ui.label(u.get("organization") or "-").classes(
                                        "text-sm font-semibold text-blue-700"
                                    )

                                    ui.label(u["email"]).classes(
                                        "text-xs text-gray-400"
                                    )

                                with ui.column().classes("items-end gap-1"):

                                    ui.label(status).classes(
                                        f"text-xs font-semibold {status_color}"
                                    )

                                    ui.label(
                                        f"H:{t['h']} K:{t['k']} M:{t['m']}"
                                    ).classes("text-[11px] text-gray-500")

                                    if u["active"] == 0:
                                        ui.label("NEW").classes(
                                            "text-[10px] bg-yellow-400 text-white px-2 py-0.5 rounded"
                                        )

            # ======================
            # EVENTS
            # ======================
            search.on("input", lambda _: refresh_table())
            sort.on("update:model-value", lambda _: refresh_table())

            refresh_table()
            ui.timer(10, lambda: None if dialog_open else refresh_table())

            # ======================
            # OVERVIEW
            # ======================
            ui.label("TRIAGE OVERVIEW").classes(
                "text-sm font-semibold text-center mt-1"
            )

            overview_container = ui.column().classes("w-full items-center gap-6")

            def load_stats():
                overview_container.clear()
                stats = get_all_users_triage_counts()

                total_h = sum(s["hijau"] or 0 for s in stats)
                total_k = sum(s["kuning"] or 0 for s in stats)
                total_m = sum(s["merah"] or 0 for s in stats)

                with overview_container:

                    with glass_card().classes("text-center"):

                        ui.label("TOTAL TRIAGE").classes("text-xs text-gray-500 mb-2")

                        with ui.row().classes(
                            "w-full justify-center items-center gap-10"
                        ):

                            with ui.column().classes("items-center"):
                                ui.label(str(total_h)).classes(
                                    "text-lg font-bold text-green-600"
                                )
                                ui.label("Hijau").classes("text-xs text-gray-400")

                            with ui.column().classes("items-center"):
                                ui.label(str(total_k)).classes(
                                    "text-lg font-bold text-yellow-500"
                                )
                                ui.label("Kuning").classes("text-xs text-gray-400")

                            with ui.column().classes("items-center"):
                                ui.label(str(total_m)).classes(
                                    "text-lg font-bold text-red-600"
                                )
                                ui.label("Merah").classes("text-xs text-gray-400")

            load_stats()
            ui.timer(15, lambda: None if dialog_open else load_stats())
