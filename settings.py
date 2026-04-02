from flask import Flask
from database import db, migrate
from sqlalchemy import event, inspect
from flask_admin import Admin
from flask_admin.base import Bootstrap4Theme
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from admin.views import UserView, DeviceView
from models import *


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smart.db"
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = 'your-random-secret-key'

db.init_app(app)
migrate.init_app(app, db)
bcrypt = Bcrypt(app)
admin = Admin(app, name="Панель администратора", theme=Bootstrap4Theme())

admin.add_view(UserView(User, db.session))
admin.add_view(DeviceView(Device, db.session))
# admin.add_view(ThemeView(Theme, db.session))
# admin.add_view(UserAnswerView(UserAnswer, db.session))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@event.listens_for(User, 'before_insert')
def before_insert(mapper, connection, target):
    # Выполняется перед INSERT
    print(target.password)
    target.password = bcrypt.generate_password_hash(target.password).decode('utf-8')


@event.listens_for(User, 'before_update')
def before_update(mapper, connection, target):
    # Выполняется перед UPDATE
    insp = inspect(target)
    history = insp.attrs.password.history
    if history.added:
        target.password = bcrypt.generate_password_hash(target.password).decode('utf-8')