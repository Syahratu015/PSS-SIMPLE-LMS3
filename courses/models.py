from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# =======================
# USER
# =======================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    def __str__(self):
        return self.username


# =======================
# CATEGORY
# =======================
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        return self.name


# =======================
# COURSE
# =======================
class CourseQuerySet(models.QuerySet):
    def for_listing(self):
        return self.select_related('instructor', 'category')


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    objects = CourseQuerySet.as_manager()

    def __str__(self):
        return self.title


# =======================
# LESSON
# =======================
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']


# =======================
# ENROLLMENT
# =======================
class EnrollmentQuerySet(models.QuerySet):
    def for_student_dashboard(self):
        return self.select_related('course').prefetch_related('progress_set')


class Enrollment(models.Model):
    student = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    objects = EnrollmentQuerySet.as_manager()

    class Meta:
        unique_together = ('student', 'course')


# =======================
# PROGRESS
# =======================
class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('enrollment', 'lesson')