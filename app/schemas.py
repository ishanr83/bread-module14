from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain a letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain a number')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class OperationType(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"

class CalculationCreate(BaseModel):
    operation: OperationType
    operand_a: float
    operand_b: float

class CalculationUpdate(BaseModel):
    operation: Optional[OperationType] = None
    operand_a: Optional[float] = None
    operand_b: Optional[float] = None

class CalculationResponse(BaseModel):
    id: int
    operation: str
    operand_a: float
    operand_b: float
    result: float
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class CalculationList(BaseModel):
    calculations: List[CalculationResponse]
    total: int
