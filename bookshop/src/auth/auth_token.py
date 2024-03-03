from dotenv import dotenv_values
import bcrypt 
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

METHOD = 'HS256'
secret_key = dotenv_values('.env')['TOKEN_SECRET_KEY']

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def verify_password(enter_password: str, hash_password: bytes) -> bool:
    enter_password = bytes(enter_password, 'utf-8')
    hash_password = bytes(hash_password, 'utf-8')
    return bcrypt.checkpw(password=enter_password, hashed_password=hash_password)

def create_token(seller_data: dict):
    token = jwt.encode(seller_data, secret_key, algorithm=METHOD)
    return token

def get_auth_seller(token: str = Depends(oauth2_scheme)):
    decoded = jwt.decode(token, secret_key, algorithms=[METHOD])
    print(decoded)
    if not decoded:
        return None
    return decoded

