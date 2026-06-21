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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#loding environment variable 
load_dotenv()

app = FastAPI()
app.add_middleware(
    
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://notes-frontend.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
    
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