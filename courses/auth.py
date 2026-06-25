# courses/auth.py

import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

from ninja import Router, Schema
from ninja.security import HttpBearer

from .models import User

auth_router = Router()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ==================================
# SCHEMAS
# ==================================

class RegisterSchema(Schema):
    username: str
    password: str
    role: str = "student"


class LoginSchema(Schema):
    username: str
    password: str


class RefreshSchema(Schema):
    refresh_token: str


class UpdateProfileSchema(Schema):
    username: str | None = None
    password: str | None = None


# ==================================
# TOKEN HELPERS
# ==================================

def create_access_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "type": "access",
        "exp": datetime.utcnow()
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_refresh_token(user):
    payload = {
        "user_id": user.id,
        "type": "refresh",
        "exp": datetime.utcnow()
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token):
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token):
    payload = decode_token(token)

    if not payload:
        return None

    try:
        return User.objects.get(
            id=payload["user_id"]
        )

    except User.DoesNotExist:
        return None


# ==================================
# JWT AUTH
# ==================================

class JWTAuth(HttpBearer):

    def authenticate(self, request, token):

        payload = decode_token(token)

        if not payload:
            return None

        if payload.get("type") != "access":
            return None

        return get_user_from_token(token)


# ==================================
# REGISTER
# ==================================

@auth_router.post("/register")
def register(request, data: RegisterSchema):

    if User.objects.filter(
        username=data.username
    ).exists():

        return {
            "error": "Username already exists"
        }

    user = User.objects.create(
        username=data.username,
        password=make_password(data.password),
        role=data.role
    )

    return {
        "message": "User registered",
        "user_id": user.id
    }


# ==================================
# LOGIN
# ==================================

@auth_router.post("/login")
def login(request, data: LoginSchema):

    try:
        user = User.objects.get(
            username=data.username
        )

    except User.DoesNotExist:
        return {
            "error": "Invalid credentials"
        }

    if not check_password(
        data.password,
        user.password
    ):
        return {
            "error": "Invalid credentials"
        }

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ==================================
# REFRESH TOKEN
# ==================================

@auth_router.post("/refresh")
def refresh_token(request, data: RefreshSchema):

    payload = decode_token(
        data.refresh_token
    )

    if not payload:
        return {
            "error": "Invalid token"
        }

    if payload.get("type") != "refresh":
        return {
            "error": "Invalid refresh token"
        }

    try:
        user = User.objects.get(
            id=payload["user_id"]
        )

    except User.DoesNotExist:
        return {
            "error": "User not found"
        }

    access_token = create_access_token(user)

    return {
        "access_token": access_token
    }


# ==================================
# CURRENT USER
# ==================================

@auth_router.get(
    "/me",
    auth=JWTAuth()
)
def me(request):

    user = request.auth

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }


# ==================================
# UPDATE PROFILE
# ==================================

@auth_router.put(
    "/me",
    auth=JWTAuth()
)
def update_profile(
    request,
    data: UpdateProfileSchema
):

    user = request.auth

    if data.username:
        user.username = data.username

    if data.password:
        user.password = make_password(
            data.password
        )

    user.save()

    return {
        "message": "Profile updated"
    }

# ==================================
# ROLE DECORATORS
# ==================================

from functools import wraps


def require_role(roles):
    def decorator(func):

        @wraps(func)
        def wrapper(request, *args, **kwargs):

            user = getattr(request, "auth", None)

            if user is None:
                return 401, {
                    "error": "Unauthorized"
                }

            if user.role not in roles:
                return 403, {
                    "error": "Forbidden"
                }

            return func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorator


def is_admin(func):
    return require_role(
        ["admin"]
    )(func)


def is_instructor(func):
    return require_role(
        ["instructor"]
    )(func)


def is_student(func):
    return require_role(
        ["student"]
    )(func)