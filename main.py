from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
import pymysql


# Configurare cheie secretă și algoritm JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
app = FastAPI()

# Conectare la baza de date
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "studenti"
}

@app.get("/")
def read_root():
    return {"message": "API is working!"}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


# Funcție pentru generare token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (form_data.username, form_data.password))
    user = cursor.fetchone()
    db.close()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": form_data.username, "role": user[0]})
    return {"access_token": access_token, "token_type": "bearer"}


# Funcție pentru validare token JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get("/students")
def get_students(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # db = get_db_connection()
    # cursor = db.cursor()
    # cursor.execute("SELECT * FROM students")
    # students = cursor.fetchall()
    # db.close()
    students = [
        {"id": 1, "name": "Ana", "email": "ana@example.com", "age": 22},
        {"id": 2, "name": "Mihai", "email": "mihai@example.com", "age": 23},
        {"id": 3, "name": "Elena", "email": "elena@example.com", "age": 21}
    ]

    return {"students": students}
