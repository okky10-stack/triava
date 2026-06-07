from nicegui import app


def get_patient():
    if 'patient' not in app.storage.user:
        app.storage.user['patient'] = {}
    return app.storage.user['patient']


def clear_patient():
    app.storage.user['patient'] = {}