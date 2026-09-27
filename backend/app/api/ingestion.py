from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.recurring import RecurringTransaction
from app.schemas.transaction import TransactionBatchResponse
from app.services.csv_parser import CSVParser
from app.services.anomaly_detector import AnomalyDetector
from app.services.recurring_detector import RecurringDetector

router = APIRouter(prefix="/ingestion", tags=["Data Ingestion"])


@router.post("/upload", response_model=TransactionBatchResponse)
async def upload_bank_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and parse bank statement CSV files.
    Standardizes dates, formats amounts, categorizes transactions,
    runs statistical anomaly detection, and stores the records.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a standard CSV file."
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded CSV file is empty."
        )

    try:
        raw_transactions = CSVParser.parse_csv_content(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse CSV statement: {str(e)}"
        )

    if not raw_transactions:
        return TransactionBatchResponse(
            total_parsed=0,
            total_saved=0,
            anomalies_detected=0,
            message="No valid transaction rows found in the uploaded file."
        )

    # Run anomaly detection
    annotated = AnomalyDetector.detect_anomalies(raw_transactions)

    saved_records = []
    anomalies_count = 0

    for item in annotated:
        is_anom = item.get("is_anomaly", False)
        if is_anom:
            anomalies_count += 1

        tx = Transaction(
            user_id=current_user.id,
            date=item["date"],
            description=item["description"],
            merchant=item.get("merchant"),
            amount=item["amount"],
            category=item.get("category", "Uncategorized"),
            is_anomaly=is_anom,
            anomaly_score=item.get("anomaly_score"),
            anomaly_reason=item.get("anomaly_reason"),
        )
        db.add(tx)
        saved_records.append(tx)

    db.commit()

    # Re-evaluate recurring transactions for this user
    all_user_txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.asc())
        .all()
    )

    tx_dicts = [
        {
            "date": t.date,
            "merchant": t.merchant or t.description,
            "amount": t.amount,
            "category": t.category,
            "description": t.description,
        }
        for t in all_user_txs
    ]

    detected_recurring = RecurringDetector.detect_recurring(tx_dicts)

    # Upsert recurring transactions
    # Clear existing detected recurring patterns and refresh with latest analysis
    db.query(RecurringTransaction).filter(RecurringTransaction.user_id == current_user.id).delete()
    for rec in detected_recurring:
        db.add(
            RecurringTransaction(
                user_id=current_user.id,
                merchant=rec["merchant"],
                category=rec["category"],
                average_amount=rec["average_amount"],
                cadence=rec["cadence"],
                interval_days=rec["interval_days"],
                occurrence_count=rec["occurrence_count"],
                last_date=rec["last_date"],
                next_expected_date=rec["next_expected_date"],
                is_active=True,
            )
        )
    db.commit()

    return TransactionBatchResponse(
        total_parsed=len(raw_transactions),
        total_saved=len(saved_records),
        anomalies_detected=anomalies_count,
        message=f"Successfully imported {len(saved_records)} transactions. Detected {anomalies_count} anomalies."
    )
