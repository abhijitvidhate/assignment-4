import sqlite3
import os
import bcrypt
from fastapi import FastAPI, HTTPException, Depends, Request, Header, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt

logging.basicConfig(level=logging.ERROR, force=True)

app = FastAPI()
DB_PATH = os.environ.get("SQLITE_DB_PATH", "sqlite.db")
SECRET_KEY = "robosecret"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    conn.commit()
    conn.close()

# Auto-initialize DB at service startup
init_db()

class User(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(user: User):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username=?", (user.username,))
    row = c.fetchone()
    conn.close()
    if not row or not bcrypt.checkpw(user.password.encode(), row[0].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"username": user.username}, SECRET_KEY, algorithm="HS256")
    return {"token": token}

@app.get("/verify")
def verify(token: str = Query(...)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_aud": False})
        return {"valid": True}
    except Exception as e:
        print(f"JWT verify error: {e}", flush=True)
        return {"valid": False}

@app.get("/users")
def get_users(authorization: str = Header(None)):
    print(f"Authorization header: {authorization}", flush=True)
    if not authorization or not authorization.startswith("Bearer "):
        print("Missing or invalid Authorization header", flush=True)
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    print(f"Raw JWT token received: {token}", flush=True)
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_aud": False})
    except Exception as e:
        print(f"JWT decode error: {e}", flush=True)
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    users = [row[0] for row in c.execute("SELECT username FROM users")]
    conn.close()
    return {"users": users}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/register")
def register(user: User):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username=?", (user.username,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user.username, password_hash))
    conn.commit()
    conn.close()
    return {"message": "User registered"}