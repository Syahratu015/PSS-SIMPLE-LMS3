import os
import time
import json
import redis

# Konfigurasi koneksi ke Redis di dalam Docker Compose Anda
# Menggunakan host 'redis' jika di dalam container, atau 'localhost' jika diuji langsung dari lokal
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
# Menggunakan port eksternal 6380 sesuai yang tertera di docker-compose.yml Anda ("6380:6379")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6380))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)

def get_weather(city):
    """Fungsi get_weather yang sudah dimodifikasi menggunakan Redis Caching"""
    cache_key = f"weather:{city.lower()}"

    # LENGKAPI TUGAS 1: Cek cache terlebih dahulu (GET)
    cached_data = redis_client.get(cache_key)

    # LENGKAPI TUGAS 2: Kalau ada di cache, langsung kembalikan datanya
    if cached_data:
        print("--- [CACHE HIT] Data diambil dari Redis cache ---")
        return json.loads(cached_data)

    # LENGKAPI TUGAS 3: Kalau tidak ada (Cache Miss), lakukan API call simulasi
    print("--- [CACHE MISS] Data belum ada di cache, memanggil API... ---")
    time.sleep(2)  # Simulasi slow API selama 2 detik
    
    # Ini adalah tiruan data JSON yang seharusnya dikembalikan oleh requests.get().json()
    response_data = {
        "city": city,
        "temperature": 30,
        "condition": "Sunny",
        "source": "Simulated API Response"
    }

    # LENGKAPI TUGAS 4: Simpan ke cache (SET) & Set expiry 5 menit / 300 detik (EXPIRE)
    redis_client.set(cache_key, json.dumps(response_data), ex=300)
    print("--- Data baru berhasil disimpan ke Redis cache ---")

    return response_data