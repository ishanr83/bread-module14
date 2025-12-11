from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from .database import engine, get_db, Base
from .models import User, Calculation
from .schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    CalculationCreate, CalculationUpdate, CalculationResponse, CalculationList
)
from .auth import hash_password, verify_password, create_access_token, get_current_user, get_required_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BREAD Calculator API - Module 14", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

def perform_calculation(operation: str, a: float, b: float) -> float:
    ops = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else None
    }
    result = ops.get(operation, lambda x, y: None)(a, b)
    if result is None:
        raise ValueError("Invalid operation or division by zero")
    return result

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/login")
async def login_page():
    return FileResponse("static/login.html")

@app.get("/register")
async def register_page():
    return FileResponse("static/register.html")

@app.get("/dashboard")
async def dashboard_page():
    return FileResponse("static/dashboard.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/register", response_model=Token, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username taken")
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_required_user)):
    return user

@app.get("/api/calculations", response_model=CalculationList)
async def browse_calculations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    operation: Optional[str] = None,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    query = db.query(Calculation)
    if user:
        query = query.filter(Calculation.user_id == user.id)
    if operation:
        query = query.filter(Calculation.operation == operation)
    total = query.count()
    calculations = query.order_by(Calculation.created_at.desc()).offset(skip).limit(limit).all()
    return CalculationList(calculations=calculations, total=total)

@app.get("/api/calculations/{calc_id}", response_model=CalculationResponse)
async def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc

@app.put("/api/calculations/{calc_id}", response_model=CalculationResponse)
async def edit_calculation(calc_id: int, update: CalculationUpdate, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    operation = update.operation.value if update.operation else calc.operation
    operand_a = update.operand_a if update.operand_a is not None else calc.operand_a
    operand_b = update.operand_b if update.operand_b is not None else calc.operand_b
    if operation == "divide" and operand_b == 0:
        raise HTTPException(status_code=400, detail="Cannot divide by zero")
    result = perform_calculation(operation, operand_a, operand_b)
    calc.operation = operation
    calc.operand_a = operand_a
    calc.operand_b = operand_b
    calc.result = result
    db.commit()
    db.refresh(calc)
    return calc

@app.post("/api/calculations", response_model=CalculationResponse, status_code=201)
async def add_calculation(
    calc: CalculationCreate,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    operation = calc.operation.value
    result = perform_calculation(operation, calc.operand_a, calc.operand_b)
    db_calc = Calculation(
        operation=operation,
        operand_a=calc.operand_a,
        operand_b=calc.operand_b,
        result=result,
        user_id=user.id if user else None
    )
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc

@app.delete("/api/calculations/{calc_id}", status_code=204)
async def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(calc)
    db.commit()
    return None
