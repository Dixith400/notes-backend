import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import settings
from database import database
from repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class PasswordHasher:
    """Wraps password hashing so authentication logic stays readable."""

    @staticmethod
    def hash(password: str):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def verify(password: str, hashed_password) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


class TokenService:
    """Creates and validates JWT tokens used by protected routes."""

    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create(self, email: str) -> str:
        return jwt.encode({"email": email}, self.secret_key, algorithm=self.algorithm)

    def read_email(self, token: str) -> str:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        return payload.get("email")


class AuthService:
    """Coordinates user lookup, password checks, and token creation."""

    def __init__(self, user_repository: UserRepository, token_service: TokenService):
        self.users = user_repository
        self.tokens = token_service

    async def register(self, email: str, password: str):
        existing_user = await self.users.find_by_email(email)
        if existing_user:
            return {"error": "user already exists"}

        await self.users.create(email, PasswordHasher.hash(password))
        return {"message": "successfully inserted the data"}

    async def login(self, email: str, password: str):
        db_user = await self.users.find_by_email(email)
        if not db_user:
            return {"error": "user not found"}

        if not PasswordHasher.verify(password, db_user["password"]):
            return {"error": "wrong password"}

        return {"token": self.tokens.create(email)}


token_service = TokenService(settings.secret_key, settings.algorithm)
auth_service = AuthService(UserRepository(database.db), token_service)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """FastAPI dependency that returns the email stored in a valid token."""

    try:
        email = token_service.read_email(token)
        if not email:
            raise HTTPException(401, detail="token is invalid")
        return email
    except JWTError:
        raise HTTPException(401, detail="token is invalid")
