from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import User


db = SessionLocal()

statement = select(User).where(User.id == 1)

result = db.execute(statement)

user = result.scalar_one_or_none()

print(user.name)
print(user.email)