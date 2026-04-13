# Rover BackEnd Development

## Description

Repository ini berisi implementasi sistem **backend** untuk proyek `Rover`, yang dimana sebuah aplikasi **deteksi objek berbasis Yolov11** yang digunakan untuk mendeteksi tingkat kematangan buah kelapa sawit

backend ini dibangun menggunakan **FastAPI** dan berperan sebagai pusat pengolaaan:

- Autentikasi dan manajemen pengguna
- Penyimpanan dan pengambilan data hasil deteksi
- Integrasi dengan model YOLOv11
- API komunikasi antara sistem deteksi dan aplikasi mobile

---

## ⚙️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL / SQLite (opsional untuk development)
- **ORM**: SQLAlchemy
- **Schema Validation**: Pydantic
- **Authentication**: JWT (JSON Web Token)
- **Environment Management**: Python venv
- **Server**: Uvicorn

## Project Structure

```bash
├── main.py # Entry point aplikasi FastAPI
├── src/
│ ├── users/ # Routing dan endpoint
│ ├── post/ # Model SQLAlchemy
│ ├── result/ # Pydantic schema
│ ├── yolo_detector/ # Business logic
│ └── core/ # Konfigurasi database
|
├── requirements.txt
└── .env.local
└── .env # digunakan untuk enviorment production
└── README.md
```

---

## Instalisasion

1. **Clone Repository**
    ```bash
    git clone https://github.com/username/Rover-Backend.git
    cd Rover-Backend
    ```
2. **Buat Virtual Enviroment**
    ```bash
    python -m venv env
    source env/bin/activate       # Mac / Linux
    env\Scripts\activate          # Windows
    ```
3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
4. **Setup environment variables**
    ```txt
    DATABASE_URL=postgresql://user:password@localhost:5432/rover_db
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    ```

## Run Server

Menjalankan server pengembangan:

```bash
uvicorn main:app --reload
```

lalu server akan berjalan di

```bash
http://127.0.0.1:8000
```

# Author

<h4 align="left">Iqbal Ramadhan</h4>
<p>🚀 Rover Project — <i>Deteksi Kematangan Buah Sawit Berbasis YOLOv11</i></p>
<p>📧 Email: <a href="mailto:iqbalramad75@gmail.com">iqbalramad75@gmail.com</a></p>
<p>💻 GitHub: <a href="https://github.com/kayabaakihiko13">Kayaba Akihiko13</a></p>
