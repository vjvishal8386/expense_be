from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_a_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_b_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=False)
    paid_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expense_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Check constraint to ensure paid_by_user_id is either user_a_id or user_b_id
    __table_args__ = (
        CheckConstraint(
            '(paid_by_user_id = user_a_id) OR (paid_by_user_id = user_b_id)',
            name='paid_by_must_be_user_a_or_b'
        ),
    )

    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, description={self.description})>"

