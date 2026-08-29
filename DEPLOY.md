# Santexnika Backend — Production Deployment Yo'riqnomasi (Docker + Nginx + PostgreSQL / SQLite)

Ushbu hujjat **santexnika-backend** FastAPI loyihasini Docker, Gunicorn, Nginx va PostgreSQL (yoki SQLite) orqali Production serverida xavfsiz va samarali ishga tushirish bo'yicha to'liq yo'riqnomadir.

---

## 1. Loyiha strukturasi va tekshiruv xulosalari

1. **`main.txt` vs `app/main.py`**:
   - **`main.txt`**: Bu fayl Python kodi emas, balki loyiha endpoint'lari va superadmin mantiqi bo'yicha yozib ketilgan qisqa eslatma (text notes) matnidir.
   - **`app/main.py`**: FastAPI `app = FastAPI(...)` obyekti va barcha yo'nalishlar (routers: `auth`, `categories`, `products`, `orders`, `users`) aynan shu faylda yaratilgan va sozlangan.
2. **`requirements.txt`**:
   - Asl fayl **UTF-16LE** kodirovkasida bo'lganligi sababli to'g'rilanib, standart **UTF-8** ga o'tkazildi.
   - Production webservisi va ma'lumotlar bazasi bilan ishlash uchun `gunicorn==21.2.0` hamda `psycopg2-binary==2.9.9` kutubxonalari qo'shildi.
3. **Ma'lumotlar bazasi sozlamasi**:
   - `app/config.py` va `app/database.py` moslashtirildi: PostgreSQL va SQLite ma'lumotlar bazasi URL'larini avtomatik va xavfsiz qabul qiladi.

---

## 2. Yaratilgan Fayllar Izohi

### 📄 `Dockerfile`
- **Multi-Stage Build**: `builder` bosqichida `requirements.txt` orqali barcha kutubxonalar o'rnatiladi va `runner` bosqichiga minimal ko'rinishda o'tkaziladi. Bu image hajmini bir necha yuz megabaytga kichraytiradi.
- **Xavfsizlik (Non-root user)**: App root userda emas, balki `appuser` (privilegesiz foydalanuvchi) sifatida ishlaydi.
- **Gunicorn + Uvicorn Workers**: Process manager sifatida Gunicorn ishlatiladi va worker sifatida Uvicorn worker'lar biriktirilgan.
- **Healthcheck**: Konteyner holatini har 30 soniyada HTTP ping orqali tekshirib turadi.

### 📄 `.dockerignore`
- Konteyner ichiga ortiqcha va xavfli fayllar (`.git`, `.env`, local `*.db`, `venv`, `__pycache__`) kirib ketishining oldini oladi.

### 📄 `docker-compose.yml`
- **`backend`**: FastAPI ilovasi (Gunicorn orqali 8000 portda).
- **`db`**: PostgreSQL 16 Alpine konteyneri (Persist hajm va healthcheck bilan).
- **`nginx`**: Reverse Proxy sifatida 80 va 443 portlarni qabul qilib backend ga yo'naltiradi.
- **Volumes**:
  - `postgres_data`: PostgreSQL bazasi o'chib ketmasligi uchun.
  - `sqlite_data`: SQLite variantida DB faylini saqlab qolish uchun.
  - `static_data`: Yuklangan mahsulot rasmlari va statik fayllarni saqlash uchun.

### 📄 `nginx/nginx.conf` va `nginx/conf.d/default.conf`
- **Reverse Proxy**: Nginx 80-portga kelgan so'rovlarni `backend:8000` ga proxy qiladi.
- **Static Caching**: `/static/` yo'lidagi media fayllarni to'g'ridan-to'g'ri Nginx o'zi tezkor kesh bilan uzatadi.
- **`client_max_body_size 50M`**: Mahsulotlarning katta rasmlarini yuklashda "413 Request Entity Too Large" xatosi chiqmasligini ta'minlaydi.
- **Gzip Compression**: Javob matnlari hamda fayllarni siqib uzatish orqali tarmoq tezligini oshiradi.

