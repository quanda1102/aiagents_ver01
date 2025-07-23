from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from config import config
from models.user import Base, Role, LoginType
from schemas.user import UserCreate, UserLogin, Token
from services.auth_service import AuthService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.auth import get_current_user, create_access_token
from models.user import User
from schemas.user import ClassUpdate
from schemas.user import UserOut
from typing import List
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from fastapi.responses import RedirectResponse , JSONResponse
from config import config
import secrets
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# Kết nối CSDL
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo bảng
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(user, db)

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login_user(user.email, user.password, db)

@router.get("/me", response_model=UserOut)
def get_logged_in_user(current_user: User = Depends(get_current_user)):
    return UserOut.from_orm_with_role_name(current_user)

class UpdateClassName(BaseModel):
    class_name: List[str]

@router.put("/me/class-name")
async def update_class_name(
    update: UpdateClassName,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.class_name = update.class_name
    db.commit()
    return {"message": "Class names updated successfully"}

oauth = OAuth()
oauth.register(
    name='google',
    client_id=config.GOOGLE_CLIENT_ID,
    client_secret=config.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/google/login")
async def login_via_google(request: Request):
    try:
        redirect_uri = config.GOOGLE_REDIRECT_URI
        if not redirect_uri:
            logger.error("Google redirect URI not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error"
            )
            
        return await oauth.google.authorize_redirect(request, redirect_uri)
        
    except Exception as e:
        logger.error(f"Google login redirect failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login"
        )

@router.get("/google/callback", response_model=Token)
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        # 1. Xác thực với Google và lấy thông tin user
        token = await oauth.google.authorize_access_token(request)
        userinfo = await oauth.google.userinfo(token=token)
        
        if not userinfo.get("email"):
            raise HTTPException(
                status_code=400,
                detail="Không nhận được email từ Google"
            )

        # 2. Tìm hoặc tạo user trong database
        user = db.query(User).filter(User.email == userinfo["email"]).first()
        if not user:
            user = User(
                email=userinfo["email"],
                full_name=userinfo.get("name"),
                login_type="google",
                oauth_id=userinfo.get("sub"),
                role=Role.STUDENT.value  # Default role
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 3. Tạo JWT token với thông tin phân quyền
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": Role(user.role).name,
                "login_type": user.login_type.value if isinstance(user.login_type, LoginType) else user.login_type
            },
            expires_delta=timedelta(hours=24)  # Token hết hạn sau 24h
        )

        # 4. Trả về token dạng JSON
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "email": user.email,
                "role": Role(user.role).name
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xác thực Google: {str(e)}"
        )

oauth.register(
    name='facebook',
    client_id=config.FACEBOOK_CLIENT_ID,
    client_secret=config.FACEBOOK_CLIENT_SECRET,
    access_token_url='https://graph.facebook.com/v19.0/oauth/access_token',
    access_token_params=None,
    authorize_url='https://www.facebook.com/v19.0/dialog/oauth',
    authorize_params=None,
    api_base_url='https://graph.facebook.com/v19.0/',
    client_kwargs={'scope': 'email public_profile'},
)

@router.get("/facebook/login")
async def login_via_facebook(request: Request):
    redirect_uri = config.FACEBOOK_REDIRECT_URI
    return await oauth.facebook.authorize_redirect(request, redirect_uri)

@router.get("/facebook/callback")
async def facebook_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.facebook.authorize_access_token(request)
    resp = await oauth.facebook.get("me?fields=id,name,email,picture{url}", token=token)
    profile = resp.json()

    email = profile.get("email")
    name = profile.get("name")
    picture = profile.get("picture", {}).get("data", {}).get("url")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Facebook response")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name, avatar=picture)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    redirect_url = f"{config.FRONTEND_URL}/oauth-callback?token={access_token}"
    return RedirectResponse(url=redirect_url)



