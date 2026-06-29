from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.db.models import Database, SyncJob, Schema, Table, ColumnModel, User
from app.api import deps
from app.services.sync_service import SyncService
from app.domain.schemas import SyncJobResponse

router = APIRouter()

def bg_sync_worker(database_id: str):
    """Background worker executing the sync job."""
    # Spawn a clean local session for the thread
    db = next(deps.get_db())
    try:
        SyncService.run_sync(db, database_id)
    except Exception as e:
        # Service logging handles failures, here we just prevent thread crash
        pass
    finally:
        db.close()

@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_sync(
    database_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Trigger an asynchronous metadata synchronization job.
    Returns immediately and runs extraction in a background worker thread.
    """
    # Verify database config exists
    db_config = db.query(Database).filter(Database.id == database_id).first()
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection profile not found."
        )

    # Check if there is already a running job
    running_job = db.query(SyncJob).filter(
        SyncJob.database_id == database_id,
        SyncJob.status == "RUNNING"
    ).first()
    
    if running_job:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A synchronization job is already running for this database profile."
        )

    # Trigger background execution
    background_tasks.add_task(bg_sync_worker, database_id)
    
    return {
        "status": "triggered",
        "database_id": database_id,
        "message": "Metadata synchronization started in the background."
    }

@router.get("/jobs", response_model=List[SyncJobResponse])
def get_sync_jobs(
    database_id: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Retrieve history of synchronization runs."""
    query = db.query(SyncJob)
    if database_id:
        query = query.filter(SyncJob.database_id == database_id)
    return query.order_by(SyncJob.started_at.desc()).limit(limit).all()

@router.get("/stats")
def get_global_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Compute aggregated counts across all database entities.
    Feeds the UI landing page.
    """
    db_count = db.query(Database).count()
    schema_count = db.query(Schema).count()
    
    # Exclude deleted tables and columns
    table_count = db.query(Table).filter(Table.is_deleted == False).count()
    column_count = db.query(ColumnModel).filter(ColumnModel.is_deleted == False).count()
    
    recent_jobs = db.query(SyncJob).order_by(SyncJob.started_at.desc()).limit(5).all()
    failed_jobs_count = db.query(SyncJob).filter(SyncJob.status == "FAILED").count()

    # Determine global system health based on failed jobs
    health = "100%"
    if failed_jobs_count > 0:
        total_jobs = db.query(SyncJob).count()
        if total_jobs > 0:
            health_val = max(0, int((1 - (failed_jobs_count / total_jobs)) * 100))
            health = f"{health_val}%"

    return {
        "connections": db_count,
        "schemas": schema_count,
        "tables": table_count,
        "columns": column_count,
        "health_index": health,
        "recent_runs": [
            {
                "id": str(job.id),
                "status": job.status,
                "records_synced": job.records_synced,
                "started_at": job.started_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error": job.error_message
            }
            for job in recent_jobs
        ]
    }
