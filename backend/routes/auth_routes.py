from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from urllib.parse import urlencode
from config import config
from models.user import Base, Role, LoginType
from schemas.user import UserCreate, UserLogin, Token, EmailRequest, OTPVerification
from services.auth_service import AuthService
from sqlalchemy.orm import sessionmaker
from utils.auth import get_current_user, create_access_token
from models.user import User
from schemas.user import ClassUpdate
from schemas.user import UserOut
from typing import List
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from fastapi.responses import RedirectResponse , JSONResponse
from utils.auth import create_access_token, get_password_hash
from config import config
import secrets
import logging
from datetime import timedelta
from fastapi import BackgroundTasks
import time
import functools
import asyncio
import statistics
from collections import defaultdict
from database import engine, SessionLocal, get_pool_status

logger = logging.getLogger(__name__)

# Global timing storage for analysis
timing_data = defaultdict(list)

# Tạo bảng
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def track_execution_time(route_name: str):
    """Decorator to track execution time of routes"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"[{route_name}] Starting execution at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                result = await func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                timing_data[route_name].append(execution_time)
                logger.info(f"[{route_name}] Completed successfully in {execution_time:.4f} seconds")
                return result
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                timing_data[route_name].append(execution_time)
                logger.error(f"[{route_name}] Failed after {execution_time:.4f} seconds with error: {str(e)}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"[{route_name}] Starting execution at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                timing_data[route_name].append(execution_time)
                logger.info(f"[{route_name}] Completed successfully in {execution_time:.4f} seconds")
                return result
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                timing_data[route_name].append(execution_time)
                logger.error(f"[{route_name}] Failed after {execution_time:.4f} seconds with error: {str(e)}")
                raise
        
        # Return async wrapper for async functions, sync wrapper for sync functions
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def get_timing_summary():
    """Get timing statistics for all tracked routes"""
    summary = {}
    for route_name, times in timing_data.items():
        if times:
            summary[route_name] = {
                "count": len(times),
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                "total_time": sum(times),
                "avg_time": sum(times) / len(times)
            }
    return summary

@router.get("/timing-stats")
def get_timing_statistics():
    """Endpoint to get timing statistics for performance analysis"""
    summary = get_timing_summary()
    return {
        "message": "Timing statistics for authentication routes",
        "data": summary,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

@router.get("/pool-status")
def get_database_pool_status():
    """Get database connection pool status for monitoring"""
    pool_status = get_pool_status()
    return {
        "message": "Database pool status",
        "data": pool_status,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

@router.post("/register", response_model=Token)
@track_execution_time("REGISTER")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(user, db)

@router.post("/login", response_model=Token)
@track_execution_time("LOGIN")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login_user(user.email, user.password, db)

@router.post("/request-otp")
@track_execution_time("REQUEST_OTP")
async def request_otp(email_request: EmailRequest, background_tasks: BackgroundTasks):
    return await AuthService.request_otp(email_request.email, background_tasks)

@router.post("/verify-otp")
@track_execution_time("VERIFY_OTP")
async def verify_otp(otp_verification: OTPVerification, db: Session = Depends(get_db)):
    return await AuthService.verify_otp(otp_verification.email, otp_verification.otp, db)

@router.get("/me", response_model=UserOut)
@track_execution_time("GET_ME")
def get_logged_in_user(current_user: User = Depends(get_current_user)):
    return UserOut.from_orm_with_role_name(current_user)

class UpdateClassName(BaseModel):
    class_name: List[str]

@router.put("/me/class-name")
@track_execution_time("UPDATE_CLASS_NAME")
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
@track_execution_time("GOOGLE_LOGIN")
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

@router.get("/google/callback", response_model=None)
@track_execution_time("GOOGLE_CALLBACK")
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
            generated_password = secrets.token_hex(16)
            user = User(
                email=userinfo["email"],
                full_name=userinfo.get("name"),
                hashed_password=AuthService.hash_password(generated_password),
                login_type="google",
                oauth_id=userinfo.get("sub"),
                role=Role.STUDENT.value
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 3. Tạo JWT token với sub là email
        access_token = create_access_token(
            data={
                "sub": user.email,
                "email": user.email,
                "role": Role(user.role).name,
                "login_type": user.login_type.value
            },
            expires_delta=timedelta(hours=24)
        )

        # 4. Redirect về frontend với token
        params = urlencode({
            "token": access_token,
            "email": user.email,
            "role": Role(user.role).name,
            "login_type": user.login_type
        })

        redirect_url = f"https://edu.aidia.vn/oauth-callback.html?{params}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"Google callback error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xác thực Google: {str(e)}"
        )

oauth.register(
    name='facebook',
    client_id=config.FACEBOOK_CLIENT_ID,
    client_secret=config.FACEBOOK_CLIENT_SECRET,
    access_token_url='https://graph.facebook.com/v19.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v19.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v19.0/',
    userinfo_endpoint='me?fields=id,name,email',
    client_kwargs={'scope': 'email public_profile'},
)

@router.get("/facebook/login")
@track_execution_time("FACEBOOK_LOGIN")
async def login_via_facebook(request: Request):
    try:
        redirect_uri = config.FACEBOOK_REDIRECT_URI
        if not redirect_uri:
            logger.error("Facebook redirect URI not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error"
            )
        
        # Debugging session
        request.session['facebook_csrf_test'] = 'hello_world'
        logger.info(f"Session before redirect: {request.session}")

        return await oauth.facebook.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Facebook login redirect failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Facebook login"
        )

@router.get("/facebook/callback", response_model=Token)
@track_execution_time("FACEBOOK_CALLBACK")
async def facebook_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.facebook.authorize_access_token(request)
        profile = await oauth.facebook.userinfo(token=token)

        fb_id = profile.get("id")
        email = profile.get("email") or f"{fb_id}@facebook.com"

        user = db.query(User).filter(User.email == email).first()
        if not user:
            generated_password = secrets.token_hex(16)
            user = User(
                email=email,
                full_name=profile.get("name", "Facebook User"),
                hashed_password=get_password_hash(generated_password),
                login_type="facebook",
                oauth_id=fb_id,
                role=Role.STUDENT.value,
                verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(
            data={
                "sub": user.email,
                "email": user.email,
                "role": Role(user.role).name,
                "login_type": user.login_type.value if hasattr(user.login_type, 'value') else str(user.login_type)
            },
            expires_delta=timedelta(hours=24)
        )

        params = urlencode({
            "token": access_token,
            "email": user.email,
            "role": Role(user.role).name,
            "login_type": user.login_type.value if hasattr(user.login_type, 'value') else str(user.login_type)
        })

        redirect_url = f"https://edu.aidia.vn/oauth-callback.html?{params}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"Facebook callback error: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xác thực Facebook: {str(e)}"
        )



