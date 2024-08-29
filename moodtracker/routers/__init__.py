from . import moods

def init_router(app):
    app.include_router(moods.router)