from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.auth.schemas import SignupRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    refresh_token_expiry,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup")
def signup(data: SignupRequest):
    if not data.email.endswith("@gmail.com"):
        raise HTTPException(
            status_code=400,
            detail="Only Gmail allowed",
        )

    db = SessionLocal()

    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return {
        "message": "User registered successfully",
        "user_id": user.id,
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not user or not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        {"sub": str(user.id)},
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_token(refresh_token: str):
    db = SessionLocal()

    token_entry = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked == False,
        )
        .first()
    )

    if not token_entry or token_entry.expires_at < refresh_token_expiry(days=0):
        db.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    token_entry.revoked = True

    new_refresh = create_refresh_token()

    db.add(
        RefreshToken(
            user_id=token_entry.user_id,
            token=new_refresh,
            expires_at=refresh_token_expiry(),
            revoked=False,
        )
    )

    access_token = create_access_token(
        data={"sub": str(token_entry.user_id)},
    )

    db.commit()
    db.close()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(refresh_token: str):
    db = SessionLocal()

    token_entry = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    if token_entry:
        token_entry.revoked = True
        db.commit()

    db.close()

    return {
        "message": "Logged out successfully",
    }
