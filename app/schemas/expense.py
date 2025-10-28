from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import date
from decimal import Decimal


class ExpenseCreate(BaseModel):
    friend_id: UUID
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    description: str = Field(..., min_length=1, max_length=500)
    paid_by_user_id: UUID
    expense_date: date

    @field_validator('description')
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()


class ExpenseResponse(BaseModel):
    id: UUID
    userAId: UUID
    userBId: UUID
    amount: float
    description: str
    paidByUserId: UUID
    date: date

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_expense(cls, expense):
        """Convert SQLAlchemy Expense model to response schema"""
        return cls(
            id=expense.id,
            userAId=expense.user_a_id,
            userBId=expense.user_b_id,
            amount=float(expense.amount),
            description=expense.description,
            paidByUserId=expense.paid_by_user_id,
            date=expense.expense_date
        )


class BalanceResponse(BaseModel):
    balance: float

