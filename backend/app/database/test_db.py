from app.database.connection import SessionLocal
from app.database.models import User


db = SessionLocal()

users = db.query(User).all()

for user in users:
    print(user.id, user.name, user.email)

db.close()