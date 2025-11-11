from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.friend import Friend
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseResponse, BalanceResponse
from app.dependencies import get_current_user
from app.services.pdf_service import pdf_service

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


@router.get(
    "/{friend_id}/pdf",
    summary="Download expense report as PDF",
    description="""
    Generate and download a PDF report of all expenses with a friend.
    
    **PDF Includes:**
    - Report generation date and time
    - Balance summary (who owes whom)
    - Detailed expense list with dates, descriptions, amounts
    - Total expenses amount
    - Professional formatting
    
    **Response:**
    - Returns PDF file
    - Filename: expense-report-{friend_id}-{date}.pdf
    - Content-Type: application/pdf
    """
)
def download_expense_pdf(
    friend_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download expense report as PDF
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
    
    # Get friend user details
    friend_user = db.query(User).filter(User.id == friend_id).first()
    if not friend_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend user not found"
        )
    
    # Get all expenses between current user and friend
    expenses = db.query(Expense).filter(
        or_(
            and_(Expense.user_a_id == current_user.id, Expense.user_b_id == friend_id),
            and_(Expense.user_a_id == friend_id, Expense.user_b_id == current_user.id)
        )
    ).order_by(Expense.expense_date.desc(), Expense.created_at.desc()).all()
    
    # Calculate balance
    balance = Decimal(0)
    for expense in expenses:
        if expense.paid_by_user_id == current_user.id:
            balance += expense.amount
        else:
            balance -= expense.amount
    
    # Convert expenses to dictionary format for PDF service
    expenses_data = []
    for expense in expenses:
        expense_dict = ExpenseResponse.from_orm_expense(expense).model_dump()
        expenses_data.append(expense_dict)
    
    # Generate PDF
    pdf_buffer = pdf_service.generate_expense_report(
        expenses=expenses_data,
        current_user_name=current_user.name or current_user.email,
        friend_name=friend_user.name or friend_user.email,
        balance=float(balance),
        currency_symbol="₹"
    )
    
    # Generate filename
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"expense-report-{friend_id}-{date_str}.pdf"
    
    # Return PDF as streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

