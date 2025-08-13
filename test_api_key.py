import requests

API_URL = "http://localhost:8000"
API_KEY = "Key_de_Seguridad_IoTproyect12345"
headers = {"Authorization": f"Bearer {API_KEY}"}

# ✅ Test GET /status con token
r = requests.get(f"{API_URL}/status", headers=headers)
print("GET /status =>", r.status_code, r.json())

# Test POST protegido (modo)
r2 = requests.post(
    f"{API_URL}/modo",
    headers=headers,
    json={"modo": 1}  # Usa JSON, no 'data'
)
print("POST /modo =>", r2.status_code, r2.json())


# 🚫 Test GET sin token (debería fallar con 403)
r3 = requests.get(f"{API_URL}/status")
print("GET /status sin token =>", r3.status_code, r3.text)
