
from app.utils.security import hash_password, verify_password

password = "MySecret123!"

# Hash the password
hashed_password = hash_password(password)

print("Password hashed successfully:", bool(hashed_password))
print("Correct password:", verify_password(password, hashed_password))
print("Wrong password:", verify_password("WrongPassword", hashed_password))
