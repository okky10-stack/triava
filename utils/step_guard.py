from nicegui import app, ui

def step_guard(required_step, redirect_to):

    current = app.storage.user.get('current_step', 1)

    if current < required_step:
        ui.navigate.to(redirect_to)
        return False

    return True