### 📄 `.env.example` & `.env`
- Maxfiy kalitlar (`SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`) kodga hardcode qilinmasdan, muhit o'zgaruvchilaridan o'qilishi ta'minlandi.

---

## 3. Ma'lumotlar Bazasi Masalasi (SQLite vs PostgreSQL)

Production serverda ko'p foydalanuvchi bir vaqtning o'zida yozish (concurrent write) so'rovlarini yuborganda SQLite fayl bloklanishi (`database is locked`) xatosini berishi mumkin. Shu sababli ikkita variant taklif etiladi:

### 🔹 Variant A: PostgreSQL (Tavsiya etiladi)
`docker-compose.yml` da `db` xizmati yoqilgan. `.env` faylida quyidagi `DATABASE_URL` o'rnatiladi:
```env
DATABASE_URL=postgresql://santex_user:santex_secret_pass@db:5432/santexnika_db
POSTGRES_USER=santex_user
POSTGRES_PASSWORD=santex_secret_pass
POSTGRES_DB=santexnika_db
```

### 🔹 Variant B: SQLite (Named Volume orqali saqlab qolish)
Agar SQLite ishlatmoqchi bo'lsangiz, `.env` faylida `DATABASE_URL`ni quyidagiga o'zgartiring:
```env
DATABASE_URL=sqlite:////app/data/santexnika.db
```
Bu holatda Docker'ning `sqlite_data` named volume'i `/app/data/` papkasidagi `santexnika.db` faylini konteyner o'chib-yonishidan qat'i nazar saqlab qoladi.

---

## 4. Ishga Tushirish Yo'riqnomasi

### Step 1: `.env` faylini sozlash
Production serverda `.env` faylini yarating yoki tahrirlang:
```bash
cp .env.example .env
nano .env
```
`SECRET_KEY` uchun kuchli random matn generatsiya qiling:
```bash
openssl rand -hex 32
```

### Step 2: Docker Compose orqali konteynerlarni qurish va ishga tushirish
```bash
docker-compose up -d --build
```

### Step 3: Konteynerlar holatini tekshirish
```bash
docker-compose ps
```

### Step 4: Konteyner ichida Superadmin yaratish
`create_superadmin.py` skripti interaktiv bo'lgani uchun `-it` bayrog'i bilan ishga tushiriladi:
```bash
docker-compose exec -it backend python create_superadmin.py
```
Sizdan telefon raqam, username va parol kiritish so'raladi va superadmin baza ichida yaratiladi.

---

## 5. Loglarni ko'rish va Monitoring

- Backend loglarini jonli kuzatish:
  ```bash
  docker-compose logs -f backend
  ```
- Nginx loglarini kuzatish:
  ```bash
  docker-compose logs -f nginx
  ```
- PostgreSQL loglarini kuzatish:
  ```bash
  docker-compose logs -f db
  ```

---

## 6. Database Migration va Backup (Zaxiralash)

### PostgreSQL Backup yaratish:
```bash
docker-compose exec db pg_dump -U santex_user santexnika_db > backup_$(date +%F).sql
```

### PostgreSQL Backup tiklash:
```bash
cat backup_2026-08-29.sql | docker-compose exec -T db psql -U santex_user -d santexnika_db
```

---

## 7. SSL Sertifikat qo'shish (Let's Encrypt / Certbot)

Production serverda HTTPS domeningiz uchun bepul SSL sertifikat o'rnatish bosqichlari:

1. Serveringizga Certbot o'rnating:
   ```bash
   sudo apt update
   sudo apt install certbot python3-certbot-nginx -y
   ```
2. Sertifikat oling (Domen `yourdomain.com` server IP'siga yo'naltirilgan bo'lishi kerak):
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```
3. Certbot avtomatik ravishda Nginx konfiguratsiyasiga SSL sertifikat yo'llarini qo'shadi va HTTP -> HTTPS redirect sozlaydi.
