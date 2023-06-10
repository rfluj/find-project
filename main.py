from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

app = FastAPI()

# MySQL database connection
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:mypassword@localhost/findProjects"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SECRET_KEY = "my-secret-key"  # Change this to your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encode_token(user_id: int):
    payload = {"user_id": user_id}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(100))

    projects = relationship("Project", back_populates="owner")

#  Project model
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(String(255))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="projects")

# form models
class ProjectCreate(BaseModel):
    title: str
    description: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# connect to database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create tables in database if not exist
Base.metadata.create_all(bind=engine)

def get_token(username: str, password: str, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(user.username)
    return access_token

def get_current_user(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.expunge(user)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid username")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"exp": expire, "sub": username}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
def register_user(user: UserCreate, db: SessionLocal = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    password_hash = pwd_context.hash(user.password)
    new_user = User(username=user.username, email=user.email, password_hash=password_hash)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = encode_token(new_user.id)
    return {"message": "User registered successfully", "access_token": Token(access_token=token, token_type="bearer")}

@app.post("/login")
def login_user(user: UserLogin, db: SessionLocal = Depends(get_db)):
    token = get_token(user.username, user.password, db)
    return {"message": "login successfully", "access_token": Token(access_token=token, token_type="bearer")}

@app.post("/projects")
def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    new_project = Project(title=project.title, description=project.description, owner=current_user)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.get("/projects/{project_id}")
def get_project(project_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}
