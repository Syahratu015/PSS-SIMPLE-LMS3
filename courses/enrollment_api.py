from ninja import Router, Schema
from django.shortcuts import get_object_or_404

from .models import (
    Course,
    Enrollment,
    Lesson,
    Progress
)

from .auth import (
    JWTAuth,
    require_role
)

router = Router()


class EnrollmentSchema(Schema):
    course_id: int


@router.post("/", auth=JWTAuth())
@require_role(["student"])
def enroll_course(
    request,
    data: EnrollmentSchema
):
    course = get_object_or_404(
        Course,
        id=data.course_id
    )

    enrollment, created = (
        Enrollment.objects.get_or_create(
            student=request.auth,
            course=course
        )
    )

    if not created:
        return {
            "message": "Already enrolled"
        }

    return {
        "message": "Enrolled successfully"
    }


@router.get(
    "/my-courses",
    auth=JWTAuth()
)
@require_role(["student"])
def my_courses(request):

    enrollments = Enrollment.objects.filter(
        student=request.auth
    )

    return [
        {
            "course_id": e.course.id,
            "title": e.course.title
        }
        for e in enrollments
    ]


class ProgressSchema(Schema):
    lesson_id: int


@router.post(
    "/{enrollment_id}/progress",
    auth=JWTAuth()
)
@require_role(["student"])
def mark_complete(
    request,
    enrollment_id: int,
    data: ProgressSchema
):

    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        student=request.auth
    )

    lesson = get_object_or_404(
        Lesson,
        id=data.lesson_id
    )

    progress, _ = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    progress.is_completed = True
    progress.save()

    return {
        "message": "Lesson completed"
    }