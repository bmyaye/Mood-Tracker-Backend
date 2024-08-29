from . import moods
from . import users

def init_router(app):
    app.include_router(moods.router)
    app.include_router(users.router)