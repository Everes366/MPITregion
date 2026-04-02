from flask_sqlalchemy import SQLAlchemy
from models import BaseModel
from flask_migrate import Migrate


db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate()