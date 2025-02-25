from machine import Pin, I2C
import dht
import ssd1306
import ujson
import network
import utime as time
import urequests as requests

# **Inisialisasi Sensor**
dht_sensor = dht.DHT11(Pin(4))
pir_sensor = Pin(13, Pin.IN)
buzzer = Pin(23, Pin.OUT)

# **Inisialisasi OLED SSD1306**
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# **Konfigurasi WiFi**
WIFI_SSID = "Mr.Predict"  # Ganti dengan SSID WiFi kamu
WIFI_PASSWORD = "ramayana"  # Ganti dengan password WiFi kamu

# **Konfigurasi API Server**
API_URL = "http://192.168.100.5:5000/sensor1"  # Ganti dengan IP lokal server Flask

# **Konfigurasi Ubidots**
UBIDOTS_TOKEN = "BBUS-VXkQvbCwxA5Op6MQSa3czDBkARhBeN"  # Ganti dengan token Ubidots kamu
UBIDOTS_DEVICE_LABEL = "esp32-sic6"  # Sesuaikan dengan device label di Ubidots
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/esp32-sic6/"

# **Fungsi Koneksi ke WiFi**
def connect_wifi():
    wifi_client = network.WLAN(network.STA_IF)
    wifi_client.active(True)
    wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

    max_retries = 20
    retries = 0
    while not wifi_client.isconnected() and retries < max_retries:
        print("⏳ Menghubungkan ke WiFi...")
        time.sleep(1)
        retries += 1

    if wifi_client.isconnected():
        print("✅ WiFi Tersambung! IP:", wifi_client.ifconfig()[0])
    else:
        print("❌ Gagal tersambung ke WiFi!")

# **Fungsi Kirim Data ke API Server Flask**
def send_data_api(temp, hum, gerakan):
    t = time.localtime()
    timestamp = "{:02d}-{:02d}-{:04d} {:02d}:{:02d}:{:02d}".format(
        t[2], t[1], t[0], t[3], t[4], t[5]
    )  # Format timestamp

    data = ujson.dumps({
        "temperature": temp,
        "humidity": hum,
        "gerakan": gerakan,
        "timestamp": timestamp
    })

    try:
        response = requests.post(API_URL, data=data, headers={"Content-Type": "application/json"})
        print("✅ Data Terkirim ke API Server!")
        print("📡 Response:", response.text)
        response.close()
    except Exception as e:
        print("❌ Gagal mengirim data ke API Server:", e)

# **Fungsi Kirim Data ke Ubidots**
def send_data_ubidots(temp, hum, gerakan):
    data = ujson.dumps({
        "temperature": { "value": temp },
        "humidity": { "value": hum },
        "motion": { "value": gerakan }
    })

    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(UBIDOTS_URL, data=data, headers=headers)
        print("✅ Data Terkirim ke Ubidots!")
        print("📡 Response:", response.text)
        response.close()
    except Exception as e:
        print("❌ Gagal mengirim data ke Ubidots:", e)

# **Mulai Koneksi WiFi**
connect_wifi()

# **Loop utama**
while True:
    try:
        # **Baca sensor DHT11**
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        gerakan = pir_sensor.value()

        print(f"🌡️ Suhu: {temp}°C | 💧 Kelembapan: {hum}% | 👀 Gerakan: {'Ya' if gerakan else 'Tidak'}")

        # **Update OLED Display**
        oled.fill(0)
        oled.text("Suhu: {} C".format(temp), 0, 10)
        oled.text("Kelembapan: {}%".format(hum), 0, 20)
        oled.text("Gerakan: {}".format("Ya" if gerakan else "Tidak"), 0, 30)
        oled.show()

        # **Aktifkan Buzzer Jika Suhu > 30°C**
        if temp > 30:
            buzzer.value(1)
            print("🚨 Peringatan! Suhu tinggi!")
        else:
            buzzer.value(0)

        # **Kirim Data ke API Server & Ubidots**
        send_data_api(temp, hum, gerakan)
        send_data_ubidots(temp, hum, gerakan)

    except Exception as e:
        print("❌ Error membaca sensor:", e)

    time.sleep(2)