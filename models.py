from pydantic import BaseModel

class user_registration(BaseModel):
    email : str
    password : str

class user_login(BaseModel):
    email: str
    password: str

class notes(BaseModel):
    name: str
    content: str
