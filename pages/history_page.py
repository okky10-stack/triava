from nicegui import ui
from database import get_all_triage
from utils.mobile_layout import mobile_container
from datetime import datetime

from components.header_triase import header_triase
from components.ui_system import glass_container


# ======================
# BUTTON SECONDARY
# ======================
def btn_secondary(label, on_click, color="glass"):

    if color == "glass":
        bg = "rgba(230,235,255,0.35)"
        text_color = "#1e293b"
    elif color == "orange":
        bg = "#fb923c"
        text_color = "white"
    elif color == "green":
        bg = "#22c55e"
        text_color = "white"
    else:
        bg = "rgba(255,255,255,0.25)"
        text_color = "#1e293b"

    with ui.element("div").classes(
        "flex-1 min-h-[42px] text-center rounded-xl cursor-pointer relative"
    ).style(
        f"""
            background: {bg};
            backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid rgba(120,140,255,0.25);
            box-shadow:
                0 6px 18px rgba(80,100,255,0.15),
                inset 0 1px 0 rgba(255,255,255,0.4);
            transition: all 0.15s ease;
        """
    ).on(
        "click", on_click
    ).on(
        "mousedown", lambda e: e.sender.style("transform: scale(0.95)")
    ).on(
        "mouseup", lambda e: e.sender.style("transform: scale(1)")
    ):

        ui.label(label).classes("py-2 font-semibold text-sm w-full").style(
            f"color: {text_color}"
        )

        ui.element("div").style(
            """
            position:absolute;
            top:0; left:0;
            width:100%; height:40%;
            background: linear-gradient(
                to bottom,
                rgba(255,255,255,0.3),
                transparent
            );
        """
        )

    # ======================
    # FORMAT TANGGAL
    # ======================


def parse_datetime(dt_value):
    if isinstance(dt_value, datetime):
        return dt_value  # sudah datetime

    if isinstance(dt_value, str):
        try:
            return datetime.strptime(dt_value, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            try:
                return datetime.strptime(dt_value, "%Y-%m-%d %H:%M:%S.%f")
            except:
                try:
                    return datetime.strptime(dt_value, "%Y-%m-%d %H:%M:%S")
                except:
                    return None

    return None


def format_short(dt):
    parsed = parse_datetime(dt)
    return parsed.strftime("%d-%m-%Y") if parsed else str(dt)


def format_full(dt):
    parsed = parse_datetime(dt)
    return parsed.strftime("%d-%m-%Y %H:%M") if parsed else str(dt)


def history_page():
    from nicegui import app

    user_id = app.storage.user.get("email")
    data = get_all_triage(user_id)

    # 🔥 limit untuk performa
    data = data[:25]

    with mobile_container().classes("items-center px-4"):

        # ======================
        # HEADER
        # ======================
        header_triase()

        # ======================
        # BACK BUTTON
        # ======================
        with ui.row().classes("w-full max-w-sm mt-2"):
            btn_secondary("Back", lambda: ui.navigate.to("/dashboard"))

        # ======================
        # MAIN GLASS
        # ======================
        with glass_container():

            ui.label("Riwayat Pasien").classes(
                "text-xl font-bold text-center w-full mb-3"
            )

            if not data:
                ui.label("Belum ada data").classes(
                    "text-sm text-gray-500 text-center mt-6"
                )

            else:

                # ======================
                # TABLE STRUCTURE
                # ======================
                columns = [
                    {"name": "no", "label": "No", "field": "no", "align": "center"},
                    {
                        "name": "nama",
                        "label": "Nama",
                        "field": "nama",
                        "align": "center",
                    },
                    {
                        "name": "triage",
                        "label": "Label",
                        "field": "triage",
                        "align": "center",
                    },
                ]

                rows = []

                for i, d in enumerate(data, start=1):
                    rows.append(
                        {
                            "no": i,
                            "nama": d["nama_pasien"],
                            "tanggal": format_short(d["created_at"]),
                            "tanggal_full": format_full(d["created_at"]),
                            "triage": d["triage_result"],
                            "masalah": d.get("masalah", []),
                        }
                    )

                table = ui.table(columns=columns, rows=rows, row_key="no").classes(
                    """
                    w-full text-sm
                    bg-white/60 backdrop-blur-md
                    rounded-xl
                    text-center
                """
                )

                # ===== CLINICAL STYLE =====
                table.props("dense flat bordered separator=horizontal")

                # ======================
                # CELL NAMA + TANGGAL
                # ======================
                table.add_slot(
                    "body-cell-nama",
                    """
                    <q-td :props="props" class="text-center align-middle">
                        <div class="flex flex-col items-center justify-center w-full">

                            <div class="font-semibold text-gray-800 text-sm">
                                {{ props.value }}
                            </div>

                            <div class="text-[10px] text-gray-500 mt-0.5">
                                {{ props.row.tanggal }}
                            </div>

                        </div>
                    </q-td>
                """,
                )

                # ======================
                # POPUP DETAIL
                # ======================
                def show_detail(row):

                    with ui.dialog() as dialog, ui.card().classes(
                        "w-[90vw] max-w-md p-4 rounded-2xl bg-white/85 backdrop-blur-md"
                    ):

                        ui.label("Detail Pasien").classes(
                            "font-bold text-lg mb-0 text-center"
                        )

                        ui.separator()

                        ui.label(f"Nama: {row['nama']}")
                        ui.label(f"Triage: {row['triage']}")
                        ui.label(f"Tanggal: {row['tanggal_full']}")

                        ui.label("Masalah Klinis:").classes("font-semibold mt-3")

                        if row["masalah"]:
                            for m in row["masalah"]:
                                ui.label(f"• {m}")
                        else:
                            ui.label("Tidak ada masalah")

                    dialog.open()

                # ======================
                # CELL TRIAGE (CLICKABLE)
                # ======================
                table.add_slot(
                    "body-cell-triage",
                    """
    <q-td :props="props" class="text-center align-middle">
        <div class="flex justify-center items-center w-full">

            <span
                @click="$parent.$emit('show_detail', props.row)"
                style="cursor:pointer"
                :class="{
                    'flex items-center justify-center text-center text-xs font-semibold rounded-full h-6 w-20': true,

                    'bg-red-500 text-white': props.value === 'RED',
                    'bg-yellow-400 text-gray-800': props.value === 'YELLOW',
                    'bg-green-500 text-white': props.value === 'GREEN'
                }"
            >
                {{
                    props.value === 'RED' ? 'MERAH' :
                    props.value === 'YELLOW' ? 'KUNING' :
                    props.value === 'GREEN' ? 'HIJAU' :
                    props.value
                }}
            </span>

        </div>
    </q-td>
""",
                )

                # ======================
                # EVENT HANDLER
                # ======================
                table.on("show_detail", lambda e: show_detail(e.args))
