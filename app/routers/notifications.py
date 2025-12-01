from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.device_token import DeviceToken
from app.services.notification_service import subscribe_token_to_topic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class SubscriptionRequest(BaseModel):
    token: str
    project_code: str


class DeviceTokenCreate(BaseModel):
    token: str
    platform: str  # 'web', 'ios', 'android'
    device_info: Optional[dict] = None


class DeviceTokenResponse(BaseModel):
    id: UUID
    platform: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/subscribe", status_code=status.HTTP_200_OK)
async def subscribe(request: SubscriptionRequest):
    """
    Subscribe device token to a topic (for group/project notifications)
    """
    try:
        topic = f"project_{request.project_code}"
        count = subscribe_token_to_topic(request.token, topic)
        return {"status": "success", "subscribed_count": count}
    except Exception as e:
        logger.error(f"Error subscribing to topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register-device", response_model=DeviceTokenResponse, status_code=status.HTTP_201_CREATED)
def register_device_token(
    token_data: DeviceTokenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a device token for push notifications.
    Called by frontend when user grants notification permission.
    """
    try:
        # Check if token already exists for this user
        existing_token = db.query(DeviceToken).filter(
            DeviceToken.user_id == current_user.id,
            DeviceToken.token == token_data.token
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.is_active = True
            existing_token.platform = token_data.platform
            existing_token.device_info = token_data.device_info
            db.commit()
            db.refresh(existing_token)
            return DeviceTokenResponse(
                id=existing_token.id,
                platform=existing_token.platform,
                is_active=existing_token.is_active,
                created_at=existing_token.created_at.isoformat()
            )
        
        # Create new token
        new_token = DeviceToken(
            user_id=current_user.id,
            token=token_data.token,
            platform=token_data.platform,
            device_info=token_data.device_info,
            is_active=True
        )
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        
        return DeviceTokenResponse(
            id=new_token.id,
            platform=new_token.platform,
            is_active=new_token.is_active,
            created_at=new_token.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error registering device token: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register device token: {str(e)}"
        )


@router.delete("/device/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def unregister_device_token(
    token_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unregister a device token (user logged out or uninstalled app)
    """
    device_token = db.query(DeviceToken).filter(
        DeviceToken.id == token_id,
        DeviceToken.user_id == current_user.id
    ).first()
    
    if not device_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    
    # Mark as inactive instead of deleting (for analytics)
    device_token.is_active = False
    db.commit()
    return None


@router.get("/devices", response_model=list[DeviceTokenResponse])
def get_my_device_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active device tokens for current user
    """
    tokens = db.query(DeviceToken).filter(
        DeviceToken.user_id == current_user.id,
        DeviceToken.is_active == True
    ).all()
    
    return [
        DeviceTokenResponse(
            id=token.id,
            platform=token.platform,
            is_active=token.is_active,
            created_at=token.created_at.isoformat()
        )
        for token in tokens
    ]
