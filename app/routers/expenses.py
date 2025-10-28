from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.friend import Friend
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseResponse, BalanceResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/{friend_id}", response_model=List[ExpenseResponse])
def get_expenses_with_friend(
    friend_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all expenses between current user and a specific friend
    """
    # Verify friend relationship exists
    friendship = db.query(Friend).filter(
        Friend.user_id == current_user.id,
        Friend.friend_id == friend_id
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend not found"
        )
    
    # Get all expenses between current user and friend (both directions)
    expenses = db.query(Expense).filter(
        or_(
            and_(Expense.user_a_id == current_user.id, Expense.user_b_id == friend_id),
            and_(Expense.user_a_id == friend_id, Expense.user_b_id == current_user.id)
        )
    ).order_by(Expense.expense_date.desc(), Expense.created_at.desc()).all()
    
    return [ExpenseResponse.from_orm_expense(expense) for expense in expenses]


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new expense between current user and a friend
    """
    # Verify friend relationship exists
    friendship = db.query(Friend).filter(
        Friend.user_id == current_user.id,
        Friend.friend_id == expense_data.friend_id
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend not found"
        )
    
    # Verify paid_by_user_id is either current user or friend
    if expense_data.paid_by_user_id not in [current_user.id, expense_data.friend_id]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="paid_by_user_id must be either current user or friend"
        )
    
    # Create expense with user_a_id = current_user, user_b_id = friend
    new_expense = Expense(
        user_a_id=current_user.id,
        user_b_id=expense_data.friend_id,
        amount=Decimal(str(expense_data.amount)),
        description=expense_data.description,
        paid_by_user_id=expense_data.paid_by_user_id,
        expense_date=expense_data.expense_date
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return ExpenseResponse.from_orm_expense(new_expense)


@router.get("/{friend_id}/balance", response_model=BalanceResponse)
def get_balance_with_friend(
    friend_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get balance between current user and a friend
    Positive balance = friend owes current user
    Negative balance = current user owes friend
    """
    # Verify friend relationship exists
    friendship = db.query(Friend).filter(
        Friend.user_id == current_user.id,
        Friend.friend_id == friend_id
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend not found"
        )
    
    # Get all expenses between current user and friend
    expenses = db.query(Expense).filter(
        or_(
            and_(Expense.user_a_id == current_user.id, Expense.user_b_id == friend_id),
            and_(Expense.user_a_id == friend_id, Expense.user_b_id == current_user.id)
        )
    ).all()
    
    # Calculate balance
    balance = Decimal(0)
    for expense in expenses:
        if expense.paid_by_user_id == current_user.id:
            # Current user paid, so friend owes them
            balance += expense.amount
        else:
            # Friend paid, so current user owes friend
            balance -= expense.amount
    
    return BalanceResponse(balance=float(balance))

