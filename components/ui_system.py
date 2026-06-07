from nicegui import ui


# =========================
# 🔷 GLASS CARD (STANDARD)
# =========================
def glass_card():
    return ui.card().classes(
        """
        w-full
        rounded-2xl
        p-4
        backdrop-blur-xl
        bg-white/70
        border border-black/10
        shadow-[0_10px_30px_rgba(0,0,0,0.08)]
    """
    )


# =========================
# 🔷 GLASS CONTAINER (STEP PAGE)
# =========================
def glass_container():
    return ui.column().classes(
        """
        w-full max-w-sm mx-auto
        backdrop-blur-2xl
        bg-white/50
        border border-white/30
        rounded-3xl
        shadow-[0_20px_60px_rgba(0,0,0,0.12)]
        px-4 py-4
    """
    )


# =========================
# 🔷 PRIMARY BUTTON
# =========================
def btn_primary(label, on_click):
    with ui.element("div").classes(
        "w-full h-[42px] flex items-center justify-center text-center rounded-xl cursor-pointer overflow-hidden"
    ).style(
        """
            background: linear-gradient(145deg, #6A00FF, #3F00CC);
            box-shadow:
                0 10px 25px rgba(106,0,255,0.4),
                inset 0 2px 0 rgba(255,255,255,0.3);
            transition: all 0.15s ease;
        """
    ).on(
        "click", on_click
    ).on(
        "mousedown", lambda e: e.sender.style("transform: scale(0.94)")
    ).on(
        "mouseup", lambda e: e.sender.style("transform: scale(1)")
    ):

        ui.label(label).classes("py-2 text-white font-semibold text-sm w-full")

        ui.element("div").style(
            """
            position:absolute;
            top:0; left:0;
            width:100%; height:35%;
            background: linear-gradient(to bottom, rgba(255,255,255,0.35), transparent);
        """
        )


# =========================
# 🔷 SECONDARY BUTTON
# =========================
def btn_secondary(label, on_click, color="glass"):

    if color == "glass":
        bg = "rgba(230,235,255,0.35)"
        text_color = "#1e293b"  # slate-800
    elif color == "orange":
        bg = "#fb923c"
        text_color = "white"
    elif color == "green":
        bg = "#22c55e"
        text_color = "white"
    else:
        bg = "rgba(255,255,255,0.25)"
        text_color = "#1e293b"

    with ui.element("div")\
        .classes("flex-1 min-h-[42px] text-center rounded-xl cursor-pointer")\
        .style(f"""
            background: {bg};
            backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid rgba(120,140,255,0.25);
            box-shadow:
                0 6px 18px rgba(80,100,255,0.15),
                inset 0 1px 0 rgba(255,255,255,0.4);
            transition: all 0.15s ease;
        """)\
        .on("click", on_click)\
        .on("mousedown", lambda e: e.sender.style("transform: scale(0.95)"))\
        .on("mouseup", lambda e: e.sender.style("transform: scale(1)")):

        ui.label(label).classes("py-2 font-semibold text-sm w-full"
        ).style(f"color: {text_color}")

        # highlight layer
        ui.element("div").style("""
            position:absolute;
            top:0; left:0;
            width:100%; height:40%;
            background: linear-gradient(
                to bottom,
                rgba(255,255,255,0.3),
                transparent
            );
        """)

def btn_primary_compact(label, on_click):
    with ui.element("div").classes(
        """
        flex-1
        h-[34px]
        rounded-lg
        cursor-pointer
        flex items-center justify-center
        text-center
        overflow-hidden
        relative
        """
    ).style(
        """
        background: linear-gradient(145deg, #6A00FF, #3F00CC);
        box-shadow:
            0 6px 14px rgba(106,0,255,0.35),
            inset 0 1px 0 rgba(255,255,255,0.25);
        transition: all 0.12s ease;
        """
    ).on(
        "click", on_click
    ).on(
        "mousedown", lambda e: e.sender.style("transform: scale(0.95)")
    ).on(
        "mouseup", lambda e: e.sender.style("transform: scale(1)")
    ):

        ui.label(label).classes("text-white text-[10px] font-semibold leading-none")

        # highlight layer
        ui.element("div").style(
            """
            position:absolute;
            top:0; left:0;
            width:100%; height:35%;
            background: linear-gradient(to bottom, rgba(255,255,255,0.3), transparent);
        """
        )


def triage_badge( value, color):
    bg = {
        "green": "bg-green-500",
        "yellow": "bg-yellow-400 text-gray-800",
        "red": "bg-red-500",
    }[color]

    label = {
        "green": "H",
        "yellow": "K",
        "red": "M",
    }[color]

    with ui.element("div").classes(
        f"{bg} text-white text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1"
    ):
        ui.label(label).classes("font-bold")
        ui.label(str(value))
