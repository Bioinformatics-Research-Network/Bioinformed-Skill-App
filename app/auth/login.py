from flask_login import LoginManager
from app.db import db_session
from app.models import Users

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(Users).get(int(user_id))
