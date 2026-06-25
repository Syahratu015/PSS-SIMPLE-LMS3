from celery import shared_task
# SINKRONISASI: Mengambil fungsi utama dari file weather_api.py Anda
# (Pastikan file weather_api.py berada di dalam folder 'courses')
from .weather_api import fungsi_ambil_cuaca 


@shared_task
def send_enrollment_email(email, course_title):
    print(
        f"Email sent to {email} for course {course_title}"
    )
    return True


@shared_task
def generate_certificate(user_id, course_id):
    print(
        f"Generate certificate for user {user_id}"
    )
    return True


@shared_task
def update_course_statistics():
    print(
        "Updating course statistics..."
    )
    return True


@shared_task
def export_course_report(course_id):
    print(
        f"Exporting report for course {course_id}"
    )
    return True


# =========================================================================
# TUGAS TAMBAHAN: Mengambil & Mencatat Data Cuaca Otomatis via Celery Beat
# =========================================================================
@shared_task
def ambil_cuaca_otomatis():
    print("Celery Beat memicu penarikan data cuaca otomatis...")
    try:
        # Menjalankan fungsi utama dari skrip weather_api.py Anda
        hasil = fungsi_ambil_cuaca()
        print(f"Sukses mengambil data cuaca: {hasil}")
        return True
    except Exception as e:
        print(f"Gagal mengambil data cuaca. Error: {str(e)}")
        return False