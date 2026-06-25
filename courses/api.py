from ninja import Router, Schema
from typing import List
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from .mongo_utils import log_activity, log_learning_analytics
from django_ratelimit.decorators import ratelimit

from .models import Course
from .auth import JWTAuth, require_role


router = Router()


# ========================
# SCHEMAS
# ========================
class CourseOutSchema(Schema):
    id: int
    title: str
    description: str


class CourseCreateSchema(Schema):
    title: str
    description: str


class CourseUpdateSchema(Schema):
    title: str = None
    description: str = None


# ========================
# LIST (PUBLIC) + REDIS CACHE + SEARCH/FILTER/SORT
# ========================
@router.get("/")
@ratelimit(key="ip", rate="60/m", block=True)
def list_courses(
    request,
    search: str = None,
    category_id: int = None,
    sort: str = None
):
    courses = Course.objects.all()

    if search:
        courses = courses.filter(
            title__icontains=search
        )

    if category_id:
        courses = courses.filter(
            category_id=category_id
        )

    if sort == "title":
        courses = courses.order_by("title")

    elif sort == "-title":
        courses = courses.order_by("-title")

    elif sort == "newest":
        courses = courses.order_by("-id")

    result = list(
        courses.values(
            "id",
            "title",
            "description"
        )
    )

    return {
        "data": result
    }

# ========================
# DETAIL (PUBLIC) + REDIS CACHE
# ========================
@router.get("/{course_id}")
@ratelimit(key="ip", rate="60/m", block=True)
def get_course(request, course_id: int):
    cache_key = f"course_detail_{course_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return {
            "source": "redis_cache",
            "data": cached_data
        }

    course = Course.objects.filter(id=course_id).values(
        "id",
        "title",
        "description"
    ).first()

    if not course:
        return {"error": "Course not found"}

    cache.set(cache_key, course, timeout=300)

    return {
        "source": "database",
        "data": course
    }


# ========================
# CREATE (INSTRUCTOR ONLY) + CACHE INVALIDATION
# ========================
@router.post("/", auth=JWTAuth())
@require_role(["instructor"])
def create_course(request, data: CourseCreateSchema):
    user = request.auth

    course = Course.objects.create(
        title=data.title,
        description=data.description,
        instructor=user
    )

    log_activity(
        user_id=user.id,
        action="CREATE_COURSE",
        detail=f"Course '{course.title}' created"
    )

    log_learning_analytics(
        user_id=user.id,
        course_id=course.id,
        event_type="COURSE_CREATED",
        progress=0
    )

    cache.clear()

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description
    }


# ========================
# UPDATE (OWNER ONLY) + CACHE INVALIDATION
# ========================
@router.patch("/{course_id}", auth=JWTAuth())
@require_role(["instructor"])
def update_course(request, course_id: int, data: CourseUpdateSchema):
    user = request.auth
    course = get_object_or_404(Course, id=course_id)

    if course.instructor != user:
        return {"error": "Not your course"}

    if data.title is not None:
        course.title = data.title

    if data.description is not None:
        course.description = data.description

    course.save()

    log_activity(
        user_id=user.id,
        action="UPDATE_COURSE",
        detail=f"Course ID {course_id} updated"
    )

    cache.clear()
    cache.delete(f"course_detail_{course_id}")

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description
    }


# ========================
# DELETE (ADMIN ONLY) + CACHE INVALIDATION
# ========================
@router.delete("/{course_id}", auth=JWTAuth())
@require_role(["admin"])
def delete_course(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    log_activity(
        user_id=request.auth.id,
        action="DELETE_COURSE",
        detail=f"Course ID {course_id} deleted"
    )

    course.delete()

    cache.clear()
    cache.delete(f"course_detail_{course_id}")

    return {"message": "Deleted successfully"}