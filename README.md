# Santexnika Backend API

Santexnika mahsulotlari do'koni uchun FastAPI + SQLModel + SQLite/PostgreSQL asosida qurilgan backend webservisi.

## Hususiyatlar
- FastAPI Web Framework
- SQLModel (SQLAlchemy + Pydantic)
- JWT Authentication & RBAC (Superadmin / Admin / User)
- Docker & Docker Compose bilan Production tayyorlik
- Nginx Reverse Proxy & Gzip compression
- Static Media upload va keshlash

## Ishga tushirish (Production Deployment)

Barcha batafsil ko'rsatmalar, Docker, PostgreSQL vs SQLite variantlari hamda SSL sertifikat sozlamalari [DEPLOY.md](./DEPLOY.md) faylida keltirilgan.

### Tezkor ishga tushirish:
```bash
# 1. Environment sozlash
cp .env.example .env

# 2. Docker containerlarni ishga tushirish
docker-compose up -d --build

# 3. Superadmin yaratish
docker-compose exec -it backend python create_superadmin.py
```
