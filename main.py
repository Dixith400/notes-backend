from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os 
from fastapi.middleware.cors import CORSMiddleware
from models import user_registration, user_login, notes
import bcrypt
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#loding environment variable 
load_dotenv()

app = FastAPI()
app.add_middleware(
    
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    
    
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client.notesdb

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

#routes 
@app.get("/")
async def health():
    await db.command("ping")
    return {"status": "ok", "db": "connected"}

@app.post("/register")
async def register(user: user_registration):
    existing_user = await db.user.find_one({"email": user.email})

    if existing_user:
        return {"error": "user already exists"}
    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

    user_data = {
        "email": user.email, 
        "password": hashed}
    await db.user.insert_one(user_data)

    return {"message": "successfully inserted the data"}

@app.post("/login")
async def login(user: user_registration):
    db_user = await db.user.find_one({"email":user.email})

    if not db_user:
        return {"error": "user not found"}
    
    # we need the name for decode user to validate 
    valid = bcrypt.checkpw(user.password.encode("utf-8"), db_user["password"])

    print("is_valid:", valid)

    if not valid:
        return {"error": "wrong password"}
    

    #syntax payload secreat key algo
    token = jwt.encode({"email": user.email}, SECRET_KEY, algorithm=ALGORITHM)

    print("token:", token)

    return {"token": token}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        return email
    
    except:
       raise HTTPException(401, detail="token is invalid")

@app.get("/test")
async def test_auth(current_user: str = Depends(get_current_user)):
    return {"logged in as": current_user}


#-------------- Google Auth ------------------------

@app.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = os.getenv("BACKEND_URL") + "/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    email = user_info["email"]
    
    existing_user = await db.users.find_one({"email": email})
    if not existing_user:
        await db.users.insert_one({"email": email, "password": None})
    
    jwt_token = jwt.encode({"email": email}, SECRET_KEY, algorithm=ALGORITHM)
    
    frontend_url = os.getenv("FRONTEND_URL")
    return RedirectResponse(f"{frontend_url}/notes?token={jwt_token}")   


### ---------------------------------              Notes apis :             --------------------------------------

@app.get("/notes")
async def get_notes(current_user: str = Depends(get_current_user)):
    notes = await db.notes.find({"user_email" : current_user}).to_list(100)
    for note in notes:
        note["_id"] = str(note["_id"])
    return notes

### user_email and _id will be create automatically by the Mongo so you don't need to add those fields to model

@app.post("/notes")
async def create_notes(notes: notes, current_user: str = Depends(get_current_user)):
    
    new_notes = {
        "name" : notes.name,
        "content" :notes.content,
        "user_email": current_user
    }

    await db.notes.insert_one(new_notes)

    return {"message": "notes created"}

@app.put("/notes/{note_id}")
async def update_notes(note_id: str, notes: notes, current_user: str = Depends(get_current_user)):
    await db.notes.update_one(
        {"_id": ObjectId(note_id), "user_email": current_user},
        {"$set" :{"name": notes.name, "content": notes.content}}
    )

    return {"message": "notes updated successfully"}

@app.delete("/notes/{note_id}")
async def delete_notes(note_id: str, current_user: str = Depends(get_current_user)):
    await db.notes.delete_one(
        {"_id": ObjectId(note_id), "user_email": current_user}    
    )
    return{"message": "notes deleted successfully"}