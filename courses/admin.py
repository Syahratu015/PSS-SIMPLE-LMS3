from django.contrib import admin
from .models import User, Category, Course, Lesson, Enrollment, Progress

# Inline Lesson
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category')
    search_fields = ('title',)
    list_filter = ('category',)
    inlines = [LessonInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed')