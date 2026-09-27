from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse

router = APIRouter(prefix="/goals", tags=["Savings Goals"])


def enrich_goal(goal: Goal) -> GoalResponse:
    """
    Calculate progress percentage, remaining balance, and required monthly contribution.
    """
    target = max(goal.target_amount, 1.0)
    current = max(goal.current_amount, 0.0)
    progress_pct = min(round((current / target) * 100.0, 1), 100.0)
    remaining = max(round(target - current, 2), 0.0)

    monthly_needed = None
    if goal.target_date and goal.target_date > date.today() and remaining > 0:
        months_left = max((goal.target_date - date.today()).days / 30.4, 1.0)
        monthly_needed = round(remaining / months_left, 2)

    return GoalResponse(
        id=goal.id,
        user_id=goal.user_id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        category=goal.category,
        status=goal.status,
        progress_percentage=progress_pct,
        remaining_amount=remaining,
        monthly_savings_needed=monthly_needed,
        created_at=goal.created_at,
    )


@router.get("/", response_model=List[GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all savings targets and calculate goal completion trajectories.
    """
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.created_at.desc()).all()
    return [enrich_goal(g) for g in goals]


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_in: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new savings target goal.
    """
    goal = Goal(
        user_id=current_user.id,
        name=goal_in.name,
        target_amount=goal_in.target_amount,
        current_amount=goal_in.current_amount or 0.0,
        target_date=goal_in.target_date,
        category=goal_in.category or "General Savings",
        status="in_progress",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return enrich_goal(goal)


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update goal attributes or contribute funds towards target.
    """
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found.")

    update_data = goal_update.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(goal, field, val)

    if goal.current_amount >= goal.target_amount:
        goal.status = "achieved"

    db.commit()
    db.refresh(goal)
    return enrich_goal(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a savings goal.
    """
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found.")

    db.delete(goal)
    db.commit()
    return None
