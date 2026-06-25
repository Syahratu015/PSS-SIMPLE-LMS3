import time
# Mengimport fungsi get_weather yang sudah kita buat di atas
from weather_api import get_weather

print("=== MEMULAI PENGUJIAN REDIS CACHING ===\n")

# Panggilan Pertama - Harus lambat (sekitar 2 detik) karena mengambil dari API
start = time.time()
result1 = get_weather("Jakarta")
time1 = time.time() - start
print(f"Hasil 1: {result1}")
print(f"First call: {time1:.2f}s\n")

print("-" * 50 + "\n")

# Panggilan Kedua - Harus sangat cepat (< 0.1 detik) karena mengambil dari Redis Cache
start = time.time()
result2 = get_weather("Jakarta")
time2 = time.time() - start
print(f"Hasil 2: {result2}")
print(f"Second call (cached): {time2:.2f}s\n")

print("=== PENGUJIAN SELESAI ===")