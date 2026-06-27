import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import Database, User
from app.api import deps
from app.core.encrypt import encrypt_data
from app.domain.schemas import ConnectionConfigCreate, ConnectionConfigResponse, ConnectionTestRequest

router = APIRouter()

@router.post("/connection", response_model=ConnectionConfigResponse, status_code=status.HTTP_201_CREATED)
def create_connection(
    payload: ConnectionConfigCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Encrypt and save a Snowflake connection configuration profile.
    Requires valid JWT authentication.
    """
    # Check if a connection with the same name already exists
    existing = db.query(Database).filter(Database.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A connection configuration with this name already exists."
        )

    # Convert the config payload to a JSON string and encrypt it
    config_json_str = json.dumps(payload.config)
    encrypted_config = encrypt_data(config_json_str)

    # Create the database record
    new_db = Database(
        name=payload.name,
        platform=payload.platform,
        connection_config=encrypted_config
    )
    
    db.add(new_db)
    db.commit()
    db.refresh(new_db)
    
    return new_db

@router.get("/connection", response_model=List[ConnectionConfigResponse])
def list_connections(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all configured database connections.
    Credential parameters are excluded from the return payload for security.
    """
    connections = db.query(Database).all()
    return connections

@router.post("/connection/test")
def test_connection(
    payload: ConnectionTestRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Verify connection settings. Returns a mock success status for Spec 001.
    """
    # Mock validation for foundation sprint
    if payload.platform != "snowflake":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only 'snowflake' platform is supported in this release."
        )
        
    config = payload.config
    required_keys = ["account", "username", "warehouse"]
    missing = [k for k in required_keys if k not in config or not config[k]]
    
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required connection fields: {', '.join(missing)}"
        )
        
    return {
        "status": "success",
        "message": "Connection properties validated successfully (mocked)."
    }
