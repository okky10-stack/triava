from nicegui import ui


def progress_bar(current_step: int, total_step: int):

    progress = current_step / total_step

    with ui.column().classes("w-full items-center mt-1 mb-2"):

        # ======================
        # WRAPPER (GLASS STYLE)
        # ======================
        with ui.element("div").classes(
            """
            w-2/3 h-2 rounded-full overflow-hidden
            bg-white/20 backdrop-blur-sm
            border border-white/90
        """
        ).style(
            """
            box-shadow:
                inset 0 1px 2px rgba(0,0,0,0.12),
                0 2px 6px rgba(0,0,0,0.08);
        """
        ):

            # ======================
            # PROGRESS FILL
            # ======================
            ui.element("div").style(
                f"""
                width: {progress * 100}%;
                height: 100%;
                background: linear-gradient(90deg, #6A00FF, #3F00CC);
                border-radius: 999px;
                transition: width 0.3s ease;

                /* subtle glow */
                box-shadow:
                    0 0 8px rgba(106,0,255,0.5);
            """
            )
