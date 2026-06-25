from django.core.cache import cache


COURSE_LIST_CACHE_KEY = "course_list"


def clear_course_cache(course_id=None):
    cache.delete(COURSE_LIST_CACHE_KEY)

    if course_id:
        cache.delete(f"course_detail_{course_id}")