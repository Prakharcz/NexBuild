from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.services.categorizer import categorizer

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    search: Optional[str] = None,
    anomaly_only: Optional[bool] = None,
):
    """
    Retrieve paginated transactions with optional keyword search, category filter,
    and anomaly detection toggle.
    """
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if category and category.lower() != "all":
        query = query.filter(Transaction.category == category)

    if anomaly_only:
        query = query.filter(Transaction.is_anomaly == True)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(search_pattern),
                Transaction.merchant.ilike(search_pattern),
                Transaction.category.ilike(search_pattern),
            )
        )

    transactions = (
        query.order_by(Transaction.date.desc(), Transaction.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually create a new financial transaction with auto-categorization fallback.
    """
    # Auto categorize if category wasn't explicitly selected
    category = tx_in.category
    merchant = tx_in.merchant
    if not category or category == "Uncategorized":
        auto_cat, auto_merch = categorizer.categorize(tx_in.description, tx_in.amount)
        category = auto_cat
        if not merchant:
            merchant = auto_merch

    tx = Transaction(
        user_id=current_user.id,
        date=tx_in.date,
        description=tx_in.description,
        merchant=merchant or tx_in.description[:50],
        amount=round(tx_in.amount, 2),
        category=category,
        is_recurring=tx_in.is_recurring or False,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    tx_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a transaction (e.g. user manually overrides the auto-assigned category).
    """
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")

    update_data = tx_update.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(tx, field, val)

    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a specific transaction.
    """
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")

    db.delete(tx)
    db.commit()
    return None
