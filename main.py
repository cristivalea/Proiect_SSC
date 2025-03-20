from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta


SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "admin": {"username": "admin", "password": "1234", "role": "admin"},
    "user": {"username": "user", "password": "1234", "role": "user"}
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") # endpoint unde se trimite nume si parola pentru tpken
#creare aplicatie FastAPI
app = FastAPI()


#definirea unui endpoint principal
@app.get("/")
def read_root():
    return {"message": "API is working!"}


#creare token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


#endpoint pentru autentificare
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}



#verifica si decodeaza token JWT
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


#endpoint pentru lista de studenti
@app.get("/students")
def get_students(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    students = [
        {"id": 1, "name": "Ana", "email": "ana@example.com", "age": 22},
        {"id": 2, "name": "Mihai", "email": "mihai@example.com", "age": 23},
        {"id": 3, "name": "Elena", "email": "elena@example.com", "age": 21}
    ]
    return {"students": students}


#endpoint pentru inregistrare
@app.post("/register")
def register(username: str, password: str, role: str = "user"):
    if username in fake_users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    fake_users_db[username] = {"username": username, "password": password, "role": role}
    return {"message": "User registered successfully"}


#endpoint pentru profilul utilizatorului autentificat
@app.get("/profile")
def get_profile(user: dict = Depends(get_current_user)):
    return {"username": user["username"], "role": user["role"]}
