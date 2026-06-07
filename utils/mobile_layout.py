from nicegui import ui


def mobile_container():
    return ui.column().classes(
        """
        w-full 
        max-w-md 
        mx-auto 
        px-4 
        pb-6 
        gap-3 
        safe-area
        """
    )
