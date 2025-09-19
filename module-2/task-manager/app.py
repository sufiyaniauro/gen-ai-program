from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import uuid
import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


os.makedirs("static", exist_ok=True)


app = FastAPI(title="Task Manager API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


SQLALCHEMY_DATABASE_URL = "sqlite:///./task_manager.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tasks = relationship("DBTask", back_populates="owner")

class DBTask(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("DBUser", back_populates="tasks")


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    id: Optional[int] = None
    
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str

class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime
    
    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"Client connected: {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            logger.info(f"Client disconnected: {user_id}")

    async def send_notification(self, user_id: str, message: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)
                logger.info(f"Message sent to {user_id}: {message}")

manager = ConnectionManager()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(DBUser).filter(DBUser.username == token_data.username).first()
    if not user:
        raise credentials_exception
    
    return user


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = DBUser(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User registered: {user.username}")
    return {"message": "User registered successfully"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=Task)
async def create_task(task_create: TaskCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    db_task = DBTask(
        id=task_id,
        title=task_create.title,
        description=task_create.description,
        owner_id=current_user.id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    

    task_dict = {
        "id": db_task.id,
        "title": db_task.title, 
        "description": db_task.description,
        "completed": db_task.completed,
        "created_at": db_task.created_at
    }
    

    await manager.send_notification(
        current_user.username,
        json.dumps({"action": "create", "task": task_dict}, cls=CustomJSONEncoder)
    )
    
    logger.info(f"Task created: {task_id} by user {current_user.username}")
    return task_dict

@app.get("/tasks", response_model=List[Task])
async def read_tasks(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(DBTask).filter(DBTask.owner_id == current_user.id).all()
    
    logger.info(f"Retrieved tasks for user {current_user.username}")
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
async def read_task(task_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(DBTask).filter(DBTask.id == task_id, DBTask.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    logger.info(f"Retrieved task {task_id} for user {current_user.username}")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(DBTask).filter(DBTask.id == task_id, DBTask.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    

    task_dict = {
        "id": task.id,
        "title": task.title, 
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at
    }
    

    await manager.send_notification(
        current_user.username,
        json.dumps({"action": "update", "task": task_dict}, cls=CustomJSONEncoder)
    )
    
    logger.info(f"Updated task {task_id} by user {current_user.username}")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(DBTask).filter(DBTask.id == task_id, DBTask.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    

    await manager.send_notification(
        current_user.username,
        json.dumps({"action": "delete", "task_id": task_id})
    )
    
    logger.info(f"Deleted task {task_id} by user {current_user.username}")
    return


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        user = db.query(DBUser).filter(DBUser.username == username).first()
        if not user:
            await websocket.close(code=1008)  
            return
        
        await manager.connect(websocket, username)
        
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket, username)
    
    except JWTError:
        await websocket.close(code=1008)  

@app.get("/")
async def get_index():
    return {"message": "Task Manager API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
