from models import db
from app import app

db.drop_all()
db.create_all()



db.session.add_all()
db.session.commit()